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
    @staticmethod
    def __new__(
        mcs,
        *args,
        **kwargs
    ): ...

    def __lt__(cls, other): ...

    def gt(cls, other): ...

    def __gt__(cls, other): ...


class ClassWithSimpleMetaclass(metaclass=SimpleMetaclass):
    """This class has metaclass
    """


class InheritedClassFromClassWithMetaclass(ClassWithSimpleMetaclass):
    """Base of this class had metaclass
    """


class CustomMetaclass(type):
    @staticmethod
    def __new__(
        mcs,
        *args,
        **kwargs
    ): ...


class ClassWithCustomMetaclass(metaclass=CustomMetaclass):
    generated_member: str
