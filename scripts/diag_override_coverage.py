#!/usr/bin/env python3
"""Diagnóstico rápido: verifica cobertura dos overrides CNES."""
import sys
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = "http://localhost:5000"

# Carrega .env
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

def check_files_directly():
    """Verifica arquivos diretamente sem depender do endpoint."""
    snapshot = os.getenv("SNAPSHOT", "202512")
    data_dir = BASE_DIR / "data"
    
    est_file = data_dir / f"tbEstabelecimento{snapshot}.csv"
    conv_file = data_dir / f"tbEstabPrestConv{snapshot}.csv"
    
    print(f"\n[ARQUIVOS] Snapshot configurado: {snapshot}")
    print(f"[ARQUIVOS] tbEstabelecimento: {'✅' if est_file.exists() else '❌'} {est_file.name}")
    print(f"[ARQUIVOS] tbEstabPrestConv: {'✅' if conv_file.exists() else '❌'} {conv_file.name}")
    
    if not est_file.exists():
        print(f"\n⚠️  PROBLEMA: Arquivo não encontrado: {est_file}")
        print("   → Verifique SNAPSHOT no .env")
        print("   → OU copie CSVs para snapshot correto")
        return False
    
    if not conv_file.exists():
        print(f"\n⚠️  AVISO: Arquivo não encontrado: {conv_file}")
        print("   → Overrides de convênios não estarão disponíveis")
        print("   → Mas overrides de esfera/SUS ainda funcionarão")
    
    return True

def main():
    print("=" * 60)
    print("DIAGNÓSTICO RÁPIDO: Cobertura dos Overrides CNES")
    print("=" * 60)
    
    # 0. Verifica arquivos diretamente primeiro
    files_ok = check_files_directly()
    
    # 1. Tenta verificar coverage via API
    try:
        r = requests.get(f"{BASE_URL}/api/v1/debug/overrides/coverage", timeout=5)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_loaded", 0)
            snapshot = data.get("snapshot_usado", "N/A")
            error = data.get("error")
            
            if error:
                print(f"\n⚠️  AVISO: {error}")
            
            print(f"\n[COVERAGE API] Total carregado: {total}")
            print(f"[COVERAGE API] Snapshot usado: {snapshot}")
            
            if total == 0:
                print("\n⚠️  PROBLEMA: total_loaded = 0")
                print("   → Overrides não foram carregados")
                if not files_ok:
                    print("   → Arquivos CSV não encontrados (veja acima)")
                else:
                    print("   → Arquivos existem, mas overrides não carregaram")
                    print("   → Tente: POST /api/v1/debug/overrides/refresh")
                return 1
            elif total < 1000:
                print(f"\n⚠️  AVISO: total_loaded muito baixo ({total})")
                print("   → Pode indicar snapshot/CSV incorreto")
            else:
                print(f"\n✅ Overrides carregados: {total} registros")
        elif r.status_code == 404:
            print(f"\n⚠️  Endpoint não encontrado (404)")
            print("   → Endpoint pode estar protegido por autenticação")
            print("   → OU servidor não está rodando em Flask")
            print("\n   Verificação alternativa (arquivos):")
            if files_ok:
                print("   ✅ Arquivo principal encontrado (tbEstabelecimento)")
                if not (BASE_DIR / "data" / f"tbEstabPrestConv{snapshot}.csv").exists():
                    print("   ⚠️  Arquivo de convênios não encontrado (tbEstabPrestConv)")
                    print("   → Overrides de esfera/SUS funcionarão, mas convênios não")
                print("   → Overrides podem estar funcionando, mas endpoint protegido")
            else:
                print("   ❌ Arquivos CSV não encontrados")
                print("   → Este é o problema principal")
            print("\n   Tente acessar diretamente:")
            print(f"   curl {BASE_URL}/api/v1/debug/overrides/coverage")
            print("\n   OU verifique se o servidor está rodando:")
            print(f"   curl {BASE_URL}/api/v1/health")
            return 1 if not files_ok else 0
        else:
            print(f"\n❌ Erro ao buscar coverage: {r.status_code}")
            print(f"   Resposta: {r.text[:200]}")
            if not files_ok:
                return 1
    except requests.exceptions.ConnectionError:
        print("\n⚠️  Servidor não está rodando em http://localhost:5000")
        print("   → Verificação via arquivos:")
        if files_ok:
            print("   ✅ Arquivos CSV encontrados")
            print("   → Quando iniciar o servidor, overrides devem carregar")
        else:
            print("   ❌ Arquivos CSV não encontrados")
            print("   → Corrija antes de iniciar o servidor")
        return 1 if not files_ok else 0
    except Exception as e:
        print(f"\n⚠️  Erro ao buscar coverage: {e}")
        if not files_ok:
            return 1
    
    # 2. Testa busca com debug
    print("\n" + "=" * 60)
    print("TESTE DE BUSCA COM DEBUG")
    print("=" * 60)
    print("\nCole no console do navegador:")
    print("""
fetch('/api/v1/emergency/search?lat=-23.1931904&lon=-45.7965568&radius_km=25&limit=20&expand=true&debug=true')
  .then(r=>r.json())
  .then(d=>console.table((d.results||[]).map(it=>({
    nome:it.nome,
    cnes:it.cnes_id,
    esfera:it.esfera,
    sus:it.sus_badge,
    hit:it.override_hit,
    reason:it.override_reason
  }))));
""")
    
    print("\n" + "=" * 60)
    print("INTERPRETAÇÃO:")
    print("=" * 60)
    print("""
- Se override_reason = "no_match" em quase todos:
  → CSV/snapshot errado (override não "enxerga" os CNES do dataset)
  → Solução: Ajuste SNAPSHOT no .env ou copie CSVs para snapshot correto

- Se aparece "esfera: Público/Filantrópico/Privado" para vários:
  → Payload está correto
  → Se ainda aparecer "Desconhecido" no front, é cache do navegador

- Se override_hit = true na maioria:
  → Overrides estão funcionando corretamente
""")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
