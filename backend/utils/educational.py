# -*- coding: utf-8 -*-
# Loader de conteúdos educativos a partir de JSON.
import json
import os
from typing import List, Dict

ALLOWED_ICONS = {"ribbon", "bottles"}


def _to_int(x, default=3):
    try:
        if isinstance(x, bool):
            return default
        return int(x)
    except Exception:
        return default


def load_educational_items(path: str) -> List[Dict]:
    """
    Lê itens do JSON. Aceita dois formatos:
      - { "items": [ {id,title,subtitle,url,read_min,icon}, ... ] }
      - [ {id,title,subtitle,url,read_min,icon}, ... ]
    Faz saneamento básico e defaults:
      - id único (gera se faltar)
      - read_min int (default 3, clamp 1..60)
      - icon ∈ {'ribbon','bottles'} (default 'ribbon')
      - ignora itens sem title ou url
    """
    if not path or not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        return []
    out, seen = [], set()
    for it in items:
        if not isinstance(it, dict):
            continue
        _id = str(it.get("id") or "").strip()
        title = str(it.get("title") or "").strip()
        subtitle = str(it.get("subtitle") or "").strip()
        url = str(it.get("url") or "").strip()
        read_min = _to_int(it.get("read_min"), 3)
        icon = str(it.get("icon") or "ribbon").strip().lower()

        if not title or not url:
            continue
        if not _id:
            _id = f"edu-{len(out)+1}"
        if _id in seen:
            _id = f"{_id}-{len(out)+1}"
        seen.add(_id)

        if icon not in ALLOWED_ICONS:
            icon = "ribbon"
        if read_min < 1:
            read_min = 1
        if read_min > 60:
            read_min = 60

        out.append({
            "id": _id,
            "title": title,
            "subtitle": subtitle,
            "url": url,
            "read_min": read_min,
            "icon": icon
        })
    return out
