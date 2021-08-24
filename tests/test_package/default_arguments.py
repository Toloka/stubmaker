"""Module for testing stub generation for complex function signatures.
"""
__all__ = [
    'func'
]

import typing
import pathlib
from functools import partial
from test_package.overlapping_names import Path


class SomeClass:
    pass


def func(
    # arg_1 and arg_2 should have different types in stubs
    arg_1: pathlib.Path,
    arg_2: Path,
    arg_3: int = 42,
    arg_4: SomeClass = SomeClass(), # default value may not appear in stubs
    arg_5: str = 'some_str',
    arg_6: typing.List = [],
    arg_7: typing.List = [123, partial, 'a'],
) -> str:
    pass
