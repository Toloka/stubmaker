"""Module for testing stub generation for enums and enum subclasses.
"""
__all__ = [
    'EnumClass',
    'UniqueEnum',
    'FunctionalEnum',
    'EnumSubclassClass',
    'AutoEnum',
    'function_with_enum_value_annotation',
]
from enum import Enum, unique, EnumMeta, auto, IntEnum
from time import sleep


class EnumClass(Enum):
    A = 1
    B = 2
    C = 'a'


@unique
class UniqueEnum(Enum):
    A = 1
    B = 2


# should appear in stubs as class definition
FunctionalEnum = Enum('FunctionalEnum', 'FIELD_1 FIELD_2')


# adds new value to enum (hacky because in reality it is much more complex)
class EnumMetaclass(EnumMeta):
    def __new__(mcs, name, bases, namespace):
        if 'VALUE_1' in namespace:
            namespace['MCS_VALUE'] = 4
        cls = super().__new__(mcs, name, bases, namespace)
        return cls


# should contain MCS_VALUE
class EnumSubclass(Enum, metaclass=EnumMetaclass):
    pass


class SomeMixin:
    pass


# should contain MCS_VALUE
class EnumSubclassClass(SomeMixin, EnumSubclass):
    VALUE_1 = 1
    VALUE_2 = 'a'


class AutoEnum(Enum):
    VALUE_1 = auto()
    VALUE_2 = auto()


class IntEnumClass(IntEnum):
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3 * 3


# default argument value should appear as IntEnumClass.VALUE_3 in stubs
def function_with_enum_value_annotation(unit: IntEnumClass = IntEnumClass.VALUE_3):
    pass
