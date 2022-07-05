from enum import Enum

from stubmaker.builder.common import Node, BaseDefinition, BaseRepresentationsTreeBuilder


class EnumDef(BaseDefinition):

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)
        assert issubclass(node.obj, Enum)
        self.bases = [self.tree.get_literal(
            self.tree.create_node_for_object(self.namespace, None, base)
        ) for base in self.obj.__bases__]
        self.enum_dict = {
            e.name: tree.get_literal(self.tree.create_node_for_object(self.namespace, None, e.value)) for e in self.obj
        }
