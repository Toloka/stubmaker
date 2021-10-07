"""Module for testing stub generation for module level attributes and annotations.
"""

__all__ = [
    'attribute_of_inner_type',
    'attribute_of_inner_type_with_value',
    'attribute_of_builtin_type',
    'attribute_of_builtin_type_with_value',
    'type_alias_attribute',
    'attribute_of_nested_type',
    'attribute_of_nested_type_with_value',
]
class InnerType:
    ...


attribute_of_inner_type_with_value: InnerType

attribute_of_builtin_type_with_value: str

class InnerType2:
    ...


type_alias_attribute = InnerType2

class ClassWithNestedType:
    class NestedType:
        ...


attribute_of_nested_type_with_value: ClassWithNestedType.NestedType

attribute_of_inner_type: InnerType

attribute_of_builtin_type: str

attribute_of_nested_type: ClassWithNestedType.NestedType
