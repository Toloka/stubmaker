from stubmaker.builder.common import Node, BaseDefinition, BaseASTBuilder


class AttributeDef(BaseDefinition):
    """Represents `name = value`"""

    def __init__(self, node: Node, ast: BaseASTBuilder):
        super().__init__(node, ast)
        self.value = self.ast.get_literal(node)

    @property
    def id(self):
        return id(self.value)

    def __iter__(self):
        yield self.value
