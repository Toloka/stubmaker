"""Module for testing handling of usual types and typing types in stub generation.
"""
__all__ = [
    'CustomType',
    'ClassWithComplexAttributes',
    'annotated_func',
    'annotated_func_2',
]

import typing
import pathlib

class CustomType:
    forward_reference_attr: typing.Optional['CustomType']
    attribute_2: int


class ClassWithComplexAttributes:
    # should be collapsed to Union[int, str]
    union: typing.Union[int, typing.Union[int, str]]
    optional: typing.Optional[int]
    # typing.Union[None, str] and typing.Union[str, None] should be converted to Optional
    union_as_optional_1: typing.Union[None, str]
    union_as_optional_2: typing.Union[str, None]
    complex_nested_type_attribute: typing.List[typing.Dict[str, typing.Optional[typing.Union[str, CustomType]]]]
    callable_1: typing.Callable[[], None]
    callable_2: typing.Callable[[int, str], CustomType]
    callable_3: typing.Callable[..., None]
    callable_4: typing.Callable[[pathlib.Path], None]


def annotated_func(attr_1: int, attr_2: CustomType) -> int:
    pass


def annotated_func_2() -> None:
    pass
