"""Module for testing metaclass specific stub generation.
"""
__all__ = [
    'SimpleMetaclass',
    'ClassWithSimpleMetaclass',
    'InheritedClassFromClassWithMetaclass',
    'CustomMetaclass',
    'ClassWithCustomMetaclass',
]


class SimpleMetaclass(type):
    def __new__(mcs, *args, **kwargs):
        return super().__new__(mcs, *args, **kwargs)

    def __lt__(cls, other):
        pass

    def gt(cls, other):
        pass

    __gt__ = gt


class ClassWithSimpleMetaclass(metaclass=SimpleMetaclass):
    """
    This class has metaclass
    """
    pass


class InheritedClassFromClassWithMetaclass(ClassWithSimpleMetaclass):
    """
    Base of this class had metaclass
    """
    pass


# Metaclass adds new attribute with annotation that should appear in stubs
class CustomMetaclass(type):
    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        cls.generated_member = 'some value'
        annotations = getattr(cls.__dict__, '__annotations__', {})
        annotations['generated_member'] = str
        cls.__annotations__ = annotations
        return cls


class ClassWithCustomMetaclass(metaclass=CustomMetaclass):
    pass
