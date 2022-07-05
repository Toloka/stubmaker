"""Module for testing custom generics support
"""

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
import abc
import typing


T = typing.TypeVar('T')

class CustomGeneric(typing.Generic[T]):
    ...


def annotated_method(field: typing.List[CustomGeneric[int]]) -> CustomGeneric[str]: ...


class ClassInheritedFromCustomGeneric(CustomGeneric[int]):
    ...


class GenericInheritedFromCustomGeneric(CustomGeneric[T]):
    ...


class CustomMapping(typing.Mapping[T, T], metaclass=abc.ABCMeta):
    ...


class ForwardRefCustomGeneric(CustomGeneric['ForwardRefCustomGeneric']):
    ...


class NotInAllGeneric(typing.Mapping[T, T], metaclass=abc.ABCMeta):
    ...


class FromNotInAllGeneric(NotInAllGeneric[T], metaclass=abc.ABCMeta):
    ...
