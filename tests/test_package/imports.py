"""Module for testing imports handling in stub generation.
"""
__all__ = [
    'function_with_argument_of_type_from_renamed_import',
    'SomeChild',
    'UsedInAllClass',
    'Path',
    'join',
    'splitext',
    'attribute_of_type_with_redefined_module_1',
    'attribute_of_type_with_redefined_module_2',
    'attribute_of_type_with_redefined_module_3',
]
# Many imports below are useless for stubs. Stub generation should provide only necessary imports for the stub file.
import os
import typing
from contextvars import ContextVar

from pathlib import Path
from functools import *
from types import ModuleType

from .classes import SimpleClass, InheritedClass
from . import docstrings, ClassWithRedefinedModule
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
class Base1(docstrings.SimpleClass):
    pass


class Base2(Base1):
    pass


class Base3(Base2):
    pass


class UsedInAllClass(Base3):
    pass


attribute_of_type_with_redefined_module_1: ModuleType
attribute_of_type_with_redefined_module_2: ClassWithRedefinedModule
attribute_of_type_with_redefined_module_3: ContextVar
