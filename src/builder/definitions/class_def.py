from .base_class_def import BaseClassDef


class ClassDef(BaseClassDef):
    def get_public_member_names(self):
        yield from (name for name in super().get_public_member_names() if not name.startswith('_') or name == '__init__')
