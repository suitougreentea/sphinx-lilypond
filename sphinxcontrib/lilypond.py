"""
    Sphinx Extension lilypond
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Allow Lilypond music notes to be included in Sphinx-generated documents
    inline and outline.

    :copyright: Copyright © 2017 by Fabrice Salvaire.
    :copyright: Copyright © 2009 by Wei-Wei Guo.
    :license: BSD, see LICENSE for details.

    The extension is modified from mathbase.py and pngmath.py by Sphinx team.

    Further modified by @suitougreentea
    Change output format to SVG, Remove LaTeX support, Remove inline support,
    Add container and caption, and more.
    pdf2svg must be installed.
"""

####################################################################################################

from hashlib import sha1 as sha
from subprocess import Popen, PIPE
import logging
import os
import shutil
import tempfile

from docutils import nodes, utils
from docutils.parsers.rst import directives

from sphinx.errors import SphinxError
from sphinx.util import ensuredir
from sphinx.util.compat import Directive

from sphinx.util import parselinenos
from sphinx.util.nodes import set_source_info

####################################################################################################

_logger = logging.getLogger(__name__)

####################################################################################################

DOCUMENT_BEGIN = r'''
\paper{
  indent=0\mm
  line-width=160\mm
  oddFooterMarkup=##f
  oddHeaderMarkup=##f
  bookTitleMarkup=##f
  scoreTitleMarkup=##f
}
'''

DIRECTIVE_BEGIN = r'''
'''

DIRECTIVE_END = r'''
'''

####################################################################################################

class LilyExtError(SphinxError):
    category = 'Lilypond extension error'

####################################################################################################

class lily(nodes.Inline, nodes.TextElement):
    pass

####################################################################################################

class displaylily(nodes.Part, nodes.Element):
    pass

####################################################################################################

class LilyDirective(Directive):

    """ This class defines a ``lily`` directive.

    .. code-block:: ReST

        .. lily::
            :nowrap:

            \relative c'' {
                c4 a d c
            }

    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'nowrap': directives.flag,
        'linenos': directives.flag,
        'lineno-start': int,
        'emphasize-lines': directives.unchanged_required,
        'caption': directives.unchanged_required,
        'name': directives.unchanged,
        'without-code': directives.flag,
        'without-image': directives.flag,
    }

    ##############################################

    def run(self):
        without_code = 'without-code' in self.options
        without_image = 'without-image' in self.options

        if not without_image:
            ## Generate LilyPond image node
            lily_source = '\n'.join(self.content)
            lilyimage = lily()
            lilyimage['lily_source'] = lily_source
            lilyimage['docname'] = self.state.document.settings.env.docname
            lilyimage['nowrap'] = 'nowrap' in self.options

        if not without_code:
            ## Generate source code node (from sphinx.directives.code)
            # type: () -> List[nodes.Node]
            document = self.state.document
            code = u'\n'.join(self.content)
            location = self.state_machine.get_source_and_line(self.lineno)

            linespec = self.options.get('emphasize-lines')
            if linespec:
                try:
                    nlines = len(self.content)
                    hl_lines = parselinenos(linespec, nlines)
                    if any(i >= nlines for i in hl_lines):
                        logger.warning('line number spec is out of range(1-%d): %r' %
                                       (nlines, self.options['emphasize-lines']),
                                       location=location)

                    hl_lines = [x + 1 for x in hl_lines if x < nlines]
                except ValueError as err:
                    return [document.reporter.warning(str(err), line=self.lineno)]
            else:
                hl_lines = None

            literal = nodes.literal_block(code, code)
            literal['language'] = 'lilypond'
            literal['linenos'] = 'linenos' in self.options or \
                                 'lineno-start' in self.options
            extra_args = literal['highlight_args'] = {}
            if hl_lines is not None:
                extra_args['hl_lines'] = hl_lines
            if 'lineno-start' in self.options:
                extra_args['linenostart'] = self.options['lineno-start']
            set_source_info(self, literal)

        ## Generate caption and container node
        caption = self.options.get('caption')
        if caption:
            caption_str = 'LilyPond: %s' % caption
        else:
            caption_str = 'LilyPond'
        caption_node = nodes.caption('', '', *[nodes.Text(caption_str)])

        container_node = nodes.container('', literal_block=True, classes=['lily-block-wrapper'])
        container_node += caption_node
        if not without_code: container_node += literal
        if not without_image: container_node += lilyimage

        self.add_name(container_node)

        return [container_node]

####################################################################################################

def render_lily(self, lily_source):

    """Render the Lilypond music expression *lily* using lilypond.

    """

    if hasattr(self.builder, '_lilypond_warned'):
        return None, None

    # self.builder.warn('Render lilipond')
    # _logger.info('Render lilypond\n' + lily_source)
    print('Render lilypond\n' + lily_source)

    basename = "{}.svg".format(sha(lily_source.encode('utf-8')).hexdigest())
    relative_filename = os.path.join(self.builder.imgpath, 'lily', basename)
    absolut_filename = os.path.join(self.builder.outdir, '_images', 'lily', basename)

    if os.path.isfile(absolut_filename):
        return relative_filename

    lily_source = '\\version "' + self.builder.config.lilypond_version + '"\n' + DOCUMENT_BEGIN + self.builder.config.lilypond_preamble + lily_source

    # use only one tempdir per build -- the use of a directory is cleaner
    # than using temporary files, since we can clean up everything at once
    # just removing the whole directory (see cleanup_lily_tempdir)
    if not hasattr(self.builder, '_lilypond_tempdir'):
        tempdir = self.builder._lilypond_tempdir = tempfile.mkdtemp()
    else:
        tempdir = self.builder._lilypond_tempdir

    lilypond_input_file = os.path.join(tempdir, 'music.ly')
    with open(lilypond_input_file, 'w') as fh:
        fh.write(lily_source)

    ensuredir(os.path.dirname(absolut_filename))

    # use some standard lilypond arguments
    lilypond_args = [self.builder.config.lilypond_command]
    # Cropped SVG
    # http://lilypond.1069038.n5.nabble.com/Cropped-SVG-Output-td182397.html
    # https://github.com/Abjad/abjad/issues/606 Option to ask lilypond to render to SVG and use ipython.display.SVG to show it #606
    # inkscape -S lylipond-test.svg
    #   svg78,170.07411,25.448056,223.11942,34.394129 # X Y W H
    lilypond_args += [
        '-o', tempdir,
        '-dbackend=eps',
        '-dno-gs-load-fonts',
        '-dinclude-eps-fonts',
    ]
    # add custom ones from config value
    lilypond_args.extend(self.builder.config.lilypond_args)

    # last, the input file name
    lilypond_args.append(lilypond_input_file)

    try:
        process_lily = Popen(lilypond_args, stdout=PIPE, stderr=PIPE)
    except OSError as exception:
        if exception.errno != 2:   # No such file or directory
            raise
        template = 'lilypond command {} cannot be run (needed for music display), check the lilypond_command setting'
        self.builder.warn(template.format(self.builder.config.lilypond_command))
        self.builder._lilypond_warned = True
        return None, None
    stdout, stderr = process_lily.communicate()
    if process_lily.returncode != 0:
        template = 'lilypond exited with error:\n[stderr]\n{}\n[stdout]\n{}'
        raise LilyExtError(template.format(stderr.decode('utf-8'), stdout.decode('utf-8')))

    try:
        process_pdf2svg = Popen(['pdf2svg', os.path.join(tempdir, 'music.pdf'), os.path.join(tempdir, 'music.svg')], stdout=PIPE, stderr=PIPE)
    except OSError as exception:
        if exception.errno != 2:   # No such file or directory
            raise
        self.builder.warn('pdf2svg command cannot be run')
        self.builder._lilypond_warned = True
        return None, None

    stdout, stderr = process_pdf2svg.communicate()
    if process_pdf2svg.returncode != 0:
        template = 'pdf2svg exited with error:\n[stderr]\n{}\n[stdout]\n{}'
        raise LilyExtError(template.format(stderr.decode('utf-8'), stdout.decode('utf-8')))

    shutil.copyfile(os.path.join(tempdir, 'music.svg'), absolut_filename)

    # Popen(['mogrify', '-trim', absolut_filename], stdout=PIPE, stderr=PIPE)

    return relative_filename

####################################################################################################

def cleanup_lily_tempdir(app, exception):

    if exception:
        return
    if not hasattr(app.builder, '_lilypond_tempdir'):
        return

    try:
        shutil.rmtree(app.builder._lilypond_tempdir)
    except Exception:
        pass

####################################################################################################

def html_visit_lily(self, node):

    if node['nowrap']:
        lily_source = node['lily_source']
    else:
        lily_source = DIRECTIVE_BEGIN + node['lily_source'] + DIRECTIVE_END

    try:
        filename = render_lily(self, lily_source)
    except LilyExtError as exception:
        sytem_message = nodes.system_message(
            str(exception), type='WARNING', level=2,
            backrefs=[], source=node['lily_source'])
        sytem_message.walkabout(self)
        self.builder.warn('display lilypond {}: {}'.format(node['lily_source'], exception))
        raise nodes.SkipNode

    lily_source = self.encode(node['lily_source']).strip()
    if filename is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="lily">{}</span>'.format(lily_source))
    else:
        template = '<img class="lily" src="{}" alt="{}" align="absbottom"/>'
        self.body.append(template.format(filename, lily_source))

    raise nodes.SkipNode

####################################################################################################

def setup(app):

    app.add_node(lily, html=(html_visit_lily, None))
    app.add_directive('lily', LilyDirective)

    app.add_config_value('lilypond_version', '2.19.59', False)
    app.add_config_value('lilypond_preamble', '', False)
    app.add_config_value('lilypond_fontsize', [10, -3], False)
    app.add_config_value('lilypond_command', 'lilypond', False)
    app.add_config_value('lilypond_args', [], False)

    app.connect('build-finished', cleanup_lily_tempdir)
