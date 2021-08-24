from stubmaker.builder.common import BaseLiteral


class ReferenceLiteral(BaseLiteral):

    def __iter__(self):
        yield from ()
