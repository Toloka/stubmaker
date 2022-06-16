from stubmaker.builder.common import Node, BaseDefinition, BaseRepresentationsTreeBuilder


class AttributeDef(BaseDefinition):
    """Represents `name = value`"""

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)
        self.value = self.tree.get_literal(node)

    @property
    def id(self):
        return id(self.value)
