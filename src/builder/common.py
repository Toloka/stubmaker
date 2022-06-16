import inspect
from typing import Optional, get_type_hints


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
    def module(self) -> str:
        if inspect.ismodule(self.obj):
            return self.tree.map_module_name(self.obj.__name__)
        else:
            guessed_module = inspect.getmodule(self.obj)
            # TODO: support imports from set of known modules (e.g. import ModuleType from types despite __module__
            #  being builtins)
            return self.tree.map_module_name(guessed_module.__name__)


class BaseLiteral(BaseRepresentation):
    pass


class BaseDefinition(BaseRepresentation):
    pass

    def get_member_rep(self, member_name: str):
        return self.tree.get_definition(self.node.get_member(member_name))


class BaseRepresentationsTreeBuilder:
    def __init__(
        self,
        module_name, module,
        module_root=None,
        modules_aliases_mapping=None,
        preserve_forward_references=True,
    ):
        if modules_aliases_mapping is None:
            modules_aliases_mapping = {
                '_asyncio': 'asyncio',
                'pandas.core.frame': 'pandas',
                'pandas.core.series': 'pandas',
            }

        self.module_name = module_name
        self.module_root = module_root or module_name
        self.modules_aliases_mapping = modules_aliases_mapping
        self.preserve_forward_references = preserve_forward_references

        self.module_rep = self.get_module_definition(Node('', '', module))

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
