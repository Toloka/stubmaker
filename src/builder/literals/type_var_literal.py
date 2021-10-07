from typing import TypeVar
from stubmaker.builder.common import BaseLiteral, BaseRepresentationsTreeBuilder, Node


class TypeVarLiteral(BaseLiteral):
    """Represents a TypeVar"""

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)
        self.type_var_name = self.tree.get_literal(Node(self.namespace, None, self.obj.__name__))
        self.type_var_reference = self.tree.get_literal(Node(self.namespace, None, TypeVar))
        self.covariant = self.tree.get_literal(Node(self.namespace, None, self.obj.__covariant__))
        self.contravariant = self.tree.get_literal(Node(self.namespace, None, self.obj.__contravariant__))
        self.bound = self.tree.get_literal(Node(self.namespace, None, self.obj.__bound__))

    def __iter__(self):
        yield self.tree.get_literal(Node(self.namespace, None, TypeVar))
        yield self.type_var_name
        yield self.covariant
        yield self.contravariant
        yield self.bound
