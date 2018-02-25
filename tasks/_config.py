"""
Config and definitions specific to PScript.
"""

import os.path as op

from . import ROOT_DIR, THIS_DIR  # noqa

NAME = 'pscript'
DOC_DIR = op.join(ROOT_DIR, 'docs')
DOC_BUILD_DIR = op.join(DOC_DIR, '_build')
