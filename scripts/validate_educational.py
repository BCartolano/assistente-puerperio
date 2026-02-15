# -*- coding: utf-8 -*-
import json
import os
import sys

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from backend.utils.educational import load_educational_items, ALLOWED_ICONS

DEFAULT_PATH = os.path.join(_root, "backend", "static", "data", "educational.json")


def main(path=None):
    path = path or os.environ.get("EDU_JSON_PATH") or DEFAULT_PATH
    errs = []
    if not os.path.isfile(path):
        print(f"[EDU] Arquivo não encontrado: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        try:
            raw = json.load(f)
        except Exception as e:
            print(f"[EDU] JSON inválido: {e}")
            sys.exit(1)
    items = raw.get("items", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        print("[EDU] Estrutura inválida: esperado lista ou objeto com 'items'")
        sys.exit(1)

    seen = set()
    for i, it in enumerate(items):
        ctx = f"item[{i}]"
        if not isinstance(it, dict):
            errs.append(f"{ctx}: não é objeto")
            continue
        idv = str(it.get("id") or "").strip()
        title = str(it.get("title") or "").strip()
        url = str(it.get("url") or "").strip()
        icon = str(it.get("icon") or "ribbon").strip().lower()
        read_min = it.get("read_min", 3)
        if not title:
            errs.append(f"{ctx}: 'title' vazio")
        if not url:
            errs.append(f"{ctx}: 'url' vazio")
        if idv in seen and idv:
            errs.append(f"{ctx}: id duplicado '{idv}'")
        if idv:
            seen.add(idv)
        if icon not in ALLOWED_ICONS:
            errs.append(f"{ctx}: icon '{icon}' inválido (permitidos: {sorted(ALLOWED_ICONS)})")
        try:
            rm = int(read_min)
            if rm < 1 or rm > 60:
                errs.append(f"{ctx}: read_min fora de faixa (1..60): {rm}")
        except Exception:
            errs.append(f"{ctx}: read_min não inteiro: {read_min}")
        if url and not (url.startswith("https://") or url.startswith("http://")):
            errs.append(f"{ctx}: url deve começar com http(s): {url[:50]}...")

    if errs:
        print("[EDU] Falhou na validação:")
        for e in errs:
            print(" -", e)
        sys.exit(2)
    normalized = load_educational_items(path)
    print(f"[EDU] OK: {len(normalized)} item(s) válidos")
    for it in normalized:
        print(f" - {it['id']}: {it['title']} ({it['read_min']} min) [{it['icon']}] -> {it['url']}")


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else None
    main(p)
