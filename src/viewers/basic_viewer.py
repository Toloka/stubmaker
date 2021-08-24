__all__ = [
    'BasicViewer',
]

import enum
import inspect

from itertools import zip_longest
from typing import ForwardRef

from stubmaker.viewers.common import ViewerBase, add_inherited_singledispatchmethod
from stubmaker.builder.common import BaseRepresentation
from stubmaker.builder.definitions import (
    AttributeAnnotationDef,
    AttributeDef,
    ClassDef,
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


@add_inherited_singledispatchmethod(method_name='view', implementation_prefix='view_')
class BasicViewer(ViewerBase):

    def view(self, representation: BaseRepresentation):
        raise ValueError(f'Unknown representation type: {type(representation)}')

    def view_attribute_annotation_definition(self, attribute_annotation_def: AttributeAnnotationDef):
        raise NotImplementedError

    def view_attribute_definition(self, attribute_def: AttributeDef):
        raise NotImplementedError

    def view_class_definition(self, class_def: ClassDef):
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
            i = 0
            namespace_tokens = reference_lit.namespace.split('.')
            qualname_tokens = reference_lit.obj.__qualname__.split('.')

            for i, (namespace_token, qualname_token) in enumerate(zip_longest(namespace_tokens, qualname_tokens)):
                if namespace_token != qualname_token:
                    break
            return '.'.join(qualname_tokens[i:])

        return getattr(reference_lit.obj, '__name__', None) or reference_lit.obj._name

    def view_type_hint_literal(self, type_hint_lit: TypeHintLiteral):
        if type_hint_lit.type_hint_args:
            args = ', '.join(self.view(arg) for arg in type_hint_lit.type_hint_args)
            return f'{self.view(type_hint_lit.type_hint_origin)}[{args}]'

        return self.view(type_hint_lit.type_hint_origin)

    def view_type_var_literal(self, type_var_lit: TypeVarLiteral):
        covariant_str = ', covariant=True' if self.view(type_var_lit.covariant) == 'True' else ''
        contravariant_str = ', contravariant=True' if self.view(type_var_lit.contravariant) == 'True' else ''
        bound_str = self.view(type_var_lit.bound)
        return f'{self.view(type_var_lit.type_var_reference)}({self.view(type_var_lit.type_var_name)}{covariant_str}{contravariant_str}, bound={bound_str})'

    def view_value_literal(self, value_lit: ValueLiteral):
        if value_lit.obj is None:
            return 'None'

        if isinstance(value_lit.obj, enum.Enum):
            return

        if isinstance(value_lit.obj, (int, str, bool)):
            return repr(value_lit.obj)

        if isinstance(value_lit.obj, list) and all(isinstance(obj, BaseRepresentation) for obj in value_lit.obj):
            return f'[{", ".join(self.view(obj) for obj in value_lit.obj)}]'

        if isinstance(value_lit.obj, ForwardRef):
            return repr(value_lit.obj.__forward_arg__)

        return '...'

    def view_enum_value_literal(self, enum_value_lit: EnumValueLiteral):
        return f'{self.view(enum_value_lit.enum_class)}.{enum_value_lit.obj._name_}'
