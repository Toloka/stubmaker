import builtins
import inspect
from collections import defaultdict
from typing import Any, Dict, Set, Tuple, Optional, Callable, TypeVar, Iterable

from stubmaker.builder.common import (
    Node,
    BaseDefinition,
    BaseRepresentationsTreeBuilder,
    BaseRepresentation,
    get_annotations,
    get_type_name,
)
from stubmaker.builder.literals import TypeHintLiteral, TypeVarLiteral, ReferenceLiteral


class ModuleDef(BaseDefinition):

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)

        self.docstring = self.tree.get_docstring(self.node)

        self.members = {}
        annotations = get_annotations(self.obj, eval_str=not tree.preserve_forward_references)

        members = self.get_representable_members()

        for member_name, member in members.items():
            # check if member is alias
            if get_type_name(member) != member_name:
                if member_name in annotations:
                    self.members[member_name] = self.tree.get_attribute_annotation_definition(Node(
                        namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name,
                        name=member_name,
                        obj=annotations[member_name],
                    ))
                else:
                    self.members[member_name] = self.tree.get_attribute_definition(self.node.get_member(member_name))
            else:
                node = self.node.get_member(member_name)
                definition = self.tree.get_definition(node)
                self.members[member_name] = definition

    def _is_import_necessary(self, member):
        if inspect.ismodule(member):
            return self.tree.module_name != member.__name__

        if isinstance(member, TypeVar):
            return member.__module__ != self.tree.module_name

        member_name = get_type_name(member)
        if not member_name:
            return False

        return self.tree.module_name != member.__module__ and member_name not in builtins.__dict__

    def get_import_module_for_representation(self, child_repr: BaseRepresentation) -> Optional[str]:
        if isinstance(child_repr, (TypeHintLiteral, TypeVarLiteral, ReferenceLiteral)) and \
                self._is_import_necessary(child_repr.obj):
            return child_repr.module

    def get_imports(
        self,
        used_object_ids: Set[int], traverse_method: Callable[[BaseRepresentation], Iterable[BaseRepresentation]]
    ) -> Tuple[Set[str], Dict[str, Set[Tuple[str, Optional[str]]]]]:
        imports = set()
        from_imports = defaultdict(set)

        for curr in traverse_method(self):
            if curr.id in used_object_ids:
                import_module = self.get_import_module_for_representation(curr)
                if import_module:
                    imports.add(import_module)

        # try to add unused but specified in __all__ dependencies
        for member_name in self.obj.__all__:
            # check if __all__ entry is module
            if member_name in self.obj.__dict__ and inspect.ismodule(self.obj.__dict__[member_name]):
                member_package_name = '.'.join(self.obj.__dict__[member_name].__name__.split('.')[:-1])
                from_imports[member_package_name].add((member_name, None))
            else:
                if member_name in self.members:
                    member_repr = self.members[member_name]
                elif member_name in self.obj.__dict__:
                    member_repr = self.tree.get_literal(self.node.get_literal_node(self.obj.__dict__[member_name]))
                else:
                    raise RuntimeError(f'{self.obj.__name__}: {member_name} is specified in __all__'
                                       f' but not found in __dict__ or __annotations__')
                import_module = self.get_import_module_for_representation(member_repr)
                if import_module:
                    from_imports[member_repr.module].add((member_name, None))

        return imports, from_imports

    def get_module_members(self) -> Dict[str, Any]:
        members = dict(self.obj.__dict__)
        for member_name in get_annotations(self.obj, eval_str=not self.tree.preserve_forward_references):
            # try to add module level attributes with annotations but without value that are specified in __all__
            # (such attributes can't be retrieved from __dict__)
            if member_name in self.obj.__all__:
                members[member_name] = None
        return members

    def private_module_members_removed(self, members: Dict[str, Any]) -> Dict[str, Any]:
        return {member_name: member for member_name, member in members.items() if not member_name.startswith('__')}

    def imported_members_removed(self, members: Dict[str, Any]) -> Dict[str, Any]:
        required_members = {}

        for member_name, member in members.items():
            if inspect.ismodule(member):
                continue

            module_name = getattr(member, '__module__', None)
            if module_name and module_name != self.tree.module_name and member_name == get_type_name(member):
                # imported external symbol that is not an alias defined in current module
                continue

            required_members[member_name] = member

        return required_members

    def get_representable_members(self):
        members = self.get_module_members()
        members = self.private_module_members_removed(members)
        return self.imported_members_removed(members)
