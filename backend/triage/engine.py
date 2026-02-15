# -*- coding: utf-8 -*-
"""
Motor de decisão – Avalia sintomas positivos e retorna nível + conduta.
Não diagnostica. Não prescreve. Apenas aplica regras.
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from backend.triage.escalation import get_conduta
from backend.triage.logger import log_evaluation

_BASE = Path(__file__).resolve().parent

# Ordem de gravidade (maior índice = mais grave)
_GRAVIDADE_ORDEM = {"monitoramento": 0, "alerta": 1, "critico": 2}


def _load_yaml(name: str) -> dict:
    path = _BASE / name
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _build_sintoma_by_id() -> Dict[str, dict]:
    data = _load_yaml("symptoms.yaml")
    return {s["id"]: s for s in data.get("sintomas", [])}


def _get_nivel_by_sintoma() -> Dict[str, str]:
    """Lê base_rules diretamente (mapeamento já pronto)."""
    data = _load_yaml("rules.yaml")
    return dict(data.get("base_rules", {}))


def _get_combinacoes() -> List[dict]:
    data = _load_yaml("rules.yaml")
    return data.get("combinacoes", [])


def _get_versao_regra() -> str:
    data = _load_yaml("rules.yaml")
    return str(data.get("versao", "0.0.0"))


def _mais_grave(a: str, b: str) -> str:
    """Retorna o nível mais grave entre a e b."""
    ga = _GRAVIDADE_ORDEM.get(a, -1)
    gb = _GRAVIDADE_ORDEM.get(b, -1)
    return a if ga >= gb else b


def evaluate(
    sintomas_positivos: List[str],
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Avalia a lista de sintomas positivos (ids) e retorna nível + conduta.

    Args:
        sintomas_positivos: Lista de ids de sintomas que o usuário afirmou ter.
        user_id: Id do usuário para auditoria.

    Returns:
        {
            "nivel": "critico" | "alerta" | "monitoramento",
            "regra_aplicada": "combinacao" | "individual",
            "conduta": {...},
            "sintomas_avaliados": [...],
            "versao_regra": "1.0.0",
            "timestamp": "2025-02-14T12:00:00Z",
        }
    """
    raw = [s.strip() for s in sintomas_positivos if s and str(s).strip()]
    nivel_by_sintoma = _get_nivel_by_sintoma()
    sintoma_by_id = _build_sintoma_by_id()
    combinacoes = _get_combinacoes()
    versao = _get_versao_regra()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Filtrar sintomas mapeados; logar warning para inexistentes (evita inconsistência futura)
    set_positivos = set()
    nao_mapeados = []
    for sid in raw:
        if sid in nivel_by_sintoma:
            set_positivos.add(sid)
        else:
            nao_mapeados.append(sid)
    if nao_mapeados:
        import logging
        logging.getLogger("sophia.triage").warning(
            "[TRIAGE] Sintoma(s) não mapeado(s), ignorado(s): %s", nao_mapeados
        )

    nivel_final = "monitoramento"
    regra_aplicada = "individual"
    detalhe = None
    template_hint = None

    # 1. Avaliar TODAS as combinações aplicáveis; manter o nível mais grave
    for combo in combinacoes:
        req = set(combo.get("sintomas", []))
        if req and req.issubset(set_positivos):
            nivel_combo = combo.get("nivel", "monitoramento")
            nivel_final = _mais_grave(nivel_final, nivel_combo)
            regra_aplicada = "combinacao"
            detalhe = combo.get("motivo", "")
            hint = combo.get("template_hint")
            if hint:
                template_hint = hint

    # 2. Se nenhuma combinação, usa o nível mais grave entre os individuais
    if regra_aplicada == "individual" and set_positivos:
        for sid in set_positivos:
            n = nivel_by_sintoma.get(sid)
            if n:
                nivel_final = _mais_grave(nivel_final, n)

    # 3. Obter conduta (escalation usa apenas nivel + template_hint)
    conduta = get_conduta(nivel_final, template_hint=template_hint)

    # 4. Enriquecer com sinais de piora (lógica no motor, não na camada de conduta)
    if nivel_final == "monitoramento":
        for sid in set_positivos:
            s = sintoma_by_id.get(sid, {})
            sinais = s.get("sinais_piora") if s else None
            if sinais:
                txt = " Se notar " + ", ".join(sinais) + ", procure avaliação."
                conduta = dict(conduta)
                conduta["descricao"] = (conduta.get("descricao", "") or "").rstrip(". ") + txt
                break

    # 5. Auditoria
    log_evaluation(
        sintomas_positivos=sorted(set_positivos),
        nivel=nivel_final,
        regra_aplicada=regra_aplicada,
        detalhe=detalhe,
        user_id=user_id,
    )

    return {
        "nivel": nivel_final,
        "regra_aplicada": regra_aplicada,
        "conduta": conduta,
        "template_hint": template_hint,
        "sintomas_avaliados": sorted(set_positivos),
        "versao_regra": versao,
        "timestamp": now,
    }


def payload_para_chat(resultado: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai APENAS o payload seguro para o chat.
    O chat NUNCA deve receber sintomas (evita interpretação paralela).

    Returns:
        { "nivel", "conduta", "template_hint" }  # template_hint pode ser None
    """
    return {
        "nivel": resultado.get("nivel", "monitoramento"),
        "conduta": dict(resultado.get("conduta", {})),
        "template_hint": resultado.get("template_hint"),
    }


def list_sintomas() -> List[Dict[str, Any]]:
    """Retorna lista de sintomas com nível para uso na UI."""
    data = _load_yaml("symptoms.yaml")
    nivel_by_sintoma = _get_nivel_by_sintoma()
    out = []
    for s in data.get("sintomas", []):
        sid = s.get("id", "")
        row = dict(s)
        row["nivel"] = nivel_by_sintoma.get(sid, "monitoramento")
        out.append(row)
    return out
