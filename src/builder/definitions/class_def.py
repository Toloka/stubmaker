import inspect
import typing

from stubmaker.builder.common import Node, BaseRepresentationsTreeBuilder, BaseDefinition, get_annotations


class ClassDef(BaseDefinition):

    # TODO:  support properties

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)

        self.docstring = self.tree.get_docstring(self.node)

        self.bases = []
        if self.obj.__bases__ != (object,):
            for base in self.node.obj.__bases__:
                self.bases.append(self.tree.get_literal(Node(self.namespace, None, base)))

        self.members = {}
        for member_name in self.get_public_member_names():
            # Accessing members through __dict__ is important in order to be able
            # to distinguish between methods, classmethods and staticmethods
            member = self.obj.__dict__[member_name]

            # TODO: dirty hack
            node = self.node.get_member(member_name)
            node.obj = member

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
        annotations = get_annotations(self.obj)
        for member_name, annotation in annotations.items():
            self.annotations[member_name] = self.tree.get_attribute_annotation_definition(Node(
                namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name,
                name=member_name,
                obj=annotations[member_name],
            ))

    def __iter__(self):
        if self.docstring:
            yield self.docstring

        yield from self.bases
        yield from self.members.values()
        yield from self.annotations.values()

    def get_public_member_names(self):
        cls = self.obj

        var_reg = None
        if hasattr(cls, '_variant_registry'):
            var_reg = cls._variant_registry

        names = set()

        for name in dir(cls):

            # Skipping all private members except for __init__
            if name.startswith('_') and name != '__init__':
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
