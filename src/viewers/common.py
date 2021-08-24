__all__ = [
    'ViewerBase',
    'add_inherited_singledispatchmethod',
]
import functools
import inspect

from stubmaker.builder.common import BaseRepresentation


def singledispatchmethod(func):
    dispatcher = functools.singledispatch(func)
    signature = inspect.signature(func)

    def wrapper(*args, **kwargs):
        dispatch_type = signature.bind(*args, **kwargs).args[1].__class__
        return dispatcher.dispatch(dispatch_type)(*args, **kwargs)

    wrapper.register = dispatcher.register
    wrapper.registry = dispatcher.registry
    functools.update_wrapper(wrapper, func)
    return wrapper


def add_inherited_singledispatchmethod(method_name, implementation_prefix):
    """Class decorator used to make overloaded method with inheritance support

    Using this decorator modifies class in two ways:
        * method_name method is decorated with singledispatchmethod
        * for every method with name starting with implementation_prefix proxy method is created and registered as
    implementation of method_name. Proxy method is used to call the method implementation in current subclass.
    Decorator can be used in subclasses of class that already use this decorator to update (overwrite)
    method_name registry.

    Args:
         method_name: method_name to be used as dispatcher
         implementation_prefix: every method with such prefix will be registered as implementation of mathod_name
    """

    def wrapper(cls):
        setattr(cls, method_name, singledispatchmethod(getattr(cls, method_name)))

        for member_name in dir(cls):
            if member_name == method_name:
                continue
            member = getattr(cls, member_name)
            if inspect.isfunction(member) and member_name.startswith(implementation_prefix):
                annotation = list(inspect.signature(member).parameters.values())[1].annotation

                def proxy(self, representation: annotation, mapped_member_name=member_name):
                    return getattr(self, mapped_member_name)(representation)

                getattr(cls, method_name).register(annotation, proxy)
        return cls

    return wrapper


class ViewerBase:
    def view(self, representation: BaseRepresentation):
        raise NotImplementedError
