"""Module for testing of usage runtime values in stubs.
"""

__all__ = [
    'ImplicitSimpleClassChild',
    'attribute',
]
import test_package
import test_package.classes
import typing


class ImplicitSimpleClassChild(test_package.classes.SimpleClass):
    class_attribute: test_package.classes.SomeType


attribute: typing.Optional[test_package.InnerAnnotationType]
