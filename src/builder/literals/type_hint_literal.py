import sys
import typing
from typing import Union, Optional, Callable

from stubmaker.builder.common import BaseLiteral, BaseRepresentationsTreeBuilder, Node


class TypeHintLiteral(BaseLiteral):
    """Represents a type hint"""

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)

        # Python < 3.9 support for generic types without arguments
        is_special = getattr(self.obj, '_special', False)

        # typing.get_args works with Callable[[], int] but does not work with
        # Callable in Python 3.8. So __args__ seems more reliable
        if not is_special:
            args = getattr(self.obj, '__args__', ())
        else:
            args = ()

        # get origin of generic type
        if getattr(self.obj, '_name', None):
            # If has _name ignore __origin__ field and get origin directly from types module. This is necessary for
            # typing aliases (e.g. __origin__ of List[int] is list instead of typing.List).
            origin = getattr(typing, self.obj._name)
            if sys.version_info >= (3, 10) and origin is Optional:
                origin = Union
        else:
            # Fallback to using __origin__. For non-generic types (e.g. List without arguments) retrieve object itself.
            origin = getattr(self.obj, '__origin__', self.obj)

        if origin is Callable and len(args) > 0 and args[0] is not Ellipsis:
            args = ([self.tree.get_literal(self.tree.create_node_for_object(self.namespace, None, arg))
                     for arg in args[:-1]], args[-1])
        elif origin is Union and type(None) in args and len(args) == 2:  # noqa: E721
            origin = Optional
            args = [arg for arg in args if arg is not type(None)]  # noqa: E721

        args = [None if arg is type(None) else arg for arg in args]  # noqa: E721
        self.type_hint_origin = self.tree.get_literal_for_reference(
            self.tree.create_node_for_object(self.namespace, None, origin)
        )
        self.type_hint_args = [self.tree.get_literal(self.tree.create_node_for_object(self.namespace, None, arg))
                               for arg in args]
