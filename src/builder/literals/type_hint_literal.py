import typing
from stubmaker.builder.common import BaseLiteral, BaseASTBuilder, Node
from typing import Union, Optional, Callable


class TypeHintLiteral(BaseLiteral):
    """Represents a type hint"""

    def __init__(self, node: Node, ast: BaseASTBuilder):
        super().__init__(node, ast)

        # Python < 3.9 support for generic types without arguments
        is_special = getattr(self.obj, '_special', False)

        # typing.get_args works with Callable[[], int] but does not work with
        # Callable in Python 3.8. So __args__ seems more reliable
        if not is_special:
            args = getattr(self.obj, '__args__', ())
        else:
            args = ()

        # get origin of generic type
        if self.obj._name:
            # If has _name ignore __origin__ field and get origin directly from types module. This is necessary for
            # typing aliases (e.g. __origin__ of List[int] is list instead of typing.List).
            origin = getattr(typing, self.obj._name)
        else:
            # Fallback to using __origin__. For non-generic types (e.g. List without arguments) retrieve object itself.
            origin = getattr(self.obj, '__origin__', self.obj)

        if origin is Callable and len(args) > 0 and args[0] is not Ellipsis:
            args = ([self.ast.get_literal(Node(self.namespace, None, arg)) for arg in args[:-1]], args[-1])
        elif origin is Union and type(None) in args and len(args) == 2:  # noqa: E721
            origin = Optional
            args = [arg for arg in args if arg is not type(None)]  # noqa: E721

        args = [None if arg is type(None) else arg for arg in args]  # noqa: E721
        self.type_hint_origin = self.ast.get_literal_for_reference(Node(self.namespace, None, origin))
        self.type_hint_args = [self.ast.get_literal(Node(self.namespace, None, arg)) for arg in args]

    def __iter__(self):
        yield self.type_hint_origin
        yield from self.type_hint_args
