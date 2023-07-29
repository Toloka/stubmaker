import inspect

from .base_class_def import BaseClassDef


class ClassDef(BaseClassDef):
    def get_public_member_names(self):
        yield from (
            name
            for name in super().get_public_member_names()
            if not name.startswith('_') or name.startswith('__') and name.endswith('__')
        )

    def _is_redefined_in_current_class(self, name):
        if self.tree.always_include_init and name == '__init__':
            return True

        cls_attr = getattr(self.obj, name)
        super_cls = super(self.obj, self.obj)
        super_cls_attr = getattr(super_cls, name, None)
        # check if function descriptor is actually redefined (i.e. classmethods and staticmethods)
        if hasattr(cls_attr, '__func__') and hasattr(super_cls_attr, '__func__'):
            cls_attr = getattr(cls_attr, '__func__')
            super_cls_attr = getattr(super_cls_attr, '__func__')
        return not self._are_almost_same(cls_attr, super_cls_attr)

    def _are_almost_same(self, left, right):
        if callable(left) and callable(right):
            if left.__name__ != right.__name__:
                return False
            # less strict ad-hoc check in case of magic methods (except for __init__)
            if left.__name__.startswith('__') and left.__name__.endswith('__') and left.__name__ != '__init__':
                try:
                    left_signature = inspect.signature(left)
                    right_signature = inspect.signature(right)
                except ValueError:
                    # skip builtin methods without signature
                    return True
                else:
                    if getattr(left, '__isabstractmethod__', False) != getattr(right, '__isabstractmethod__', False):
                        return False

                    left_params_descriptor = [
                        (param.annotation, param.default) for param_name, param in left_signature.parameters.items()
                    ]
                    right_params_descriptor = [
                        (param.annotation, param.default) for param_name, param in right_signature.parameters.items()
                    ]
                    if (
                        left_params_descriptor == right_params_descriptor
                        and left_signature.return_annotation == right_signature.return_annotation
                    ):
                        return True
        return left is right
