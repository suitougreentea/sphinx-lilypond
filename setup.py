from setuptools import setup, find_packages

setup(
    name='sphinxcontrib-lilypond',
    version='1.1.0',
    url='https://github.com/FabriceSalvaire/sphinx-lilypond',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-lilypond',
    author='Fabrice Salvaire', # Wei-Wei Guo
    author_email='fabrice.salvaire@orange.fr', # wwguocn@gmail.com
    description='Sphinx lilypond extension',
    long_description=open('README.rst').read(),
    license='BSD',
    # license='GPLv3',
    keywords='sphinx extension literalinclude',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        # 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        # 'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Sphinx>=0.6'
    ],
    namespace_packages=[
        'sphinxcontrib',
    ],
)
