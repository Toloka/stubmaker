"""Some definitions, mainly used by submodules. Also used for testing nested submodule importing stub generation.
"""
__all__ = [
    'function_without_return_annotation',
    'get_implicit_annotation',
    'SimpleClass',
    'SubpackageClass',
    'module',
    'classes',
    'external_typevar'
]
import typing

# should appear in stubs in from ... import ... form because specified in __all__
from .test_subpackage import module
from .test_subpackage import SubpackageClass
from .classes import SimpleClass


def function_without_return_annotation():
    return SimpleClass


# Not specified in __all__ and signatures of current module so should not appear in __init__.pyi
class InnerAnnotationType:
    pass


def get_implicit_annotation():
    return typing.Optional[InnerAnnotationType]


external_typevar = typing.TypeVar('external_typevar')
