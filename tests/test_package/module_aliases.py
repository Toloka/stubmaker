"""Module for testing module aliases functionality."""
__all__ = [
    'attribute'
]
from .hidden_module_proxy import HiddenClass

attribute: HiddenClass
