import re
import docstring_parser

from stubmaker.builder.common import BaseDefinition, URL_REGEXP


class DocumentationDef(BaseDefinition):

    def __iter__(self):
        yield from ()

    def get_parsed(self):
        parsed = docstring_parser.google.parse(self.obj)
        # show links as real links
        if parsed.short_description:
            parsed.short_description = re.sub(URL_REGEXP, r'[\g<0>](\g<0>)', parsed.short_description)
        if parsed.long_description:
            parsed.long_description = re.sub(URL_REGEXP, r'[\g<0>](\g<0>)', parsed.long_description)
        return parsed
