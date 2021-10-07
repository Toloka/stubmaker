__all__ = [
    'wrap_function_signature',
    'indent',
    'replace_representations_in_signature',
    'get_common_namespace_prefix',
]
import inspect
import textwrap

from itertools import zip_longest
from typing import List, Tuple


def _split_str_signature_by_params(signature: inspect.Signature) -> Tuple[str, List[str], str]:
    signature_str = str(signature)
    params_str = []
    last_param_end = 0
    prefix = ''

    for param_str in signature.parameters.values():
        param_str = str(param_str)
        param_start = signature_str.find(param_str, last_param_end)
        current_prefix = signature_str[last_param_end:param_start]
        last_param_end = param_start + len(param_str)

        if '*' in current_prefix:
            params_str.append('*')
        elif '/' in current_prefix:
            params_str.append('/')
        elif '(' in current_prefix:
            prefix = current_prefix

        params_str.append(param_str)

    postfix = signature_str[last_param_end:]

    return prefix, params_str, postfix


def wrap_function_signature(
    signature: inspect.Signature,
    max_args_on_line: int = 1,
    min_args_to_wrap: int = 2,
    wrap_self: bool = True
) -> str:
    if len(signature.parameters) <= min_args_to_wrap:
        return str(signature)

    prefix, params_str, postfix = _split_str_signature_by_params(signature)

    if 'self' not in signature.parameters:
        wrap_self = False

    wrapped_params_str = []

    start_from = 0
    if wrap_self and next(iter(signature.parameters), '') == 'self':
        prefix = prefix + '\n'
        wrapped_params_str.append(params_str[0])
        start_from = 1

    for line_start in range(start_from, len(params_str), max_args_on_line):
        new_line = '\n' + ', '.join(params_str[line_start:line_start + max_args_on_line])
        wrapped_params_str.append(new_line)

    return f'{prefix}{indent(",".join(wrapped_params_str))}\n{postfix}'


def indent(string: str, level: int = 1, tabulation: str = ' ' * 4) -> str:
    return textwrap.indent(string, tabulation * level)


def get_view_adapter(representation, viewer):
    class Adapter(type(representation)):
        def __init__(self, wrapped_obj):
            self.wrapped_obj = wrapped_obj

        def __getattr__(self, item):
            return getattr(self.wrapped_obj, item)

        def __str__(self):
            return viewer.view(self.wrapped_obj)

        __repr__ = __str__

    return Adapter(representation)


def replace_representations_in_signature(signature: inspect.Signature, viewer):
    parameters = []
    for parameter in signature.parameters.values():
        if parameter.annotation is not inspect.Parameter.empty:
            parameter = parameter.replace(annotation=get_view_adapter(parameter.annotation, viewer))
        if parameter.default is not inspect.Parameter.empty:
            parameter = parameter.replace(default=get_view_adapter(parameter.default, viewer))
        parameters.append(parameter)

    return_annotation = signature.return_annotation
    if signature.return_annotation is not inspect.Parameter.empty:
        return_annotation = get_view_adapter(return_annotation, viewer)

    return signature.replace(parameters=parameters, return_annotation=return_annotation)


def get_common_namespace_prefix(first_namespace, second_namespace):
    first_namespace = first_namespace.split('.')
    second_namespace = second_namespace.split('.')
    common_tokens = []
    for first_token, second_token in zip_longest(first_namespace, second_namespace):
        if first_token != second_token:
            break
        common_tokens.append(first_token)
    return '.'.join([*common_tokens, ''])
