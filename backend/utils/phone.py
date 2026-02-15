#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formatação de telefone BR: display "+55 (DD) 9XXXX-XXXX" e e164 "+55DDXXXXXXXXX".
Remover tudo que não for dígito; remover prefixo 55 se presente.
Vazio/curto: retornar ("Telefone não informado", None).
"""

import re
from typing import Optional, Tuple


def _digits_only(s: str) -> str:
    return re.sub(r"\D", "", s) if s else ""


def format_br_phone(raw: Optional[str]) -> Tuple[str, Optional[str]]:
    """
    Retorna (telefone_formatado, phone_e164).
    - 11 dígitos: celular → "+55 (DD) 9XXXX-XXXX" e e164 "+55DDXXXXXXXXX".
    - 10 dígitos: fixo → "+55 (DD) XXXX-XXXX" e e164 "+55DDXXXXXXXX".
    - Vazio/curto: ("Telefone não informado", None).
    """
    if not raw or not str(raw).strip():
        return ("Telefone não informado", None)
    d = _digits_only(str(raw))
    if d.startswith("55") and len(d) > 11:
        d = d[2:]
    if len(d) < 10:
        return ("Telefone não informado", None)
    if len(d) == 10:
        dd, rest = d[:2], d[2:]
        return (f"+55 ({dd}) {rest[:4]}-{rest[4:]}", f"+55{dd}{rest}")
    if len(d) == 11 and d[2] == "9":
        dd, rest = d[:2], d[2:]
        return (f"+55 ({dd}) {rest[:5]}-{rest[5:]}", f"+55{dd}{rest}")
    if len(d) >= 11:
        d = d[-11:] if len(d) > 11 else d
        dd, rest = d[:2], d[2:]
        if len(rest) == 9:
            return (f"+55 ({dd}) {rest[:5]}-{rest[5:]}", f"+55{dd}{rest}")
        return (f"+55 ({dd}) {rest[:4]}-{rest[4:]}", f"+55{dd}{rest}")
    return ("Telefone não informado", None)
