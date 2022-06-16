"""Module for testing custom generics support"""
__all__ = [
    'T',
    'CustomGeneric',
    'annotated_method',
    'ClassInheritedFromCustomGeneric',
    'GenericInheritedFromCustomGeneric',
    'CustomMapping',
    'ForwardRefCustomGeneric',
    'FromNotInAllGeneric',
]

import typing

T = typing.TypeVar('T')


class CustomGeneric(typing.Generic[T]):
    pass


def annotated_method(field: typing.List[CustomGeneric[int]]) -> CustomGeneric[str]:
    pass


class ClassInheritedFromCustomGeneric(CustomGeneric[int]):
    pass


class GenericInheritedFromCustomGeneric(CustomGeneric[T]):
    pass


class CustomMapping(typing.Mapping[T, T]):
    pass


class ForwardRefCustomGeneric(CustomGeneric['ForwardRefCustomGeneric']):
    pass


class NotInAllGeneric(typing.Mapping[T, T]):
    pass


class FromNotInAllGeneric(NotInAllGeneric[T]):
    pass
