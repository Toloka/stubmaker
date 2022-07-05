import builtins
import inspect
from collections import defaultdict
from typing import Dict, Set, Tuple, Optional, Callable, TypeVar, Iterable, Any

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

        self.members = self.get_members_representations()

    def _is_import_necessary(self, member: BaseRepresentation):
        if inspect.ismodule(member.obj):
            return self.tree.module_name != member.name

        if isinstance(member.obj, TypeVar):
            return member.module_name != self.tree.module_name

        member_name = get_type_name(member.obj)
        if not member_name:
            return False

        return self.tree.module_name != member.module_name and member_name not in builtins.__dict__

    def get_import_module_for_representation(self, representation: BaseRepresentation) -> Optional[str]:
        if isinstance(representation, (TypeHintLiteral, TypeVarLiteral, ReferenceLiteral)) and \
                self._is_import_necessary(representation):
            return representation.module_name

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
                    member_repr = self.tree.get_literal(
                        self.tree.create_node_for_object(self.namespace, None, self.obj.__dict__[member_name])
                    )
                else:
                    raise RuntimeError(f'{self.obj.__name__}: {member_name} is specified in __all__'
                                       f' but not found in __dict__ or __annotations__')
                import_module = self.get_import_module_for_representation(member_repr)
                if import_module:
                    from_imports[member_repr.module_name].add((member_name, None))

        return imports, from_imports

    def get_public_module_member_objects(self) -> Dict[str, Any]:
        member_objects = dict(self.obj.__dict__)
        annotations = get_annotations(self.obj, eval_str=not self.tree.preserve_forward_references)
        for member_name in annotations:
            # try to add module level attributes with annotations but without value that are specified in __all__
            # (such attributes can't be retrieved from __dict__)
            if member_name in self.obj.__all__:
                member_objects[member_name] = None
        return {
            member_name: member for member_name, member in member_objects.items() if not member_name.startswith('__')
        }

    def _get_members_defined_in_current_module(self, members: Dict[str, BaseRepresentation]):
        local_members = {}
        for member_name, member in members.items():
            if member is None or inspect.ismodule(member.obj):
                continue

            if (member.module_name and member.module_name != self.tree.module_name and
                    member_name == get_type_name(member.obj)):
                # imported external symbol that is not an alias defined in current module
                continue

            local_members[member_name] = member
        return local_members

    def get_members_representations(self) -> Dict[str, BaseRepresentation]:
        member_objects = self.get_public_module_member_objects()
        annotations = get_annotations(self.obj, eval_str=not self.tree.preserve_forward_references)
        members = {}

        for member_name in annotations:
            # try to add module level attributes with annotations but without value that are specified in __all__
            # (such attributes can't be retrieved from __dict__)
            if member_name in self.obj.__all__:
                member_objects[member_name] = None

        for member_name, member_object in member_objects.items():
            # check if member is alias
            if get_type_name(member_object) != member_name:
                if member_name in annotations:
                    members[member_name] = self.tree.get_attribute_annotation_definition(
                        self.tree.create_node_for_object(
                            namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name,
                            name=member_name,
                            obj=annotations[member_name],
                        )
                    )
                else:
                    members[member_name] = self.tree.get_attribute_definition(
                        self.get_node_for_member(member_name)
                    )
            else:
                node = self.get_node_for_member(member_name)
                definition = self.tree.get_definition(node)
                members[member_name] = definition

        return self._get_members_defined_in_current_module(members)
