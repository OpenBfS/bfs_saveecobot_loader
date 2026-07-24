# -*- coding: utf-8 -*-
"""API key-based loader implementation placeholder."""


def run_apikey_loader(plugin):
    """Placeholder for future API key workflow implementation."""
    from qgis.core import Qgis

    plugin.iface.messageBar().pushMessage(
        'SaveEcoBot loader',
        'API key loader workflow is not implemented yet.',
        level=Qgis.MessageLevel.Info,
    )
    return None
