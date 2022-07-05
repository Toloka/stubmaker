import collections.abc
import enum
import inspect
from contextvars import ContextVar
from enum import Enum
from types import ModuleType
from typing import TypeVar, Optional

from stubmaker.builder.common import BaseDefinition, BaseLiteral, BaseRepresentationsTreeBuilder, Node
from stubmaker.builder.definitions import (
    AttributeAnnotationDef,
    AttributeDef,
    ClassDef,
    MetaclassDef,
    DocumentationDef,
    FunctionDef,
    ModuleDef,
    StaticMethodDef,
    ClassMethodDef,
    EnumDef
)
from stubmaker.builder.literals import ReferenceLiteral, TypeHintLiteral, TypeVarLiteral, ValueLiteral, EnumValueLiteral
from typing_inspect import is_generic_type


class RepresentationsTreeBuilder(BaseRepresentationsTreeBuilder):

    DEFAULT_DESCRIBED_OBJECTS = {
        ModuleType: ('types', 'ModuleType'),
        ContextVar: ('contextvars', 'ContextVar'),
    }

    def __init__(
        self,
        module_name, module,
        module_root=None,
        modules_aliases_mapping=None,
        described_objects=None,
        preserve_forward_references=True,
    ):
        """Class used to build the tree of objects and definitions representations for one module.

        Parameters:
            module_name: name of the current module.
            module: current module object.
            module_root: current module root package. Used in imports.
            modules_aliases_mapping: a dictionary of modules aliases to use.
            described_objects: a dictionary from python objects to tuples consisting of module and qualname for each
                object (e.g. ModuleType: ("types", "ModuleType")). Such objects' names and modules will not be deduced
                based on runtime data and provided names and modules will be used instead.
            preserve_forward_references: if True forward references will not be evaluated in resulting expressions.
        """

        super().__init__()

        if modules_aliases_mapping is None:
            modules_aliases_mapping = {
                '_asyncio': 'asyncio',
            }

        described_objects = described_objects or self.DEFAULT_DESCRIBED_OBJECTS
        self.object_qualname_mapping = {obj: qualname for obj, (_, qualname) in described_objects.items()}
        self.object_module_mapping = {obj: module for obj, (module, _) in described_objects.items()}

        self.module_name = module_name
        self.module_root = module_root or module_name
        self.modules_aliases_mapping = modules_aliases_mapping
        self.preserve_forward_references = preserve_forward_references

        self.module_rep = self.get_module_definition(self.create_node_for_object('', '', module))

    def create_node_for_object(self, namespace, name, obj):
        if isinstance(obj, collections.abc.Hashable):
            module_name = self.object_module_mapping.get(obj)
            qualname = self.object_qualname_mapping.get(obj)
        else:
            module_name = None
            qualname = None

        if module_name is None:
            guessed_module = inspect.getmodule(obj)
            module_name = guessed_module and guessed_module.__name__

        return Node(
            namespace, name, obj,
            module_name=self.map_module_name(module_name),
            qualname=qualname or getattr(obj, '__qualname__', None),
        )

    # Get representation for definitions

    def resolve_namespace_definition(self, node: Node):
        """Resolve a node to its definition"""

        if inspect.isclass(node.obj):
            return self.get_class_definition(node)

        if inspect.isfunction(node.obj):
            return self.get_function_definition(node)

        return self.get_attribute_definition(node)

    def map_module_name(self, module_name: Optional[str]) -> Optional[str]:
        if not module_name:
            return None

        prefixes = [(len(key), key) for key in self.modules_aliases_mapping if module_name.startswith(key)]
        if not prefixes:
            return module_name
        longest_prefix = max(prefixes)[1]
        return self.modules_aliases_mapping[longest_prefix] + module_name[len(longest_prefix):]

    # def resolve_value_literal(sel):

    def get_definition(self, node: Node):
        """Resolve a node to its definition"""

        if inspect.isclass(node.obj):
            return self.get_class_definition(node)

        if inspect.isfunction(node.obj):
            return self.get_function_definition(node)

        return self.get_attribute_definition(node)

    def get_attribute_definition(self, node: Node) -> BaseDefinition:
        """Get a definition representing `name = literal`"""
        return AttributeDef(node, self)

    def get_attribute_annotation_definition(self, node: Node) -> BaseDefinition:
        """Get a definition representing `name: literal`"""
        return AttributeAnnotationDef(node, self)

    def get_documentation_definition(self, node: Node) -> BaseDefinition:
        """Get a definition representing docstring"""
        return DocumentationDef(node, self)

    def get_class_definition(self, node: Node) -> BaseDefinition:

        if node.module_name == self.module_name:
            if issubclass(node.obj, Enum):
                return EnumDef(node, self)
            if issubclass(node.obj, type):
                return MetaclassDef(node, self)
            return ClassDef(node, self)

        return self.get_attribute_definition(node)

    def get_function_definition(self, node: Node) -> BaseDefinition:
        """Get a definition representing a function or a method"""
        return FunctionDef(node, self)

    def get_class_method_definition(self, node: Node) -> BaseDefinition:
        return ClassMethodDef(node, self)

    def get_static_method_definition(self, node: Node) -> BaseDefinition:
        return StaticMethodDef(node, self)

    def get_module_definition(self, node: Node) -> BaseDefinition:
        """Get a definition representing a module"""
        return ModuleDef(node, self)

    # Get representations for values

    def get_literal(self, node: Node):
        """Resolves an object to a literal"""

        if is_generic_type(node.obj):
            return TypeHintLiteral(node, self)

        if inspect.isclass(node.obj) or inspect.ismodule(node.obj) or inspect.isfunction(node.obj):
            return ReferenceLiteral(node, self)

        if isinstance(node.obj, enum.Enum):
            return EnumValueLiteral(node, self)

        if isinstance(node.obj, TypeVar):
            return TypeVarLiteral(node, self)

        if str(node.obj).startswith('typing.'):
            return TypeHintLiteral(node, self)

        return ValueLiteral(node, self)

    def get_literal_for_reference(self, obj) -> BaseLiteral:
        """Get a literal in form of `x.y.z`"""
        return ReferenceLiteral(obj, self)

    def get_literal_for_type_hint(self, obj) -> BaseLiteral:
        """Get literal for a typing.* hints"""
        return TypeHintLiteral(obj, self)

    def get_literal_for_value(self, obj: Node) -> BaseLiteral:
        """Get a literal for plain values such as None, strings etc"""
        return ValueLiteral(obj, self)
