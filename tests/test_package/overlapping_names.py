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


# parent class in stubs should be pathlib.Path but not Path
class Path(pathlib.Path):
    my_path_implementation_attr: int


class B:
    pass


class C:
    pass


class A:
    class B:
        pass

    class C:
        pass

    # f definition should be strictly lower than A.B definition
    def f(self, A: B = B()):
        pass


def function_with_argument_of_nested_B_type(arg: A.B):
    pass


def function_with_argument_of_nested_C_type(arg: A.C):
    pass


# should not generate anything in stubs
pathlib = pathlib
