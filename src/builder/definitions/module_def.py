import builtins
import inspect
from collections import defaultdict
from typing import Any, Dict, get_type_hints

from stubmaker.builder.common import Node, BaseDefinition, BaseASTBuilder
from stubmaker.builder.literals.reference_literal import ReferenceLiteral
from stubmaker.builder.literals.type_hint_literal import TypeHintLiteral


def get_type_name(obj):
    if hasattr(obj, '__name__'):
        return obj.__name__
    # types from typing module (i.e. Callable, Optional, etc.)
    if hasattr(obj, '_name'):
        return obj._name
    return None


class ModuleDef(BaseDefinition):

    # TODO: support imported functions
    # TODO: support imported classes

    def __init__(self, node: Node, ast: BaseASTBuilder):
        super().__init__(node, ast)

        self.docstring = self.ast.get_docstring(self.node)

        self.members = {}
        annotations = get_type_hints(self.obj)

        public_members = self.get_public_members()

        for member_name, member in self.remove_imported_members(public_members).items():
            # check if member is alias
            if get_type_name(member) != member_name:
                if member_name in annotations:
                    self.members[member_name] = self.ast.get_attribute_annotation_definition(Node(
                        namespace=f'{self.namespace}.{self.name}' if self.namespace else self.name,
                        name=member_name,
                        obj=annotations[member_name],
                    ))
                else:
                    self.members[member_name] = self.ast.get_attribute_definition(self.node.get_member(member_name))
            else:
                node = self.node.get_member(member_name)
                definition = self.ast.get_definition(node)
                self.members[member_name] = definition

    def __iter__(self):
        if self.docstring:
            yield self.docstring

        yield from self.members.values()

    def _is_import_necessary(self, member):
        if inspect.ismodule(member):
            return self.ast.module_name != member.__name__

        member_name = get_type_name(member)
        if not member_name:
            return False

        return self.ast.module_name != member.__module__ and member_name not in builtins.__dict__

    def _get_import_from(self, member, member_name):
        guessed_module = inspect.getmodule(member)
        if member_name in guessed_module.__dict__:
            return member.__module__, member_name

        raise ValueError(f"{member_name} can't be imported from from {guessed_module.__name__}")

    def get_imports(self, used_object_ids):
        imports = set()
        from_imports = defaultdict(set)

        for curr in self.traverse():
            if curr.id not in used_object_ids:
                continue

            if isinstance(curr, TypeHintLiteral):
                imports.add('typing')

            if isinstance(curr, ReferenceLiteral):
                if not self._is_import_necessary(curr.obj):
                    continue

                # TODO: not all builtins are available from globals. For instance NoneType
                if inspect.ismodule(curr.obj):
                    module_name = curr.obj.__name__
                else:
                    module_name = curr.obj.__module__

                # hack urllib3 stubs for mypy
                if module_name and module_name.startswith('urllib3'):
                    if inspect.ismodule(curr.obj):
                        curr.obj.__name__ = f'requests.packages.{module_name}'
                        module_name = curr.obj.__name__
                    else:
                        curr.obj.__module__ = f'requests.packages.{module_name}'
                        module_name = curr.obj.__module__

                imports.add(module_name)

        # try to add unused but specified in __all__ dependencies
        for member_name in self.obj.__all__:
            member = getattr(self.obj, member_name, None)
            if not member:
                # annotated attribute without value
                member = self.members[member_name].obj
            if self._is_import_necessary(member):
                # check if object is module
                if inspect.ismodule(member):
                    member_package_name = '.'.join(member.__name__.split('.')[:-1])
                    from_imports[member_package_name].add((member_name, None))
                else:
                    from_module, from_name = self._get_import_from(member, member_name)
                    from_imports[from_module].add((from_name, None))

        return imports, from_imports

    def remove_imported_members(self, members):
        required_members = {}

        for member_name, member in members.items():
            if inspect.ismodule(member):
                continue

            module_name = getattr(member, '__module__', None)
            if module_name and module_name != self.ast.module_name and member_name == get_type_name(member):
                # imported external symbol that is not an alias defined in current module
                continue

            required_members[member_name] = member

        return required_members

    def get_public_members(self) -> Dict[str, Any]:
        public_members = {member_name: member for member_name, member in self.obj.__dict__.items()
                          if not member_name.startswith('__')}

        for member_name in get_type_hints(self.obj):
            # try to add module level attributes with annotations but without value that are specified in __all__
            # (such attributes can't be retrieved from __dict__)
            if member_name not in public_members and member_name in self.obj.__all__:
                public_members[member_name] = None

        return public_members
