"""Module for testing of usage runtime values in stubs.
"""
__all__ = [
    'ImplicitSimpleClassChild',
    'attribute',
]
from . import function_without_return_annotation, get_implicit_annotation


# should be inherited from SimpleClass in stubs (SimpleClass also should be correctly imported)
class ImplicitSimpleClassChild(function_without_return_annotation()):
    pass


# should have typing.Optional[test_package.InnerAnnotationType] annotation
attribute: get_implicit_annotation()
