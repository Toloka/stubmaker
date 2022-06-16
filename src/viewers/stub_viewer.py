__all__ = [
    'StubViewer',
]
import inspect
import os
from io import StringIO
from typing import Dict, Tuple, Optional, Set, List

from stubmaker.builder.definitions import (
    AttributeAnnotationDef,
    AttributeDef,
    ClassDef,
    MetaclassDef,
    DocumentationDef,
    EnumDef,
    FunctionDef,
    ModuleDef,
    ClassMethodDef,
    StaticMethodDef,
)
from stubmaker.builder.literals import ReferenceLiteral, TypeVarLiteral
from stubmaker.viewers.basic_viewer import BasicViewer
from stubmaker.viewers.common import add_inherited_singledispatchmethod
from stubmaker.viewers.util import (
    wrap_function_signature,
    indent,
    replace_representations_in_signature,
    get_common_namespace_prefix,
)


@add_inherited_singledispatchmethod(method_name='iter_over', implementation_prefix='iter_over')
@add_inherited_singledispatchmethod(method_name='view', implementation_prefix='view_')
class StubViewer(BasicViewer):

    class ModuleContext:
        def __init__(self, module_def: ModuleDef, viewer: 'StubViewer'):
            self.module_def = module_def
            self.viewer = viewer
            self.object_id_to_definition = {}

        def __enter__(self):
            self.viewer.module_context = self
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.viewer.module_context = None
            self.object_id_to_definition.clear()

    def view_reference_literal(self, reference_lit: ReferenceLiteral):
        view = super().view_reference_literal(reference_lit)

        import_module = self.module_context.module_def.get_import_module_for_representation(reference_lit)
        if not import_module:
            return view
        return f'{import_module}.{view}'

    def view_type_var_literal(self, type_var_lit: TypeVarLiteral):
        # Present name means that TypeVar is used in definition (i.e. T = TypeVar(...))
        if type_var_lit.node.name:
            return super().view_type_var_literal(type_var_lit)

        definition = self.module_context.object_id_to_definition.get(type_var_lit.id)
        if definition:
            prefix = get_common_namespace_prefix(type_var_lit.node.namespace, definition.namespace)
            return definition.namespace[len(prefix):] + definition.name

        # consider TypeVar being imported from other module
        imported_from_module = os.sys.modules[type_var_lit.obj.__module__]
        name = next(obj_name for obj_name, obj in imported_from_module.__dict__.items() if obj == type_var_lit.obj)
        import_module = self.module_context.module_def.get_import_module_for_representation(type_var_lit)
        if not import_module:
            return name
        return f'{import_module}.{name}'

    def view_attribute_annotation_definition(self, attribute_annotation_def: AttributeAnnotationDef):
        return f'{attribute_annotation_def.name}: {self.view(representation=attribute_annotation_def.annotation)}\n'

    def view_attribute_definition(self, attribute_def: AttributeDef):
        return f'{attribute_def.name} = {self.view(attribute_def.value)}\n'

    def view_class_definition(self, class_def: ClassDef):
        sio = StringIO()

        sio.write(f'class {class_def.name}')

        metaclass_is_type = class_def.metaclass.obj is type  # noqa
        metaclass_is_inherited = any(class_def.metaclass.obj is type(base.obj) for base in class_def.bases)  # noqa
        need_to_write_metaclass = not metaclass_is_type and not metaclass_is_inherited

        if class_def.bases and need_to_write_metaclass:
            bases = ', '.join(self.view(base) for base in class_def.bases)
            sio.write(f'({bases}, metaclass={self.view(class_def.metaclass)})')
        elif class_def.bases:
            bases = ', '.join(self.view(base) for base in class_def.bases)
            sio.write(f'({bases})')
        elif need_to_write_metaclass:
            sio.write(f'(metaclass={self.view(class_def.metaclass)})')
        sio.write(':\n')

        if class_def.docstring:
            sio.write(indent(f'{self.view(class_def.docstring)}\n'))

        if class_def.members:
            for name, rep in class_def.members.items():
                sio.write(indent(f'{self.view(rep)}'))

        if class_def.annotations:
            for name, annotation in class_def.annotations.items():
                sio.write(indent(f'{self.view(annotation)}'))

        if not class_def.docstring and not class_def.members and not class_def.annotations:
            sio.write(indent('...\n'))

        if not sio.getvalue().endswith('\n\n'):
            sio.write('\n')
        return sio.getvalue()

    def view_metaclass_definition(self, metaclass_def: MetaclassDef):
        return self.view_class_definition(metaclass_def)

    def view_documentation_definition(self, documentation_def: DocumentationDef):
        return f'"""{inspect.cleandoc(documentation_def.obj).rstrip()}\n"""\n'

    def view_enum_definition(self, enum_def: EnumDef):
        sio = StringIO()

        sio.write(f'class {enum_def.name}({", ".join([self.view(base) for base in enum_def.bases])}):\n')

        if enum_def.docstring:
            sio.write(indent(f'{self.view(enum_def.docstring)}\n'))

        if enum_def.enum_dict:
            for name, literal in enum_def.enum_dict.items():
                sio.write(indent(f'{name} = {self.view(literal)}\n'))
        else:
            sio.write(indent('...\n'))

        sio.write('\n')
        return sio.getvalue()

    def view_function_definition(self, function_def: FunctionDef):
        sio = StringIO()

        signature = replace_representations_in_signature(function_def.signature, self)

        wrapped_signature = wrap_function_signature(signature)

        if function_def.docstring:
            sio.write(f'def {function_def.name}{wrapped_signature}:\n')
            sio.write(indent(self.view(function_def.docstring)))
            sio.write(indent('...\n'))
        else:
            sio.write(f'def {function_def.name}{wrapped_signature}: ...\n')

        sio.write('\n')
        return sio.getvalue()

    def view_module_definition(self, module_def: ModuleDef):
        sio = StringIO()

        with StubViewer.ModuleContext(module_def, self) as ctx:
            # docstring
            if module_def.docstring:
                sio.write(f'{self.view(module_def.docstring)}\n')

            # all
            if hasattr(module_def.obj, '__all__'):
                if module_def.obj.__all__:
                    all_value = (',\n'.join(f"{token!r}" for token in module_def.obj.__all__))
                    sio.write(f'__all__ = [\n{indent(all_value)},\n]\n')
                else:
                    sio.write('__all__: list = []\n')

            used_object_ids = self.get_used_members_ids(module_def)

            # add used TypeVar definitions
            for representation in self.traverse(module_def):
                if isinstance(representation, AttributeDef) and isinstance(representation.value, TypeVarLiteral):
                    if representation.value.id in used_object_ids:
                        used_object_ids.add(representation.id)
                        ctx.object_id_to_definition[representation.value.id] = representation

            # imports
            imports, from_imports = module_def.get_imports(used_object_ids, self.traverse)

            self._write_imports_section(imports, sio)
            self._write_from_imports_section(from_imports, sio)

            if imports or from_imports:
                sio.write('\n')

            # module members
            if module_def.members:
                for representation in self.iter_over(module_def):
                    if representation.id in used_object_ids:
                        sio.write(self.view(representation))
                        sio.write('\n')

        return sio.getvalue().rstrip('\n') + '\n'

    def _write_from_imports_section(self, from_imports: Dict[str, Set[Tuple[str, Optional[str]]]], sio: StringIO):
        if from_imports:
            for key in sorted(from_imports.keys()):
                self._write_from_import(key, sorted(from_imports[key], key=lambda x: x[0]), sio)
            sio.write('\n')

    def _write_from_import(self, module_name: str, names: List[Tuple[str, Optional[str]]], sio: StringIO):
        if len(names) > 1:
            names = ',\n'.join(
                f'{name} as {import_as}' if import_as else name for name, import_as in names)
            sio.write(f'from {module_name} import (\n{indent(names)},\n)\n')
        else:
            names = ', '.join(f'{name} as {import_as}' if import_as else name for name, import_as in names)
            sio.write(f'from {module_name} import {names}\n')

    def _write_imports_section(self, imports: List[str], sio: StringIO):
        if imports:
            for name in sorted(imports):
                self._write_import(name, sio)
            sio.write('\n')

    def _write_import(self, module_name: str, sio: StringIO):
        sio.write(f'import {module_name}\n')

    def view_class_method_definition(self, class_method_definition: ClassMethodDef):
        return f'@classmethod\n{self.view_function_definition(class_method_definition)}'

    def view_static_method_definition(self, static_method_definition: StaticMethodDef):
        return f'@staticmethod\n{self.view_function_definition(static_method_definition)}'
