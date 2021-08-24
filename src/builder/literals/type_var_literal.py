from typing import TypeVar
from stubmaker.builder.common import BaseLiteral, BaseASTBuilder, Node


class TypeVarLiteral(BaseLiteral):
    """Represents a TypeVar"""

    def __init__(self, node: Node, ast: BaseASTBuilder):
        super().__init__(node, ast)
        self.type_var_name = self.ast.get_literal(Node(self.namespace, None, self.obj.__name__))
        self.type_var_reference = self.ast.get_literal(Node(self.namespace, None, TypeVar))
        self.covariant = self.ast.get_literal(Node(self.namespace, None, self.obj.__covariant__))
        self.contravariant = self.ast.get_literal(Node(self.namespace, None, self.obj.__contravariant__))
        self.bound = self.ast.get_literal(Node(self.namespace, None, self.obj.__bound__))

    def __iter__(self):
        yield self.ast.get_literal(Node(self.namespace, None, TypeVar))
        yield self.type_var_name
        yield self.covariant
        yield self.contravariant
        yield self.bound
