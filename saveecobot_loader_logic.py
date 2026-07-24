# -*- coding: utf-8 -*-
"""Helpers for executing the SaveEcoBot loader workflow."""

from .apikey_loader_impl import run_apikey_loader
from .saveecobot_loader_impl import run_saveecobot_loader


def resolve_loader_handler(result):
    """Return the loader handler for a dialog result value."""
    if result in (True, 1):
        return run_saveecobot_loader
    if result == 2:
        return run_apikey_loader
    return None


def execute_loader_action(result, plugin):
    """Dispatch the saved dialog result to the appropriate loader workflow."""
    handler = resolve_loader_handler(result)
    if handler is None:
        return None
    return handler(plugin)
