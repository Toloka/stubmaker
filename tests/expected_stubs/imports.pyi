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
import contextvars
import pathlib
import test_package
import test_package.classes
import test_package.docstrings
import types

from pathlib import Path
from posixpath import (
    join,
    splitext,
)


def function_with_argument_of_type_from_renamed_import(arg: pathlib.Path): ...


class SomeChild(test_package.classes.InheritedClass):
    class_attribute: test_package.classes.SomeType


class UsedByUsedInAllClass(test_package.docstrings.SimpleClass):
    ...


class UsedInAllClass(UsedByUsedInAllClass):
    ...


attribute_of_type_with_redefined_module_1: types.ModuleType

attribute_of_type_with_redefined_module_2: test_package.ClassWithRedefinedModule

attribute_of_type_with_redefined_module_3: contextvars.ContextVar
