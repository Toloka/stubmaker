from contextvars import ContextVar
from types import ModuleType
from test_package import ClassWithRedefinedModule

DESCRIBED_OBJECTS = {
    ModuleType: ('types', 'ModuleType'),
    ClassWithRedefinedModule: ('test_package', 'ClassWithRedefinedModule'),
    ContextVar: ('contextvars', 'ContextVar'),
}