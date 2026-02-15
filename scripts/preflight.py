#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ok = True


def mark(status: bool, msg: str):
    global ok
    prefix = "[OK]" if status else "[ERRO]"
    print(f"{prefix} {msg}")
    if not status:
        ok = False


def exists(relpath: str):
    p = ROOT / relpath
    mark(p.exists(), f"{relpath} {'encontrado' if p.exists() else 'NÃO encontrado'}")
    return p.exists(), p


def load_envs():
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("[AVISO] python-dotenv não instalado; pulando carregamento automático de .env/env.example")
        return False
    loaded = False
    env_path = ROOT / ".env"
    env_example = ROOT / "env.example"
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path), override=False)  # não sobrescreve o que já existir
        print("[INFO] .env carregado")
        loaded = True
    if env_example.exists():
        load_dotenv(dotenv_path=str(env_example), override=False)  # fallback
        print("[INFO] env.example carregado (fallback)")
        loaded = True
    return loaded


def check_env_vars():
    required = ["API_PORT", "DB_URL", "SCORING_FILE", "CNES_CODES_FILE", "GEOCODER"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        mark(False, f"Variáveis ausentes: {missing} (crie .env a partir de env.example)")
    else:
        mark(True, "Variáveis essenciais presentes")
    print("GEOCODER =", os.environ.get("GEOCODER", "(default)"))
    print("TRAVEL_TIME =", os.environ.get("TRAVEL_TIME", "off"))


def check_cnes_codes(path: str):
    try:
        data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        kws = [k.lower() for k in data.get("keywords_nome_fantasia", [])]
        campos = [c.upper() for c in data.get("campos_sus", [])]
        dv = str(data.get("data_version", ""))

        def norm(s):
            return s.replace("é", "e").replace("É", "E")

        kws_norm = [norm(k) for k in kws]
        needed = [norm("maternidade"), norm("hospital da mulher"), norm("obstétrico")]
        has_kws = all(any(n in k for k in kws_norm) for n in needed)
        has_campos = ("IND_SUS" in campos and "ATEND_SUS" in campos)
        mark(has_kws, f"keywords_nome_fantasia ok: {data.get('keywords_nome_fantasia')}")
        mark(has_campos, f"campos_sus ok: {campos}")
        mark(dv == "2025-02", f"data_version = {dv} (esperado: 2025-02)")
    except Exception as e:
        mark(False, f"Falha lendo config/cnes_codes.json: {e}")


def main():
    exists("env.example")
    exists("config/scoring.yaml")
    has_codes, _ = exists("config/cnes_codes.json")
    exists("backend/api/contracts/get_evidence.json")
    exists("backend/api/main.py")
    exists("backend/api/routes.py")
    exists("backend/utils/env.py")
    exists("backend/utils/phone.py")
    exists("backend/utils/travel_time.py")
    exists("scripts/run_orchestrator.py")
    exists(".github/workflows/snapshot.yml")
    exists("tests/unit/test_phone.py")
    exists("tests/golden/test_golden_set.py")
    exists("sql/qa_queries.sql")

    if has_codes:
        check_cnes_codes("config/cnes_codes.json")

    load_envs()
    check_env_vars()

    print("\nResumo:", "SUCESSO ✅" if ok else "PENDÊNCIAS ❌")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
