"""Module for testing stub generation for enums and enum subclasses.
"""

__all__ = [
    'EnumClass',
    'UniqueEnum',
    'FunctionalEnum',
    'EnumSubclassClass',
    'AutoEnum',
    'function_with_enum_value_annotation',
    'ClassWithNestedEnum',
]
import enum


class EnumClass(enum.Enum):
    """An enumeration.
    """

    A = 1
    B = 2
    C = 'a'


class UniqueEnum(enum.Enum):
    """An enumeration.
    """

    A = 1
    B = 2


class FunctionalEnum(enum.Enum):
    """An enumeration.
    """

    FIELD_1 = 1
    FIELD_2 = 2


class EnumSubclass(enum.Enum):
    """An enumeration.
    """

    ...


class SomeMixin:
    ...


class EnumSubclassClass(SomeMixin, EnumSubclass):
    """An enumeration.
    """

    VALUE_1 = 1
    VALUE_2 = 'a'
    MCS_VALUE = 4


class AutoEnum(enum.Enum):
    """An enumeration.
    """

    VALUE_1 = 1
    VALUE_2 = 2


class IntEnumClass(enum.IntEnum):
    """An enumeration.
    """

    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 9


def function_with_enum_value_annotation(unit: IntEnumClass = IntEnumClass.VALUE_3): ...


class ClassWithNestedEnum:
    class NestedEnum(enum.Enum):
        """An enumeration.
        """

        VALUE = 1

    def __init__(self, enum_value=NestedEnum.VALUE): ...
