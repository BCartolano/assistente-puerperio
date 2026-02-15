# -*- coding: utf-8 -*-
"""
Triage – Motor de decisão para escalonamento de sintomas.
Separação: Dados | Regras | Motor | Escalonamento | Auditoria.
"""
from backend.triage.engine import evaluate, list_sintomas, payload_para_chat
from backend.triage.escalation import get_conduta, NIVEL_LABELS

__all__ = [
    "evaluate",
    "list_sintomas",
    "payload_para_chat",
    "get_conduta",
    "NIVEL_LABELS",
]
