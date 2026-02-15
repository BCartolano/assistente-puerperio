#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Classify – Aplica regras e pesos (config/scoring.yaml + config/cnes_codes.json).
Gera has_maternity, score, evidence (tipo, código, fonte) por cnes_id.
Regras: sinal forte = leito OU serviço/classif OU habilitação OU tipo maternidade;
        provável = score 0.4–0.59 + keyword no nome fantasia.
"""

import os
import sys
import json
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
CONFIG_DIR = os.path.join(BASE_DIR, "config")


def load_cnes_codes():
    path = os.path.join(CONFIG_DIR, "cnes_codes.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scoring():
    try:
        import yaml
        path = os.path.join(CONFIG_DIR, "scoring.yaml")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return {
            "weights": {
                "leito_obst_neonatal": 0.6,
                "servico_classif_obst": 0.5,
                "habilitacao_obst": 0.5,
                "tipo_maternidade": 0.3,
                "keyword_nome_fantasia": 0.2,
            },
            "rules": {
                "has_maternity_provavel": {"score_min": 0.4, "score_max": 0.59, "require_keyword": True},
            },
        }


def classify_establishment(estab: dict, codes: dict, weights: dict, rules: dict) -> dict:
    """
    Retorna { "has_maternity": 0|1, "score": float, "evidence": list }.
    estab: dict com cnes_id, fantasy_name, tipo_unidade, leitos[], servicos[], classif[], habilitacoes[]
    """
    evidence = []
    score = 0.0

    # Sinais fortes
    leitos = estab.get("leitos") or estab.get("co_leito_list") or []
    for code in leitos:
        if str(code) in codes.get("bed_types_obst", []) + codes.get("bed_types_neonatal", []):
            score = max(score, weights.get("leito_obst_neonatal", 0.6))
            evidence.append(f"leito:{code}:rlEstabLeito")
            break

    servicos = estab.get("servicos") or estab.get("co_servico_list") or []
    for code in servicos:
        if str(code) in codes.get("services_obst", []):
            score = max(score, weights.get("servico_classif_obst", 0.5))
            evidence.append(f"servico:{code}:rlEstabServClass")
            break

    classif = estab.get("classificacoes") or estab.get("co_classificacao_list") or []
    for code in classif:
        if str(code) in codes.get("classif_obst", []):
            score = max(score, weights.get("servico_classif_obst", 0.5))
            evidence.append(f"classif:{code}:rlEstabServClass")
            break

    hab = estab.get("habilitacoes") or estab.get("co_habilitacao_list") or []
    hab_obst = codes.get("habilitacoes_obst", [])
    if hab_obst and hab_obst != ["review_needed"]:
        for code in hab:
            if str(code) in hab_obst:
                score = max(score, weights.get("habilitacao_obst", 0.5))
                evidence.append(f"habilitacao:{code}:habilitacoes")
                break

    tipo = str(estab.get("tipo_unidade") or estab.get("co_tipo_unidade") or "")
    if tipo in codes.get("tipos_estab_maternidade", []):
        score = max(score, weights.get("tipo_maternidade", 0.3))
        evidence.append(f"tipo:{tipo}:tbEstabelecimento")

    # Sinal fraco: keyword (normalizando acentos e caixa)
    import unicodedata
    def _norm(s):
        if not s:
            return ""
        s = unicodedata.normalize("NFD", str(s))
        return "".join(c for c in s if unicodedata.category(c) != "Mn").upper()
    nome_raw = estab.get("fantasy_name") or estab.get("name") or ""
    nome = _norm(nome_raw)
    keywords = codes.get("keywords_nome_fantasia", [])
    has_keyword = any(_norm(kw or "") in nome for kw in keywords)
    if has_keyword:
        score += weights.get("keyword_nome_fantasia", 0.2)
        evidence.append("keyword:nome_fantasia")

    # Decisão
    has_strong = any(
        e.startswith("leito:") or e.startswith("servico:") or e.startswith("classif:")
        or e.startswith("habilitacao:") or e.startswith("tipo:")
        for e in evidence
    )
    if has_strong:
        has_maternity = 1
    else:
        prov = rules.get("has_maternity_provavel", {})
        smin, smax = prov.get("score_min", 0.4), prov.get("score_max", 0.59)
        if smin <= score <= smax and prov.get("require_keyword") and has_keyword:
            has_maternity = 1  # Provável
        else:
            has_maternity = 0

    score = min(1.0, score)
    return {"has_maternity": has_maternity, "score": round(score, 4), "evidence": evidence}


def main():
    parser = argparse.ArgumentParser(description="Classificador maternidade")
    parser.add_argument("--input", default=None, help="JSON/GeoJSON com estabelecimentos")
    parser.add_argument("--output", default=None, help="JSON de saída com has_maternity, score, evidence")
    args = parser.parse_args()

    codes = load_cnes_codes()
    scoring = load_scoring()
    weights = scoring.get("weights", {})
    rules = scoring.get("rules", {})

    if args.input and os.path.isfile(args.input):
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        features = data.get("features", [data] if isinstance(data, list) else [])
        results = []
        for feat in features:
            props = feat.get("properties", feat) if isinstance(feat, dict) else feat
            cnes_id = props.get("id") or props.get("cnes_id")
            if not cnes_id:
                continue
            out = classify_establishment(props, codes, weights, rules)
            out["cnes_id"] = cnes_id
            results.append(out)
        out_path = args.output or args.input.replace(".geojson", "_classified.json").replace(".json", "_classified.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Classificados: {len(results)}. Saída: {out_path}")
    else:
        # Exemplo: um estabelecimento
        example = {
            "cnes_id": "1234567",
            "fantasy_name": "Hospital da Mulher",
            "tipo_unidade": "07",
            "leitos": ["01", "02"],
            "servicos": ["125"],
            "classificacoes": ["001"],
        }
        out = classify_establishment(example, codes, weights, rules)
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
