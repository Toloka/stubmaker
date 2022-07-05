"""Module for testing module aliases functionality.
"""

__all__ = [
    'attribute',
]
import test_package.hidden_module_proxy


attribute: test_package.hidden_module_proxy.HiddenClass
