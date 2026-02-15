# -*- coding: utf-8 -*-
# get_geo_data_info() sem editar backend.api.routes:
# - introspecta variáveis/globals prováveis (_geo_df, _geo_df_loaded_at, _geo_df_path, EMERGENCY_CACHE_TTL_SECONDS)
# - retorna um dict com count, source_path, mtime, loaded_at, ttl_seconds, ttl_remaining

import importlib
import os
import time
from typing import Any, Dict, Optional


def _getattr_any(mod, *names, default=None):
    for n in names:
        if hasattr(mod, n):
            return getattr(mod, n)
    return default


def _count_obj(df: Any) -> Optional[int]:
    try:
        # pandas DataFrame
        try:
            import pandas
            if isinstance(df, pandas.core.generic.NDFrame):
                return int(getattr(df, "shape", [0])[0])
        except Exception:
            pass
        # lista, dict, etc.
        if hasattr(df, "__len__"):
            return int(len(df))
    except Exception:
        return None
    return None


def get_geo_data_info() -> Dict:
    """
    Tenta ler os metadados expostos em backend.api.routes.
    Retorna dict com count/source_path/mtime/loaded_at/ttl_seconds/ttl_remaining quando possível.
    """
    routes = importlib.import_module("backend.api.routes")
    
    # DataFrame/cache
    df = _getattr_any(routes, "_geo_df_cache", "_geo_df", "GEO_DF", default=None)
    count = _count_obj(df)
    
    # fonte/caminho do arquivo
    source_path = _getattr_any(routes, "_geo_df_path", "GEO_SOURCE_PATH", "EMERGENCY_SOURCE_PATH", default=None)
    
    # se não achou path direto, tenta função _geo_parquet_path()
    if source_path is None:
        try:
            parquet_path_fn = _getattr_any(routes, "_geo_parquet_path", default=None)
            if callable(parquet_path_fn):
                p = parquet_path_fn()
                if p:
                    source_path = str(p) if hasattr(p, "__str__") else p
        except Exception:
            pass
    
    # mtime do arquivo
    mtime = None
    if source_path and isinstance(source_path, str):
        try:
            mtime = int(os.path.getmtime(source_path))
        except Exception:
            mtime = None
    
    # se não achou mtime do arquivo, tenta variável global
    if mtime is None:
        mtime_val = _getattr_any(routes, "_geo_df_mtime", "GEO_DF_MTIME", default=None)
        if mtime_val is not None:
            try:
                mtime = int(mtime_val)
            except Exception:
                mtime = None
    
    # quando foi carregado na memória
    loaded_at = _getattr_any(routes, "_geo_df_loaded_at", "GEO_DF_LOADED_AT", default=None)
    if loaded_at is not None:
        try:
            loaded_at = int(loaded_at)
        except Exception:
            loaded_at = None
    
    # TTL (segundos) e quanto falta
    ttl_seconds = None
    try:
        ttl_seconds = _getattr_any(routes, "EMERGENCY_CACHE_TTL_SECONDS", "CACHE_TTL_SECONDS", default=None)
        if ttl_seconds is None:
            ttl_seconds = int(os.environ.get("EMERGENCY_CACHE_TTL_SECONDS", "0"))  # fallback env
        if ttl_seconds is not None:
            ttl_seconds = int(ttl_seconds)
    except Exception:
        ttl_seconds = None
    
    ttl_remaining = None
    try:
        if loaded_at and ttl_seconds:
            ttl_remaining = max(0, loaded_at + ttl_seconds - int(time.time()))
    except Exception:
        ttl_remaining = None
    
    out = {
        "count": count,
        "source_path": source_path,
        "mtime": mtime,
        "loaded_at": loaded_at,
        "ttl_seconds": ttl_seconds,
        "ttl_remaining": ttl_remaining,
    }
    
    # limpa None vazios para log ficar mais "limpo" (opcional)
    return {k: v for k, v in out.items() if v is not None}
