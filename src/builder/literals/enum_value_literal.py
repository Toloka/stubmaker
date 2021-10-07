from stubmaker.builder.common import Node, BaseRepresentationsTreeBuilder, BaseLiteral


class EnumValueLiteral(BaseLiteral):

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)
        self.enum_class = self.tree.get_literal(Node(self.namespace, None, self.obj.__objclass__))

    def __iter__(self):
        yield self.enum_class
