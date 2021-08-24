"""Module for testing imports handling in stub generation.
"""

__all__ = [
    'function_with_argument_of_type_from_renamed_import',
    'SomeChild',
    'UsedInAllClass',
    'Path',
]
import pathlib
import test_package.classes

from pathlib import Path

def function_with_argument_of_type_from_renamed_import(arg: pathlib.Path): ...


class SomeChild(test_package.classes.InheritedClass):
    class_attribute: test_package.classes.SomeType


class UsedByUsedInAllClass:
    ...


class UsedInAllClass(UsedByUsedInAllClass):
    ...
