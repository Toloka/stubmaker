"""Some definitions, mainly used by submodules. Also used for testing nested submodule importing stub generation.
"""

__all__ = [
    'function_without_return_annotation',
    'get_implicit_annotation',
    'SimpleClass',
    'SubpackageClass',
    'module',
    'classes',
    'external_typevar',
]
import typing

from test_package import classes
from test_package.classes import SimpleClass
from test_package.test_subpackage import module
from test_package.test_subpackage.module import SubpackageClass

def function_without_return_annotation(): ...


def get_implicit_annotation(): ...


external_typevar = typing.TypeVar('external_typevar')
