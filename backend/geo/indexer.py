# -*- coding: utf-8 -*-
import csv
import json
import os
import re
import time
import unicodedata
from hashlib import md5
from typing import Dict, Iterable, List, Optional

ALIASES = {
    "cnes": ["cnes", "cod_cnes", "codigo_cnes", "co_cnes", "id_cnes", "cnes_code"],
    "name": ["no_fantasia", "nome_fantasia", "nome", "razao_social", "name"],
    "logradouro": ["logradouro", "endereco", "rua", "address", "logradouro_nome"],
    "numero": ["numero", "nro", "num", "nr"],
    "bairro": ["bairro", "district", "neighborhood"],
    "municipio": ["municipio", "cidade", "city"],
    "uf": ["uf", "estado", "state"],
    "cep": ["cep", "zip", "codigo_postal"],
    "lat": ["lat", "latitude", "nu_latitude", "latitude_dec", "y"],
    "lon": ["lon", "longitude", "nu_longitude", "longitude_dec", "x"],
    "public_private": ["tp_gestao", "gestao", "esfera", "natureza", "esfera_admin", "publico_privado"],
    "accepts_sus": ["sus", "atende_sus", "aceita_sus", "aceite_sus", "tem_sus", "atendimento_sus"],
    "accepts_convenio": ["convenio", "plano", "plano_saude", "particular", "aceita_convenio", "tem_convenio"],
}


def _norm_text(s: Optional[str]) -> str:
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    s = s.strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s


def _lower(s: Optional[str]) -> str:
    return _norm_text(s).lower()


def _get_any(row: Dict, keys: List[str]) -> Optional[str]:
    if not row:
        return None
    map_low = {_lower(k): k for k in row.keys()}
    for k in keys:
        lk = _lower(k)
        if lk in map_low:
            v = row.get(map_low[lk])
            if v is not None and str(v).strip() != "":
                return str(v)
    return None


def _to_bool(val: Optional[str]) -> Optional[bool]:
    if val is None:
        return None
    v = _lower(str(val))
    if v in {"sim", "s", "true", "1", "y", "yes", "x"}:
        return True
    if v in {"nao", "não", "n", "false", "0"}:
        return False
    if v == "s":
        return True
    if v == "n":
        return False
    return None


def _classify_ownership(raw: Optional[str]) -> Optional[str]:
    v = _lower(raw)
    if not v:
        return None
    if any(x in v for x in ["filantrop", "santacasa", "santa casa"]):
        return "Filantrópico"
    if any(x in v for x in ["public", "publico", "publica", "municipal", "estadual", "federal", "distrital"]):
        return "Público"
    if any(x in v for x in ["privado", "privada", "particular", "cooperativa", "entidade empresarial"]):
        return "Privado"
    return None


def _build_address(row: Dict) -> str:
    parts = []
    lg = _get_any(row, ALIASES["logradouro"])
    if lg:
        parts.append(lg)
    num = _get_any(row, ALIASES["numero"])
    if num:
        parts.append(num)
    bai = _get_any(row, ALIASES["bairro"])
    if bai:
        parts.append(bai)
    mun = _get_any(row, ALIASES["municipio"])
    if mun:
        parts.append(mun)
    uf = _get_any(row, ALIASES["uf"])
    if uf:
        parts.append(uf)
    cep = _get_any(row, ALIASES["cep"])
    if cep:
        parts.append(cep)
    return ", ".join([str(p).strip() for p in parts if str(p).strip() != ""])


def _to_float(x: Optional[str]) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None


def _slug_name_address(name: str, address: str) -> str:
    n = re.sub(r"[^a-z0-9]+", "-", _lower(name)).strip("-")
    a = re.sub(r"[^a-z0-9]+", "-", _lower(address)).strip("-")
    return f"{n}|{a}"


def _iter_records_from_file(path: str) -> Iterable[Dict]:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".csv", ".tsv"}:
        delim = "," if ext == ".csv" else "\t"
        with open(path, "r", encoding="utf-8-sig", errors="ignore", newline="") as f:
            reader = csv.DictReader(f, delimiter=delim)
            for row in reader:
                yield row
    elif ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for row in data:
                if isinstance(row, dict):
                    yield row
        elif isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
            for row in data["items"]:
                if isinstance(row, dict):
                    yield row
    elif ext in {".ndjson", ".jsonl"}:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    if isinstance(row, dict):
                        yield row
                except Exception:
                    continue


def _canonicalize(row: Dict, source_file: str) -> Optional[Dict]:
    cnes = _get_any(row, ALIASES["cnes"])
    if cnes:
        cnes = re.sub(r"\D", "", cnes)
        if cnes == "":
            cnes = None
    name = _get_any(row, ALIASES["name"])
    address = _build_address(row)
    lat = _to_float(_get_any(row, ALIASES["lat"]))
    lon = _to_float(_get_any(row, ALIASES["lon"]))
    owns_raw = _get_any(row, ALIASES["public_private"])
    ownership = _classify_ownership(owns_raw)
    sus_v = _to_bool(_get_any(row, ALIASES["accepts_sus"]))
    conv_v = _to_bool(_get_any(row, ALIASES["accepts_convenio"]))
    if ownership is None and sus_v is True:
        ownership = "Público"
    if not name and not cnes:
        return None
    return {
        "cnes": cnes,
        "name": name or "",
        "address": address or "",
        "lat": lat,
        "lon": lon,
        "public_private": ownership,
        "accepts_sus": True if sus_v is True else (False if sus_v is False else None),
        "accepts_convenio": True if conv_v is True else (False if conv_v is False else None),
        "_source": source_file,
    }


def _merge_records(a: Dict, b: Dict) -> Dict:
    out = dict(a)
    if len((b.get("name") or "")) > len((a.get("name") or "")):
        out["name"] = b.get("name")
    if len((b.get("address") or "")) > len((a.get("address") or "")):
        out["address"] = b.get("address")
    if (a.get("lat") is None or a.get("lon") is None) and (b.get("lat") is not None and b.get("lon") is not None):
        out["lat"] = b.get("lat")
        out["lon"] = b.get("lon")
    for k in ("accepts_sus", "accepts_convenio"):
        va, vb = a.get(k), b.get(k)
        if vb is True or (va is None and vb is not None):
            out[k] = vb
    own_a, own_b = a.get("public_private"), b.get("public_private")
    if own_a is None and own_b is not None:
        out["public_private"] = own_b
    elif own_a and own_b and own_a != own_b:
        if out.get("accepts_sus") is True:
            out["public_private"] = "Público"
    srcs = []
    for s in (a.get("_source"), b.get("_source")):
        if isinstance(s, list):
            srcs.extend(s)
        elif isinstance(s, str) and s:
            srcs.append(s)
    out["_source"] = sorted(list({*srcs}))
    return out


def build_hospitals_index(source_dirs: List[str], output_path: str) -> Dict:
    items_by_id: Dict[str, Dict] = {}
    total_files = 0
    total_rows = 0
    for d in source_dirs:
        if not d or not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for fn in files:
                if os.path.splitext(fn)[1].lower() not in {".csv", ".tsv", ".json", ".ndjson", ".jsonl"}:
                    continue
                total_files += 1
                fpath = os.path.join(root, fn)
                for row in _iter_records_from_file(fpath):
                    total_rows += 1
                    rec = _canonicalize(row, fpath)
                    if not rec:
                        continue
                    key = rec.get("cnes") or _slug_name_address(rec.get("name", ""), rec.get("address", ""))
                    if key in items_by_id:
                        items_by_id[key] = _merge_records(items_by_id[key], rec)
                    else:
                        rec["_source"] = [rec["_source"]] if isinstance(rec["_source"], str) else (rec["_source"] or [])
                        items_by_id[key] = rec
    items = list(items_by_id.values())
    payload = {
        "created_at": int(time.time()),
        "count": len(items),
        "items": items,
    }
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    return payload


class GeoIndex:
    def __init__(self, index_path: str, source_dirs: List[str], ttl_seconds: int = 600):
        self.index_path = index_path
        self.source_dirs = source_dirs
        self.ttl = ttl_seconds
        self._cache = None
        self._cache_loaded_at = 0
        self._etag = None

    def _compute_etag(self) -> str:
        h = md5()
        try:
            st = os.stat(self.index_path)
            h.update(str(st.st_mtime_ns).encode())
            h.update(str(st.st_size).encode())
        except Exception:
            h.update(b"no-file")
        return h.hexdigest()

    def _should_rebuild(self) -> bool:
        try:
            idx_mtime = os.path.getmtime(self.index_path)
        except Exception:
            return True
        newest_src = 0
        for d in self.source_dirs:
            if not d or not os.path.isdir(d):
                continue
            for root, _, files in os.walk(d):
                for fn in files:
                    if os.path.splitext(fn)[1].lower() not in {".csv", ".tsv", ".json", ".ndjson", ".jsonl"}:
                        continue
                    m = os.path.getmtime(os.path.join(root, fn))
                    if m > newest_src:
                        newest_src = m
        return newest_src > idx_mtime

    def ensure_loaded(self, force_rebuild: bool = False):
        now = time.time()
        if self._cache and (now - self._cache_loaded_at) < self.ttl and not force_rebuild:
            return
        if force_rebuild or self._should_rebuild() or not os.path.isfile(self.index_path):
            build_hospitals_index(self.source_dirs, self.index_path)
        with open(self.index_path, "r", encoding="utf-8") as f:
            self._cache = json.load(f)
        self._cache_loaded_at = now
        self._etag = self._compute_etag()

    @property
    def etag(self) -> Optional[str]:
        return self._etag

    @property
    def items(self) -> List[Dict]:
        return (self._cache or {}).get("items", [])
