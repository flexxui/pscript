# -*- coding: utf-8 -*-

"""
PScript setup script.
"""

import os
import sys
import shutil

try:
    import setuptools  # noqa, analysis:ignore
except ImportError:
    pass  # setuptools allows for "develop", but it's not essential

from distutils.core import setup


## Function we need

def get_version_and_doc(filename):
    NS = dict(__version__='', __doc__='')
    docStatus = 0  # Not started, in progress, done
    for line in open(filename, 'rb').read().decode().splitlines():
        if line.startswith('__version__'):
            exec(line.strip(), NS, NS)
        elif line.startswith('"""'):
            if docStatus == 0:
                docStatus = 1
                line = line.lstrip('"')
            elif docStatus == 1:
                docStatus = 2
        if docStatus == 1:
            NS['__doc__'] += line.rstrip() + '\n'
    if not NS['__version__']:
        raise RuntimeError('Could not find __version__')
    return NS['__version__'], NS['__doc__']


def package_tree(pkgroot):
    subdirs = [os.path.relpath(i[0], THIS_DIR).replace(os.path.sep, '.')
               for i in os.walk(os.path.join(THIS_DIR, pkgroot))
               if '__init__.py' in i[2]]
    return subdirs


def copy_for_legacy_python(src_dir, dest_dir):
    from translate_to_legacy import LegacyPythonTranslator
    # Dirs and files to explicitly not translate
    skip = ['tests/python_sample.py',
            'tests/python_sample2.py',
            'tests/python_sample3.py']
    # Make a fresh copy of the package
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
    ignore = lambda src, names: [n for n in names if n == '__pycache__']
    shutil.copytree(src_dir, dest_dir, ignore=ignore)
    # Translate in-place
    LegacyPythonTranslator.translate_dir(dest_dir, skip=skip)


## Collect info for setup()

THIS_DIR = os.path.dirname(__file__)

# Define name and description
name = 'pscript'
description = "Python to JavaScript compiler."

# Get version and docstring (i.e. long description)
version, doc = get_version_and_doc(os.path.join(THIS_DIR, name, '__init__.py'))
doc = ""  # won't render open(os.path.join(THIS_DIR, 'README.md'), "rb").read().decode()

# Support for legacy Python: we install a second package with the
# translated code. We generate that code when we can. We use
# "name_legacy" below in "packages", "package_dir", and "package_data".
name_legacy = name + '_legacy'
if os.path.isfile(os.path.join(THIS_DIR, 'translate_to_legacy.py')):
    copy_for_legacy_python(os.path.join(THIS_DIR, name),
                           os.path.join(THIS_DIR, name_legacy))


## Setup

setup(
    name=name,
    version=version,
    author='Almar Klein and contributors',
    author_email='almar.klein@gmail.com',
    license='(new) BSD',
    url='http://pscript.readthedocs.io',
    download_url='https://pypi.python.org/pypi/pscript',
    keywords="Python, JavaScript, compiler, transpiler",
    description=description,
    long_description=doc,
    long_description_content_type="text/markdown",
    platforms='any',
    provides=[name],
    install_requires=[],
    packages=package_tree(name) + package_tree(name_legacy),
    package_dir={name: name, name_legacy: name_legacy},
    # entry_points={'console_scripts': ['pscript = pscript.__main__:main'], },
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
