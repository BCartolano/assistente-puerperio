# -*- coding: utf-8 -*-
"""
Escalonamento – Mapeamento nível + template_hint → conduta (texto + ações).
Não diagnostica. Não prescreve. Apenas orienta.

REGRA: Usa APENAS nivel e template_hint. Nunca sintomas ou ids.
Evita regras paralelas.
"""
from typing import Any, Dict, Optional

# Labels para o usuário
NIVEL_LABELS = {
    "critico": "Atenção imediata",
    "alerta": "Avaliar em até 24h",
    "monitoramento": "Observar e acompanhar",
}

# Condutas por nível
CONDUTAS = {
    "critico": {
        "titulo": "Procure atendimento de emergência",
        "descricao": "Com base no que você relatou, recomenda-se avaliação médica imediata. "
        "Se não puder ir sozinha, ligue 192.",
        "acoes": [
            {"tipo": "telefone", "numero": "192", "texto": "Ligar SAMU (192)"},
            {"tipo": "hospital", "texto": "Ver unidades próximas"},
        ],
    },
    "alerta": {
        "titulo": "Recomenda-se avaliação em até 24 horas",
        "descricao": "Com base no que você relatou, é importante ser avaliada por um profissional de saúde "
        "nas próximas 24 horas. UPA, posto de saúde ou consulta médica são opções.",
        "acoes": [
            {"tipo": "hospital", "texto": "Ver unidades próximas"},
        ],
    },
    "monitoramento": {
        "titulo": "Você pode observar em casa",
        "descricao": "Com base no que você relatou, você pode observar em casa. "
        "Descanse, hidrate-se e monitore. Se notar piora ou outros sinais, procure avaliação.",
        "acoes": [],
    },
}

# Conduta quando template_hint=saude_mental e nivel=critico (CVV em vez de 192)
CONDUTA_SAUDE_MENTAL = {
    "titulo": "Procure apoio emocional",
    "descricao": "Você não está sozinha. O CVV (188) pode te ouvir 24 horas, gratuitamente e com sigilo. "
    "Recomenda-se também avaliação com profissional de saúde mental nas próximas 24–48 horas.",
    "acoes": [
        {"tipo": "telefone", "numero": "188", "texto": "Ligar CVV (188)"},
        {"tipo": "hospital", "texto": "Ver unidades próximas"},
    ],
}


def get_conduta(nivel: str, template_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Retorna a conduta para o nível dado.
    Usa APENAS nivel e template_hint. Nunca sintomas.

    Args:
        nivel: critico | alerta | monitoramento
        template_hint: ex. "saude_mental" → usa conduta CVV quando nivel=critico
    """
    if template_hint == "saude_mental" and nivel == "critico":
        out = dict(CONDUTA_SAUDE_MENTAL)
    else:
        out = dict(CONDUTAS.get(nivel, CONDUTAS["monitoramento"]))
    out["nivel"] = nivel
    out["nivel_label"] = NIVEL_LABELS.get(nivel, "Monitorar")
    return out
