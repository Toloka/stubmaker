import enum
import inspect
from enum import Enum
from typing import Optional, TypeVar

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

    def __str__(self):
        return str(self.module_rep)

    def get_docstring(self, node: Node) -> Optional[BaseDefinition]:
        if getattr(node.obj, '__doc__') is not None:
            return self.get_documentation_definition(node.get_member('__doc__'))
        return None

    # Get representation for definitions

    def resolve_namespace_definition(self, node: Node):
        """Resolve a node to its definition"""

        if inspect.isclass(node.obj):
            return self.get_class_definition(node)

        if inspect.isfunction(node.obj):
            return self.get_function_definition(node)

        return self.get_attribute_definition(node)

    def map_module_name(self, module_name: str) -> str:
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

        if node.obj.__module__ == self.module_name:
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
