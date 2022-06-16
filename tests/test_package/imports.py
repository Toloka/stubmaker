"""Module for testing imports handling in stub generation.
"""
__all__ = [
    'function_with_argument_of_type_from_renamed_import',
    'SomeChild',
    'UsedInAllClass',
    'Path',
    'join',
    'splitext',
]
# Many imports below are useless for stubs. Stub generation should provide only necessary imports for the stub file.
import os
import typing

from pathlib import Path
from functools import *

from .classes import SimpleClass, InheritedClass
from . import docstrings
from .docstrings import module_function
from .enums import *
# check "from ... import (...)" form of import in stubs
from os.path import join, splitext

import pathlib as renamed_pathlib


def function_with_argument_of_type_from_renamed_import(arg: renamed_pathlib.Path):
    pass


# useless for stubs usage of imported class
SimpleClass(None)


# useful for stubs usage of imported class
class SomeChild(InheritedClass):
    pass


class NotUsedInAllClass:
    pass


# should appear in stubs. also should cause docstrings module import
class UsedByUsedInAllClass(docstrings.SimpleClass):
    pass


class UsedInAllClass(UsedByUsedInAllClass):
    pass
