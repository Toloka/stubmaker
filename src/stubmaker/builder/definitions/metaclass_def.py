from .base_class_def import BaseClassDef


class MetaclassDef(BaseClassDef):
    def _is_redefined_in_current_class(self, name):
        cls_attr = getattr(self.obj, name)
        super_cls = super(self.obj, self.obj)
        super_cls_attr = getattr(super_cls, name, None)
        # check if function descriptor is actually redefined (i.e. classmethods and staticmethods)
        if hasattr(cls_attr, '__func__') and hasattr(super_cls_attr, '__func__'):
            return getattr(cls_attr, '__func__') != getattr(super_cls_attr, '__func__')
        return cls_attr is not super_cls_attr
