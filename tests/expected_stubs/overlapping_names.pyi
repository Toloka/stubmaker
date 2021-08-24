"""Module for testing handling of overlapping names in stub generation.
"""

__all__ = [
    'Path',
    'B',
    'C',
    'A',
    'function_with_argument_of_nested_B_type',
    'function_with_argument_of_nested_C_type',
]
import pathlib


class Path(pathlib.Path):
    my_path_implementation_attr: int


class B:
    ...


class C:
    ...


class A:
    class B:
        ...

    class C:
        ...

    def f(self, A: B = ...): ...


def function_with_argument_of_nested_B_type(arg: A.B): ...


def function_with_argument_of_nested_C_type(arg: A.C): ...
