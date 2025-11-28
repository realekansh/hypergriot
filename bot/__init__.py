"""
HyperGriot bot package

This module exposes `create_client()` or other bootstrapping helpers later.
For now it provides a simple registry object used by handlers.
"""
from .commands import registry
__all__ = ["registry"]
