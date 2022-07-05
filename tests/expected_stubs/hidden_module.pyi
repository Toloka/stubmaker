"""Module for emulating modules that shouldn't be accessed in stubs directly but instead proxy modules should be used.
This module is supposed to be used via hidden_module_proxy.py in stubs
"""

__all__ = [
    'HiddenClass',
]
from test_package.hidden_module_proxy import HiddenClass
