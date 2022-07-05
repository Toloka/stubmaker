import inspect
import typing

from stubmaker.builder.common import Node, BaseRepresentationsTreeBuilder, BaseDefinition, get_annotations
from typing_inspect import is_generic_type, get_generic_bases


class BaseClassDef(BaseDefinition):

    # TODO:  support properties

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)

        self.metaclass = self.tree.get_literal(self.tree.create_node_for_object(self.namespace, None, type(self.obj)))

        self.bases = []
        if self.obj.__bases__ != (object,):
            # get_generic_bases sometimes returns empty tuple even for Generic types (e.g. for typing.Protocol)
            generic_bases = get_generic_bases(self.obj) if is_generic_type(self.obj) else tuple()
            bases = generic_bases or self.obj.__bases__

            for base in bases:
                self.bases.append(self.tree.get_literal(self.tree.create_node_for_object(self.namespace, None, base)))

        self.members = {}
        for member_name in self.get_public_member_names():
            # Accessing members through __dict__ is important in order to be able
            # to distinguish between methods, classmethods and staticmethods
            member = self.obj.__dict__[member_name]

            node = self.tree.create_node_for_object(
                namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name if self.name else '',
                name=member_name,
                obj=member,
            )

            if isinstance(member, staticmethod):
                node.obj = member.__func__
                definition = self.tree.get_static_method_definition(node)
            elif isinstance(member, classmethod):
                node.obj = member.__func__
                definition = self.tree.get_class_method_definition(node)
            elif inspect.isfunction(member):
                definition = self.tree.get_function_definition(node)
            elif inspect.isclass(member) and member.__module__ == self.tree.module_name:
                definition = self.tree.get_class_definition(node)
            elif isinstance(member, typing.TypeVar):
                definition = self.tree.get_attribute_definition(node)
            else:
                continue

            self.members[member_name] = definition

        self.annotations = {}
        annotations = get_annotations(self.obj, eval_str=not tree.preserve_forward_references)
        for member_name, annotation in annotations.items():
            self.annotations[member_name] = self.tree.get_attribute_annotation_definition(
                self.tree.create_node_for_object(
                    namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name,
                    name=member_name,
                    obj=annotations[member_name],
                )
            )

    def get_public_member_names(self):
        cls = self.obj

        var_reg = None
        if hasattr(cls, '_variant_registry'):
            var_reg = cls._variant_registry

        names = set()

        for name in dir(cls):

            if name.startswith('__') and not inspect.isfunction(getattr(cls, name, None)):
                continue

            if var_reg and name == var_reg.field:
                continue

            if name == '_variant_registry':
                continue

            # Only considering members that were actually (re)defined in cls
            if self._is_redefined_in_current_class(name):
                names.add(name)

        ordered_names = []
        for name in cls.__dict__:
            if name in names:
                ordered_names.append(name)
                names.remove(name)

        for name in names:
            ordered_names.append(name)

        yield from ordered_names

        # return [name for name in dir(self.obj) if not name.startswith('__') and name != '__init__']

    def _is_redefined_in_current_class(self, name):
        cls_attr = getattr(self.obj, name)
        super_cls = super(self.obj, self.obj)
        super_cls_attr = getattr(super_cls, name, None)
        # check if function descriptor is actually redefined (i.e. classmethods and staticmethods)
        if hasattr(cls_attr, '__func__') and hasattr(super_cls_attr, '__func__'):
            return getattr(cls_attr, '__func__') != getattr(super_cls_attr, '__func__')
        return cls_attr is not super_cls_attr
