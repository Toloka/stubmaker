__all__ = [
    'StubViewer',
]
import inspect

from io import StringIO

from stubmaker.viewers.basic_viewer import BasicViewer
from stubmaker.viewers.common import add_inherited_singledispatchmethod
from stubmaker.viewers.util import wrap_function_signature, indent, replace_representations_in_signature
from stubmaker.builder.definitions import (
    AttributeAnnotationDef,
    AttributeDef,
    ClassDef,
    DocumentationDef,
    EnumDef,
    FunctionDef,
    ModuleDef,
    ClassMethodDef,
    StaticMethodDef,
)
from stubmaker.builder.literals import ReferenceLiteral


@add_inherited_singledispatchmethod(method_name='view', implementation_prefix='view_')
class StubViewer(BasicViewer):

    class ModuleContext:
        def __init__(self, module_def: ModuleDef, viewer: 'StubViewer'):
            self.module_def = module_def
            self.viewer = viewer

        def __enter__(self):
            self.viewer.module_context = self
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.viewer.module_context = None

    def view_reference_literal(self, reference_lit: ReferenceLiteral):
        view = super().view_reference_literal(reference_lit)

        obj_module = getattr(reference_lit.obj, '__module__', None)

        if not self.module_context.module_def._is_import_necessary(reference_lit.obj):
            return view
        return f'{obj_module}.{view}'

    def view_attribute_annotation_definition(self, attribute_annotation_def: AttributeAnnotationDef):
        return f'{attribute_annotation_def.name}: {self.view(representation=attribute_annotation_def.annotation)}\n'

    def view_attribute_definition(self, attribute_def: AttributeDef):
        return f'{attribute_def.name} = {self.view(attribute_def.value)}\n'

    def view_class_definition(self, class_def: ClassDef):
        sio = StringIO()

        if class_def.node.obj.__bases__ == (object,):
            sio.write(f'class {class_def.name}:\n')
        else:
            bases = ', '.join(self.view(base) for base in class_def.bases)
            sio.write(f'class {class_def.name}({bases}):\n')

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

        with StubViewer.ModuleContext(module_def, self):
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

            # traverse to get actually needed objects
            used_object_ids = set()
            for representation in module_def:
                if representation.name != '__all__' and representation.name not in module_def.obj.__all__:
                    continue

                used_object_ids.add(representation.id)
                for child_rep in representation.traverse():
                    used_object_ids.add(child_rep.id)

            # imports

            imports, from_imports = module_def.get_imports(used_object_ids)

            if imports:
                for name in sorted(imports):
                    sio.write(f'import {name}\n')
                sio.write('\n')

            if from_imports:
                for key in sorted(from_imports.keys()):
                    if len(from_imports[key]) > 1:
                        names = ',\n'.join(
                            indent(f'{name} as {import_as}' if import_as else f'{name}')
                            for name, import_as in sorted(from_imports[key], key=lambda x: x[0])
                        )
                        sio.write(f'from {key} import (\n{names}\n)\n')
                    else:
                        names = ', '.join(
                            f'{name} as {import_as}' if import_as else name for name, import_as in from_imports[key])
                        sio.write(f'from {key} import {names}\n')

            if imports or from_imports:
                sio.write('\n')

            # module members
            if module_def.members:
                for representation in module_def:
                    if representation.id in used_object_ids:
                        sio.write(self.view(representation))
                        sio.write('\n')

        return sio.getvalue().rstrip('\n') + '\n'

    def view_class_method_definition(self, class_method_definition: ClassMethodDef):
        return f'@classmethod\n{self.view_function_definition(class_method_definition)}'

    def view_static_method_definition(self, static_method_definition: StaticMethodDef):
        return f'@staticmethod\n{self.view_function_definition(static_method_definition)}'
