import inspect
import logging
import sys
from typing import Optional, get_type_hints

from stubmaker.builder.common import BaseDefinition, Node, BaseRepresentationsTreeBuilder


logger = logging.getLogger(__file__)


class FunctionDef(BaseDefinition):
    def __init__(self, node: Node, tree: BaseRepresentationsTreeBuilder):
        super().__init__(node, tree)

        signature = inspect.signature(self.obj)
        if not tree.preserve_forward_references:
            module = sys.modules.get(self.obj.__module__)
            try:
                globalns = None if module is None else module.__dict__
                annotations = get_type_hints(self.obj, globalns)
            except (NameError, TypeError) as exc:
                logger.warning(f'Failed to evaluate forward reference for {self.obj}: {exc}')
                annotations = self.obj.__annotations__

        params = []
        for param in signature.parameters.values():
            if param.annotation is not inspect.Parameter.empty:
                annotation = (
                    param.annotation
                    if tree.preserve_forward_references
                    else annotations.get(param.name, param.annotation)
                )
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
            annotation = (
                return_annotation if tree.preserve_forward_references else annotations.get('return', return_annotation)
            )
            return_annotation = tree.get_literal(self.tree.create_node_for_object(self.namespace, None, annotation))

        self.signature = signature.replace(parameters=params, return_annotation=return_annotation)
        self.is_async = inspect.iscoroutinefunction(self.obj)

    def get_parameter(self, arg_name: str) -> Optional[inspect.Parameter]:
        return self.signature.parameters.get(arg_name)


class ClassMethodDef(FunctionDef):
    pass


class StaticMethodDef(FunctionDef):
    pass
