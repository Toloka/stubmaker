"""Module for testing handling of usual types and typing types in stub generation.
"""

__all__ = [
    'CustomType',
    'ClassWithComplexAttributes',
    'annotated_func',
    'annotated_func_2',
]
import pathlib
import typing


class CustomType:
    forward_reference_attr: typing.Optional[CustomType]
    attribute_2: int


class ClassWithComplexAttributes:
    union: typing.Union[int, str]
    optional: typing.Optional[int]
    union_as_optional_1: typing.Optional[str]
    union_as_optional_2: typing.Optional[str]
    complex_nested_type_attribute: typing.List[typing.Dict[str, typing.Union[str, CustomType, None]]]
    callable_1: typing.Callable[[], None]
    callable_2: typing.Callable[[int, str], CustomType]
    callable_3: typing.Callable[..., None]
    callable_4: typing.Callable[[pathlib.Path], None]


def annotated_func(attr_1: int, attr_2: CustomType) -> int: ...


def annotated_func_2() -> None: ...
