# -*- coding: utf-8 -*-
import os
import time

# Cache por processo: evita que version mude a cada request e cause loop de reload
_VERSION_CACHE = None


def get_build_version():
    global _VERSION_CACHE
    if _VERSION_CACHE is not None:
        return _VERSION_CACHE
    v = os.environ.get("BUILD_VERSION")
    if v:
        _VERSION_CACHE = str(v)
        return _VERSION_CACHE
    # Se existir arquivo VERSION, use-o
    path = os.path.join(os.path.dirname(__file__), "..", "VERSION")
    path = os.path.abspath(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            t = f.read().strip()
            if t:
                _VERSION_CACHE = t
                return _VERSION_CACHE
    except Exception:
        pass
    # Fallback: timestamp fixo por processo (muda só no deploy/restart)
    _VERSION_CACHE = str(int(time.time()))
    return _VERSION_CACHE
