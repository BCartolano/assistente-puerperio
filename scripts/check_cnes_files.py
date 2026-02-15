#!/usr/bin/env python3
"""Verifica quais arquivos CNES existem."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

snapshot = os.getenv("SNAPSHOT", "202512")
data_dir = BASE_DIR / "data"

print("=" * 60)
print("VERIFICAÇÃO DE ARQUIVOS CNES")
print("=" * 60)
print(f"\nSnapshot configurado: {snapshot}")

# Verifica estabelecimentos
est_file = data_dir / f"tbEstabelecimento{snapshot}.csv"
print(f"\n[ESTABELECIMENTOS]")
print(f"  Arquivo esperado: tbEstabelecimento{snapshot}.csv")
if est_file.exists():
    size = est_file.stat().st_size / (1024 * 1024)  # MB
    print(f"  ✅ Encontrado: {est_file}")
    print(f"  Tamanho: {size:.2f} MB")
else:
    print(f"  ❌ Não encontrado: {est_file}")
    # Procura alternativas
    alternatives = list(data_dir.glob("tbEstabelecimento*.csv"))
    if alternatives:
        print(f"  Arquivos alternativos encontrados:")
        for alt in alternatives:
            print(f"    - {alt.name}")

# Verifica convênios
conv_file = data_dir / f"tbEstabPrestConv{snapshot}.csv"
print(f"\n[CONVÊNIOS]")
print(f"  Arquivo esperado: tbEstabPrestConv{snapshot}.csv")
if conv_file.exists():
    size = conv_file.stat().st_size / (1024 * 1024)  # MB
    print(f"  ✅ Encontrado: {conv_file}")
    print(f"  Tamanho: {size:.2f} MB")
else:
    print(f"  ⚠️  Não encontrado: {conv_file}")
    print(f"  (OPCIONAL - overrides de esfera/SUS funcionam sem ele)")
    # Procura alternativas
    alternatives = list(data_dir.glob("tbEstabPrestConv*.csv"))
    if alternatives:
        print(f"  Arquivos alternativos encontrados:")
        for alt in alternatives:
            print(f"    - {alt.name}")
    else:
        # Procura em outros formatos
        alt_names = [
            f"rlEstabPrestConv{snapshot}.csv",
            f"tbEstabPrestConv{snapshot}.parquet",
        ]
        for alt_name in alt_names:
            alt_path = data_dir / alt_name
            if alt_path.exists():
                print(f"  ✅ Encontrado formato alternativo: {alt_name}")

print("\n" + "=" * 60)
print("CONCLUSÃO:")
print("=" * 60)
if est_file.exists():
    print("✅ Arquivo de estabelecimentos encontrado")
    print("   → Overrides de esfera/SUS funcionarão")
    if conv_file.exists():
        print("✅ Arquivo de convênios encontrado")
        print("   → Overrides de convênios também funcionarão")
    else:
        print("⚠️  Arquivo de convênios não encontrado")
        print("   → Overrides de esfera/SUS funcionarão normalmente")
        print("   → Apenas convênios não estarão disponíveis")
else:
    print("❌ Arquivo de estabelecimentos NÃO encontrado")
    print("   → Overrides NÃO funcionarão")
    print("   → Apenas normalização por nome será aplicada")
