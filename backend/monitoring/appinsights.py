# -*- coding: utf-8 -*-
import logging
import os
import json
from typing import Optional


def init_appinsights(app) -> Optional[logging.Handler]:
    """
    Liga export de logs para Azure Application Insights se APPINSIGHTS_CONNECTION_STRING estiver no ambiente.
    Falha silenciosa se biblioteca não estiver instalada.
    """
    conn = os.environ.get("APPINSIGHTS_CONNECTION_STRING")
    if not conn:
        return None
    try:
        from opencensus.ext.azure.log_exporter import AzureLogHandler
    except Exception:
        try:
            app.logger.warning("[AI] opencensus-ext-azure ausente; skip monitoramento")
        except Exception:
            pass
        return None
    handler = AzureLogHandler(connection_string=conn)
    handler.setLevel(logging.INFO)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    try:
        app.logger.info("[AI] Application Insights: ON")
    except Exception:
        pass
    return handler


def log_emergency_search(props: dict):
    """
    Eventos de busca de hospitais (0094):
    props recomendados: count, source, mtime, lat, lon, radius_km, ttl_remaining (se houver)
    """
    try:
        msg = "emergency_search " + json.dumps(props, ensure_ascii=False)
        logging.getLogger().info(msg)
    except Exception:
        pass
