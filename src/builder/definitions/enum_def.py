from enum import Enum

from stubmaker.builder.common import Node, BaseDefinition, BaseRepresentationsTreeBuilder


class EnumDef(BaseDefinition):

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)
        assert issubclass(node.obj, Enum)
        self.docstring = self.tree.get_docstring(self.node)
        self.bases = [self.tree.get_literal(Node(self.namespace, None, base)) for base in self.obj.__bases__]
        self.enum_dict = {e.name: tree.get_literal(Node(self.namespace, None, e.value)) for e in self.obj}

    def __iter__(self):
        yield from self.bases
        yield from self.enum_dict.values()
