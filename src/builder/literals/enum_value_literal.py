from stubmaker.builder.common import Node, BaseASTBuilder, BaseLiteral


class EnumValueLiteral(BaseLiteral):

    def __init__(self, node: Node, ast: BaseASTBuilder):
        super().__init__(node, ast)
        self.enum_class = self.ast.get_literal(Node(self.namespace, None, self.obj.__objclass__))

    def __iter__(self):
        yield self.enum_class
