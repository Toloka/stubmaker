"""Module for testing stub generation for complex function signatures.
"""

__all__ = [
    'func',
]
import pathlib
import test_package.overlapping_names
import typing


class SomeClass:
    ...


def func(
    arg_1: pathlib.Path,
    arg_2: test_package.overlapping_names.Path,
    arg_3: int = 42,
    arg_4: SomeClass = ...,
    arg_5: str = 'some_str',
    arg_6: typing.List = [],
    arg_7: typing.List = ...
) -> str: ...
