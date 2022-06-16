"""Module for testing class and metaclass specific stub generation.
"""
__all__ = [
    'SimpleClass',
    'InheritedClass',
    'MultipleInheritedClass',
]


class SomeType:
    pass


class SimpleClass:

    def __init__(self, arg_1, arg_2: int = 4):
        self.arg_1 = arg_1
        self.arg_2 = arg_2

    # should appear in stub of this class and all children classes
    class_attribute: SomeType


class InheritedClass(SimpleClass):

    # dunder and private methods should not appear in stubs
    def __str__(self):
        pass

    def _private_method(self):
        pass

    def __dunder_private_method(self):
        pass

    # should appear only in stubs of InheritedClass
    # (but not in MultipleInheritedClass because it does not modify these methods)
    @classmethod
    def classmethod_func(cls):
        pass

    @staticmethod
    def staticmethod_func():
        pass

    # should appear both in a stub of this class and a stub of MultipleInheritedClass
    @classmethod
    def classmethod_to_redefine(cls):
        pass

    @staticmethod
    def staticmethod_to_redefine():
        pass


class MultipleInheritedClass(InheritedClass, SimpleClass):
    # all methods should appear in MultipleInheritedClass stub
    def new_method(self):
        pass

    @classmethod
    def classmethod_to_redefine(cls):
        return None

    @staticmethod
    def staticmethod_to_redefine():
        return None
