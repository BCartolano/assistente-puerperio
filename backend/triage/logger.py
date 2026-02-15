# -*- coding: utf-8 -*-
"""
Triage logger – Auditoria de decisões.
Registra avaliações para rastreabilidade e conformidade.
"""
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("sophia.triage")


def log_evaluation(
    sintomas_positivos: list,
    nivel: str,
    regra_aplicada: str,
    detalhe: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """Registra uma avaliação de triagem para auditoria."""
    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "sintomas": sintomas_positivos,
        "nivel": nivel,
        "regra": regra_aplicada,
    }
    if detalhe:
        payload["detalhe"] = detalhe
    if user_id:
        payload["user_id"] = str(user_id)

    logger.info(
        "[TRIAGE] Avaliação: nivel=%s regra=%s sintomas=%s",
        nivel,
        regra_aplicada,
        sintomas_positivos,
        extra=payload,
    )
