#!/usr/bin/env python3
"""Teste rápido para verificar se _normalize_esfera está funcionando corretamente."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

try:
    from api.routes import _normalize_esfera
except ImportError:
    from backend.api.routes import _normalize_esfera

# Testes
test_cases = [
    ("Desconhecido", "HOSPITAL SAO JOSE", None),
    ("DESCONHECIDO", "HOSPITAL TESTE", None),
    ("desconhecido", None, None),
    ("Público", None, "Público"),
    ("Privado", None, "Privado"),
    ("Filantrópico", None, "Filantrópico"),
    (None, "HOSPITAL MUNICIPAL", "Público"),
    ("", "HOSPITAL ESTADUAL", "Público"),
]

print("Testando _normalize_esfera:")
print("=" * 60)
for esfera_raw, nome, expected in test_cases:
    result = _normalize_esfera(esfera_raw, nome)
    status = "✅" if (result == expected or (expected is None and result in ("Público", "Privado", "Filantrópico", None))) else "❌"
    print(f"{status} esfera_raw={esfera_raw!r:20} nome={nome!r:30} → {result!r:15} (esperado: {expected!r})")

print("\n" + "=" * 60)
print("Se todos os testes passaram, a função está funcionando corretamente.")
