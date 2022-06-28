import inspect
from typing import Optional, get_type_hints, TYPE_CHECKING

if TYPE_CHECKING:
    from stubmaker.builder.representations_tree_builder import RepresentationsTreeBuilder


class Node:
    """Object data used in BaseRepresentation type.

    Parameters:
        namespace: namespace of representation.
        name: name of representation associated with object in the namespace. May be None for literals (e.g. type
            annotations does not have names, but classes do).
        obj: python object.
        module_name: name of the module where obj is defined.
        qualname: qualname of obj.
    """

    def __init__(
        self,
        namespace: str, name: Optional[str], obj, module_name: Optional[str], qualname: Optional[str],
    ):
        self.namespace = namespace
        self.name = name
        self.obj = obj
        self.module_name = module_name
        self.qualname = qualname

    @property
    def full_name(self):
        return f'{self.module_name}.{self.qualname}' if self.module_name else self.qualname


class BaseRepresentation:

    def __init__(self, node: Node, tree: 'RepresentationsTreeBuilder'):
        self.node = node
        self.tree = tree

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

    @property
    def module_name(self) -> str:
        return self.node.module_name

    @property
    def qualname(self) -> str:
        return self.node.qualname


class BaseLiteral(BaseRepresentation):
    pass


class BaseDefinition(BaseRepresentation):

    def get_node_for_member(self, member_name: str) -> Node:
        return self.tree.create_node_for_object(
            namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name if self.name else '',
            name=member_name,
            obj=getattr(self.obj, member_name),
        )

    @property
    def docstring(self) -> Optional['BaseDefinition']:
        if getattr(self.obj, '__doc__') is not None:
            return self.tree.get_documentation_definition(self.get_node_for_member('__doc__'))
        return None


class BaseRepresentationsTreeBuilder:

    # Helper methods

    def create_node_for_object(self, namespace, name, obj) -> Node:
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


def get_annotations(obj, eval_str):
    if eval_str:
        return get_type_hints(obj)

    if inspect.isclass(obj):
        annotations = {}
        for parent in obj.__mro__[::-1]:
            annotations.update(getattr(parent, '__annotations__', {}))
        return annotations
    return getattr(obj, '__annotations__', {})


def get_type_name(obj):
    if hasattr(obj, '__name__'):
        return obj.__name__
    # types from typing module (i.e. Callable, Optional, etc.)
    if hasattr(obj, '_name'):
        return obj._name
    return None
