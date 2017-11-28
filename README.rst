.. |Pypi Version| image:: https://img.shields.io/pypi/v/sphinxcontrib-lilypond.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-lilypond
   :alt: sphinxcontrib-lilypond last version

.. |Pypi License| image:: https://img.shields.io/pypi/l/sphinxcontrib-lilypond.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-lilypond
   :alt: sphinxcontrib-lilypond license

.. |Pypi Python Version| image:: https://img.shields.io/pypi/pyversions/sphinxcontrib-lilypond.svg
   :target: https://pypi.python.org/pypi/sphinxcontrib-lilypond
   :alt: sphinxcontrib-lilypond python version

.. |Python| replace:: Python
.. _Python: http://python.org

.. |PyPI| replace:: PyPI
.. _PyPI: https://pypi.python.org/pypi

.. |Sphinx| replace:: Sphinx
.. _Sphinx: http://sphinx-doc.org

==============================
 Lilypond plugin for Sphinx
==============================

|Pypi License|
|Pypi Python Version|

|Pypi Version|

This plugin implements a ``lily`` role and directive to include Music score formatted by `Lilypond
<http://lilypond.org>`_.

Credits
-------

* `Fabrice Salvaire <http://fabrice-salvaire.fr>`_ 2017 (cleanup for Python 3)
* Wei-Wei Guo 2009, licensed under BSD https://bitbucket.org/birkenfeld/sphinx-contrib

Installation
------------

Using ``pip``:

.. code-block:: bash

    pip install sphinxcontrib-lilypond

Functionalities
---------------

- A ``lily`` role to include a standalone music markup.
  For example, a G clef can be inserted by::

     :lily:`\musicglyph #"clefs.G"`

  The purpose of the 'lily' role is writing music comments or learning notes.
  So only one markup is allowed.

- A ``lily`` directive to include a score, for example::

     .. lily::

        \relative c'' {
          c4 a d c
        }

Settings
--------

The ``lilypond_fontsize`` variable can be used to set the font size::

     lilypond_fontsize = ['6', '-3']

* The first value is for ``lily`` role setting in absolute font size.
* The second value is for ``lily`` directive setting in relative font size.
