"""Module for testing stub generation for module level attributes and annotations.
"""

__all__ = [
    'attribute_of_inner_type',
    'attribute_of_inner_type_with_value',
    'attribute_of_builtin_type',
    'attribute_of_builtin_type_with_value',
    'type_alias_attribute',
]
class InnerType:
    ...


attribute_of_inner_type_with_value: InnerType

attribute_of_builtin_type_with_value: str

class InnerType2:
    ...


type_alias_attribute = InnerType2

attribute_of_inner_type: InnerType

attribute_of_builtin_type: str
