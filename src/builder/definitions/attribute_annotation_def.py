from stubmaker.builder.common import Node, BaseDefinition, BaseASTBuilder


class AttributeAnnotationDef(BaseDefinition):
    """Represents `name: annotation`"""

    def __init__(self, node: Node, ast: BaseASTBuilder):
        super().__init__(node, ast)
        self.annotation = self.ast.get_literal(node)

    @property
    def id(self):
        return id(self.annotation)

    def __iter__(self):
        yield self.annotation
