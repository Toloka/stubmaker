"""Module for testing class and metaclass specific stub generation.
"""

__all__ = [
    'SimpleClass',
    'InheritedClass',
    'MultipleInheritedClass',
]
class SomeType:
    ...


class SimpleClass:
    def __init__(
        self,
        arg_1,
        arg_2: int = 4
    ): ...

    class_attribute: SomeType


class InheritedClass(SimpleClass):
    @classmethod
    def classmethod_func(cls): ...

    @staticmethod
    def staticmethod_func(): ...

    @classmethod
    def classmethod_to_redefine(cls): ...

    @staticmethod
    def staticmethod_to_redefine(): ...

    class_attribute: SomeType


class MultipleInheritedClass(InheritedClass, SimpleClass):
    def new_method(self): ...

    @classmethod
    def classmethod_to_redefine(cls): ...

    @staticmethod
    def staticmethod_to_redefine(): ...

    class_attribute: SomeType
