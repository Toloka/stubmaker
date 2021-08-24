from enum import Enum

from stubmaker.builder.common import Node, BaseDefinition, BaseASTBuilder


class EnumDef(BaseDefinition):

    def __init__(self, node: Node, ast: BaseASTBuilder):
        super().__init__(node, ast)
        assert issubclass(node.obj, Enum)
        self.docstring = self.ast.get_docstring(self.node)
        self.bases = [self.ast.get_literal(Node(self.namespace, None, base)) for base in self.obj.__bases__]
        self.enum_dict = {e.name: ast.get_literal(Node(self.namespace, None, e.value)) for e in self.obj}

    def __iter__(self):
        yield from self.bases
        yield from self.enum_dict.values()
