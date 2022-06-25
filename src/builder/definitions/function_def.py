import inspect
import sys
from typing import get_type_hints

from stubmaker.builder.common import BaseDefinition, Node, BaseRepresentationsTreeBuilder


class FunctionDef(BaseDefinition):

    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)

        signature = inspect.signature(self.obj)
        if not tree.preserve_forward_references:
            try:
                module = sys.modules.get(self.obj.__module__)
                annotations = get_type_hints(self.obj, module and module.__dict__)
            except NameError as exc:
                raise RuntimeError(f'Failed to evaluate forward reference for {self.obj}') from exc

        params = []
        for param in signature.parameters.values():
            if param.annotation is not inspect.Parameter.empty:
                annotation = param.annotation if tree.preserve_forward_references else annotations[param.name]
                param = param.replace(
                    annotation=tree.get_literal(self.tree.create_node_for_object(self.namespace, None, annotation))
                )
            if param.default is not inspect.Parameter.empty:
                param = param.replace(
                    default=tree.get_literal(self.tree.create_node_for_object(self.namespace, None, param.default))
                )
            params.append(param)

        return_annotation = signature.return_annotation
        if return_annotation is not inspect.Parameter.empty:
            annotation = return_annotation if tree.preserve_forward_references else annotations['return']
            return_annotation = tree.get_literal(self.tree.create_node_for_object(self.namespace, None, annotation))

        self.signature = signature.replace(parameters=params, return_annotation=return_annotation)

    def get_parameter(self, arg_name: str) -> inspect.Parameter:
        return self.signature.parameters.get(arg_name)


class ClassMethodDef(FunctionDef):
    pass


class StaticMethodDef(FunctionDef):
    pass
