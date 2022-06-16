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
    'attribute_of_external_type'
]

from . import function_without_return_annotation


class InnerType:
    pass


attribute_of_inner_type: InnerType
attribute_of_inner_type_with_value: InnerType = InnerType()


attribute_of_builtin_type: str
attribute_of_builtin_type_with_value: str = '123'


class InnerType2:
    pass


type_alias_attribute = InnerType2


class InnerType3:
    pass


# everything below should not appear in stubs (not specified in __all__ and not used by anything specified in __all__)
hidden_attribute: InnerType3
hidden_attribute_with_value: InnerType3 = InnerType3()


hidden_attribute_with_shared_builtin_type: str
hidden_attribute_with_shared_type: InnerType
hidden_attribute_with_shared_builtin_type_with_value: str = ''
hidden_attribute_with_shared_type_with_value: InnerType = InnerType()


# should be rendered in stubs because NestedType is used
class ClassWithNestedType:
    class NestedType:
        pass


attribute_of_nested_type: ClassWithNestedType.NestedType
attribute_of_nested_type_with_value: ClassWithNestedType.NestedType = ClassWithNestedType.NestedType()


attribute_of_external_type: function_without_return_annotation()
