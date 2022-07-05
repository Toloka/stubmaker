from stubmaker.builder.common import Node, BaseRepresentationsTreeBuilder, BaseLiteral


class EnumValueLiteral(BaseLiteral):

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)
        self.enum_class = self.tree.get_literal(
            self.tree.create_node_for_object(self.namespace, None, self.obj.__objclass__)
        )
