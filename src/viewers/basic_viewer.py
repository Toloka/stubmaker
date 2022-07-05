__all__ = [
    'BasicViewer',
]

import enum
import inspect
from typing import ForwardRef

from stubmaker.builder.common import BaseRepresentation, BaseDefinition
from stubmaker.builder.definitions import (
    AttributeAnnotationDef,
    AttributeDef,
    BaseClassDef,
    ClassDef,
    MetaclassDef,
    DocumentationDef,
    EnumDef,
    FunctionDef,
    ModuleDef,
)
from stubmaker.builder.literals import (
    EnumValueLiteral,
    ReferenceLiteral,
    TypeHintLiteral,
    TypeVarLiteral,
    ValueLiteral,
)
from stubmaker.viewers.common import ViewerBase, add_inherited_singledispatchmethod
from stubmaker.viewers.util import get_common_namespace_prefix


@add_inherited_singledispatchmethod(method_name='iter_over', implementation_prefix='iter_over_')
@add_inherited_singledispatchmethod(method_name='view', implementation_prefix='view_')
class BasicViewer(ViewerBase):

    def view(self, representation: BaseRepresentation):
        raise ValueError(f'Unknown representation type: {type(representation)}')

    def view_attribute_annotation_definition(self, attribute_annotation_def: AttributeAnnotationDef):
        raise NotImplementedError

    def view_attribute_definition(self, attribute_def: AttributeDef):
        raise NotImplementedError

    def view_base_class_definition(self, class_def: BaseClassDef):
        raise NotImplementedError

    def view_documentation_definition(self, documentation_def: DocumentationDef):
        raise NotImplementedError

    def view_enum_definition(self, enum_def: EnumDef):
        raise NotImplementedError

    def view_function_definition(self, function_def: FunctionDef):
        raise NotImplementedError

    def view_module_definition(self, module_def: ModuleDef):
        raise NotImplementedError

    def view_reference_literal(self, reference_lit: ReferenceLiteral):
        if inspect.isclass(reference_lit.obj) or inspect.isfunction(reference_lit.obj):
            qualname = reference_lit.qualname
            prefix = get_common_namespace_prefix(reference_lit.namespace, qualname[:qualname.rfind('.')])
            return qualname[len(prefix):]
        return getattr(reference_lit.obj, '__name__', None) or reference_lit.obj._name

    def view_type_hint_literal(self, type_hint_lit: TypeHintLiteral):
        if type_hint_lit.type_hint_args:
            args = ', '.join(self.view(arg) for arg in type_hint_lit.type_hint_args)
            return f'{self.view(type_hint_lit.type_hint_origin)}[{args}]'

        return self.view(type_hint_lit.type_hint_origin)

    def view_type_var_literal(self, type_var_lit: TypeVarLiteral):
        covariant_str = ', covariant=True' if self.view(type_var_lit.covariant) == 'True' else ''
        contravariant_str = ', contravariant=True' if self.view(type_var_lit.contravariant) == 'True' else ''
        if type_var_lit.bound.obj is not None:
            bound_str = self.view(type_var_lit.bound)
            return f'{self.view(type_var_lit.type_var_reference)}({self.view(type_var_lit.type_var_name)}{covariant_str}{contravariant_str}, bound={bound_str})'
        return f'{self.view(type_var_lit.type_var_reference)}({self.view(type_var_lit.type_var_name)}{covariant_str}{contravariant_str})'

    def view_value_literal(self, value_lit: ValueLiteral):
        if value_lit.obj is None:
            return 'None'

        if isinstance(value_lit.obj, enum.Enum):
            return

        if isinstance(value_lit.obj, (int, str, bool, float)):
            return repr(value_lit.obj)

        if isinstance(value_lit.obj, list) and all(isinstance(obj, BaseRepresentation) for obj in value_lit.obj):
            return f'[{", ".join(self.view(obj) for obj in value_lit.obj)}]'

        if isinstance(value_lit.obj, ForwardRef):
            return repr(value_lit.obj.__forward_arg__)

        return '...'

    def view_enum_value_literal(self, enum_value_lit: EnumValueLiteral):
        return f'{self.view(enum_value_lit.enum_class)}.{enum_value_lit.obj._name_}'

    def iter_over(self, representation: BaseRepresentation):
        raise ValueError(f'Unknown representation type: {type(representation)}')

    def iter_over_attribute_annotation_definition(self, attribute_annotation_def: AttributeAnnotationDef):
        yield attribute_annotation_def.annotation

    def iter_over_attribute_definition(self, attribute_def: AttributeDef):
        yield attribute_def.value

    def iter_over_class_definition(self, class_def: ClassDef):
        if class_def.docstring:
            yield class_def.docstring

        yield class_def.metaclass
        yield from class_def.bases
        yield from class_def.members.values()
        yield from class_def.annotations.values()

    def iter_over_metaclass_definition(self, metaclass_def: MetaclassDef):
        yield from self.iter_over_class_definition(metaclass_def)

    def iter_over_documentation_definition(self, documentation_def: DocumentationDef):
        yield from ()

    def iter_over_enum_definition(self, enum_def: EnumDef):
        yield from enum_def.bases
        yield from enum_def.enum_dict.values()

    def iter_over_function_definition(self, function_def: FunctionDef):
        if function_def.docstring:
            yield function_def.docstring

        for param in function_def.signature.parameters.values():
            if param.annotation is not inspect.Parameter.empty:
                yield param.annotation
            if param.default is not inspect.Parameter.empty:
                yield param.default

        if function_def.signature.return_annotation is not inspect.Parameter.empty:
            yield function_def.signature.return_annotation

    def iter_over_module_definition(self, module_def: ModuleDef):
        if module_def.docstring:
            yield module_def.docstring

        yield from module_def.members.values()

    def iter_over_reference_literal(self, reference_lit: ReferenceLiteral):
        yield from ()

    def iter_over_type_hint_literal(self, type_hint_lit: TypeHintLiteral):
        yield type_hint_lit.type_hint_origin
        yield from type_hint_lit.type_hint_args

    def iter_over_type_var_literal(self, type_var_lit: TypeVarLiteral):
        yield type_var_lit.origin
        yield type_var_lit.type_var_name
        yield type_var_lit.covariant
        yield type_var_lit.contravariant
        yield type_var_lit.bound

    def iter_over_value_literal(self, value_lit: ValueLiteral):
        if isinstance(value_lit.obj, list):
            yield from (nested_obj for nested_obj in value_lit.obj if isinstance(nested_obj, BaseRepresentation))

    def iter_over_enum_value_literal(self, enum_value_lit: EnumValueLiteral):
        yield enum_value_lit.enum_class

    def get_subtree_ids(self, root_representation: BaseRepresentation):
        ids = set()
        for child in self.traverse(root_representation):
            ids.add(child.id)
        return ids

    def get_used_members_ids(self, module_def):
        # traverse to get actually used representations
        used_object_ids = set()
        for representation in self.iter_over(module_def):
            if representation.name != '__all__' and representation.name not in module_def.obj.__all__:
                continue

            used_object_ids.update(self.get_subtree_ids(representation))

        # traverse one more time to add representations that have nested definitions that are used by used
        # representations.
        for representation in self.iter_over(module_def):
            for child_rep in self.traverse(representation):
                if isinstance(child_rep, BaseDefinition) and child_rep.id in used_object_ids:
                    used_object_ids.update(self.get_subtree_ids(representation))
                    break

        return used_object_ids
