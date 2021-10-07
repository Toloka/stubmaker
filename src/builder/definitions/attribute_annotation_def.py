from stubmaker.builder.common import Node, BaseDefinition, BaseRepresentationsTreeBuilder


class AttributeAnnotationDef(BaseDefinition):
    """Represents `name: annotation`"""

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)
        # we don't want to associate annotation object with name (e.g. TypeVar used in annotation shouldn't be accessed
        # with this name)
        self.annotation = self.tree.get_literal(Node(node.namespace, '', node.obj))

    @property
    def id(self):
        return id(self.annotation)

    def __iter__(self):
        yield self.annotation
