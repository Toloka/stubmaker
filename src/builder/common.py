import inspect
from typing import Generator, Optional

URL_REGEXP = r'https?://\S+'


class Node:
    """Spec for a represented object"""

    def __init__(self, namespace: str, name: Optional[str], obj):
        self.namespace = namespace
        self.name = name
        self.obj = obj

    @property
    def indentation_level(self) -> int:
        if not self.namespace:
            return 0
        return self.namespace.count('.') + 1

    def get_member(self, member_name: str) -> 'Node':
        return Node(
            namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name if self.name else '',
            name=member_name,
            obj=getattr(self.obj, member_name)
        )

    def get_literal_node(self, obj):
        return Node(
            namespace=self.namespace,
            name=None,
            obj=obj
        )

    @property
    def full_name(self):
        if hasattr(self.obj, '__module__') and hasattr(self.obj, '__qualname__'):
            return f'{self.obj.__module__}.{self.obj.__qualname__}'
        else:
            return ''


class BaseRepresentation:

    def __init__(self, node: Node, tree: 'RepresentationsTreeBuilder'):
        self.node = node
        self.tree = tree

    def __iter__(self):
        raise NotImplementedError

    @property
    def id(self):
        return id(self.obj)

    @property
    def obj(self):
        return self.node.obj

    @property
    def name(self):
        return self.node.name

    @property
    def namespace(self):
        return self.node.namespace

    @property
    def full_name(self):
        return self.node.full_name

    def traverse(self) -> Generator['BaseRepresentation', None, None]:
        """Recursively traverses the definition tree"""
        yield self
        for child in self:
            yield from child.traverse()


class BaseLiteral(BaseRepresentation):

    def __iter__(self):
        raise NotImplementedError


class BaseDefinition(BaseRepresentation):

    def __iter__(self):
        raise NotImplementedError

    def get_member_rep(self, member_name: str):
        return self.tree.get_definition(self.node.get_member(member_name))


class BaseRepresentationsTreeBuilder:

    # Helper methods

    def get_docstring(self, node: Node) -> Optional[BaseDefinition]:
        raise NotImplementedError

    # Get representation for definitions

    def get_definition(self, node: Node) -> BaseDefinition:
        raise NotImplementedError

    def get_attribute_definition(self, node: Node) -> BaseDefinition:
        raise NotImplementedError

    def get_documentation_definition(self, node: Node) -> BaseDefinition:
        raise NotImplementedError

    def get_class_definition(self, node: Node) -> BaseDefinition:
        raise NotImplementedError

    def get_function_definition(self, node: Node) -> BaseDefinition:
        raise NotImplementedError

    def get_module_definition(self, node: Node) -> BaseDefinition:
        raise NotImplementedError

    # Get representations for values

    def get_literal(self, obj):
        raise NotImplementedError

    def get_literal_for_reference(self, obj) -> BaseLiteral:
        raise NotImplementedError

    def get_literal_for_type_hint(self, obj) -> BaseLiteral:
        raise NotImplementedError

    def get_literal_for_value(self, obj: Node) -> BaseLiteral:
        raise NotImplementedError


def get_annotations(obj):
    if inspect.isclass(obj):
        annotations = {}
        for parent in obj.__mro__[::-1]:
            annotations.update(getattr(parent, '__annotations__', {}))
        return annotations
    return getattr(obj, '__annotations__', {})
