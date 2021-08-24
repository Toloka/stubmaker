from stubmaker.builder.common import BaseLiteral, BaseRepresentation


class ValueLiteral(BaseLiteral):

    def __iter__(self):
        if isinstance(self.obj, list):
            yield from (nested_obj for nested_obj in self.obj if isinstance(nested_obj, BaseRepresentation))
