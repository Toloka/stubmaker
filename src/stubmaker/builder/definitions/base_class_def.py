import inspect
from abc import abstractmethod
from typing import TypeVar, cast

from stubmaker.builder.common import BaseDefinition, BaseRepresentationsTreeBuilder, Node, get_annotations
from stubmaker.builder.definitions.function_def import FunctionDef
from typing_inspect import get_generic_bases, is_generic_type


def _try_patch_pydantic_init_signature(cls):
    """Pydantic implements custom class signature but assigns it only to cls.__signature__ but not
    cls.__init__.__signature__ due to technical reasons: https://github.com/pydantic/pydantic/issues/1032. This
    function tries to detect if the class is pydantic BaseModel and manually assigns signature to __init__.__signature__
    """

    try:
        from pydantic import BaseModel  # type: ignore

        if issubclass(cls, BaseModel):
            parameters = cls.__signature__.parameters.values()
            has_positional_only = any(param.kind == inspect.Parameter.POSITIONAL_ONLY for param in parameters)
            if has_positional_only:
                kind = inspect.Parameter.POSITIONAL_ONLY
            else:
                kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
            cls.__init__.__signature__ = cls.__signature__.replace(
                parameters=[inspect.Parameter(name='self', kind=kind), *parameters],
            )
    except ImportError:
        pass


class BaseClassDef(BaseDefinition):
    # TODO:  support properties

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)
        _try_patch_pydantic_init_signature(node.obj)

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
            # Accessing members through getattr_static is important in order to be able
            # to distinguish between methods, classmethods and staticmethods
            member = inspect.getattr_static(self.obj, member_name)

            def member_node_factory(obj):
                return self.tree.create_node_for_object(
                    namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name if self.name else '',
                    name=member_name,
                    obj=obj,
                )

            if isinstance(member, staticmethod):
                definition = self.tree.get_static_method_definition(member_node_factory(member.__func__))
            elif isinstance(member, classmethod):
                definition = self.tree.get_class_method_definition(member_node_factory(member.__func__))
            elif inspect.isfunction(member):
                definition = self.tree.get_function_definition(member_node_factory(member))
            elif inspect.isclass(member) and member.__module__ == self.tree.module_name:
                definition = self.tree.get_class_definition(member_node_factory(member))
            elif isinstance(member, TypeVar):
                definition = self.tree.get_attribute_definition(member_node_factory(member))
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

    @property
    def init_method(self) -> FunctionDef:
        return cast(FunctionDef, self.members['__init__'])

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

    @abstractmethod
    def _is_redefined_in_current_class(self, name):
        raise NotImplementedError
