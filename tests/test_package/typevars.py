"""Module for testing TypeVars support
"""
__all__ = [
    'GenericClassAlias',
    'GenericClassWithTypeVarOverlap',
    'T',
    'external_typevar'
]
import typing

# should appear in stubs both in test_package.external_typevar form and "from test_package import external_typevar" form
from . import external_typevar


T = typing.TypeVar('T')
T_bounded = typing.TypeVar('T_bounded', bound=int)
T_covariant = typing.TypeVar('T_covariant', covariant=True)
T_contravariant = typing.TypeVar('T_contravariant', contravariant=True)


class GenericClass:
    def __init__(
        self,
        arg_1: T, arg_2: T_bounded, arg_3: T_covariant,
        arg_4: T_contravariant, arg_5: external_typevar
    ):
        pass


GenericClassAlias = GenericClass


class GenericClassWithTypeVarOverlap:
    T = typing.TypeVar('T')

    # arg_1 should have "T" annotation stubs (but not GenericClassWithTypeVarOverlap.T)
    def some_func(self, arg_1: T):
        pass
