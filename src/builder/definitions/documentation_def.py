import docstring_parser

from stubmaker.builder.common import BaseDefinition


class DocumentationDef(BaseDefinition):

    def get_parsed(self):
        return docstring_parser.google.parse(self.obj)
