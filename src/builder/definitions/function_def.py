import inspect

from stubmaker.builder.common import BaseDefinition, Node, BaseASTBuilder


class FunctionDef(BaseDefinition):

    # TODO: support statimethods and classmethods

    def __init__(self, node: Node, ast: BaseASTBuilder):
        super().__init__(node, ast)

        signature = inspect.signature(self.obj)

        params = []
        for param in signature.parameters.values():
            if param.annotation is not inspect.Parameter.empty:
                param = param.replace(annotation=ast.get_literal(Node(self.namespace, None, param.annotation)))
            if param.default is not inspect.Parameter.empty:
                param = param.replace(default=ast.get_literal(Node(self.name, None, param.default)))
            params.append(param)

        return_annotation = signature.return_annotation
        if return_annotation is not inspect.Parameter.empty:
            return_annotation = ast.get_literal(Node(self.namespace, None, return_annotation))

        self.signature = signature.replace(parameters=params, return_annotation=return_annotation)
        self.docstring = ast.get_docstring(node)

    def __iter__(self):
        if self.docstring:
            yield self.docstring

        for param in self.signature.parameters.values():
            if param.annotation is not inspect.Parameter.empty:
                yield param.annotation
            if param.default is not inspect.Parameter.empty:
                yield param.default

        if self.signature.return_annotation is not inspect.Parameter.empty:
            yield self.signature.return_annotation

    def get_parameter(self, arg_name: str) -> inspect.Parameter:
        return self.signature.parameters.get(arg_name)


class ClassMethodDef(FunctionDef):
    pass


class StaticMethodDef(FunctionDef):
    pass
