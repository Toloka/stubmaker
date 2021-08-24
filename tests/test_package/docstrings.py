"""Module for testing docstring generation in stubs (including this docstring).
"""

__all__ = [
    'SimpleClass',
    'module_function',
    'generator_function',
]


class SimpleClass:
    """Short description

    Long description

    Args:
        arg_1: arg_1 description
        arg_2: arg_2 description

    Attributes:
        attr_1: attribute_1 description
        attr_2: attribute_2 description
    """

    def __init__(self, arg_1, arg_2):
        """Init short description

        Init long description

        Args:
            arg_1: arg_1 init description
            arg_2: arg_2 init description
        """
        pass

    def method(self, arg):
        """Method short description

        Method long description

        Args:
            arg: arg method description

        Returns:
            int: returns zero

        Raises:
            ValueError: some error

        Examples:
            >>> module_function(1)
            some example description
        """
        if arg == 0:
            raise ValueError
        return 0


def module_function(arg):
    """Module function short description

    Module function long description

    Args:
        arg: arg module function description

    Returns:
        int: returns zero

    Raises:
        ValueError: some error

    Example:
        >>> module_function(1)
        some example description
    """
    if arg == 0:
        raise ValueError
    return 0


def generator_function(arg):
    """Generator function short description

    Generator function long description

    Args:
        arg: arg generator function description

    Yields:
        int: yield value description
    """
    yield 1
