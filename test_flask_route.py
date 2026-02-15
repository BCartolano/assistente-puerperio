#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se as rotas Flask estão funcionando
"""

import requests
import sys

BASE_URL = "http://localhost:5000"

print("🔍 Testando rotas Flask...")
print("=" * 50)

# Teste 1: Rota raiz
print("\n1. Testando rota raiz (/)...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ OK - Rota raiz funciona")
    else:
        print(f"   ❌ ERRO - Status inesperado: {response.status_code}")
except Exception as e:
    print(f"   ❌ ERRO - Não foi possível conectar: {e}")
    sys.exit(1)

# Teste 2: Rota /api/user (deve retornar 401, não 500)
print("\n2. Testando rota /api/user (GET)...")
try:
    response = requests.get(f"{BASE_URL}/api/user", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Resposta: {response.text[:200]}")
    if response.status_code == 401:
        print("   ✅ OK - Retornou 401 (não autenticado), como esperado")
    elif response.status_code == 500:
        print("   ❌ ERRO - Retornou 500 (erro interno)")
    else:
        print(f"   ⚠️ Status inesperado: {response.status_code}")
except Exception as e:
    print(f"   ❌ ERRO - Exceção: {e}")

# Teste 3: Rota /api/login (POST vazio deve retornar 400, não 500)
print("\n3. Testando rota /api/login (POST vazio)...")
try:
    response = requests.post(f"{BASE_URL}/api/login", json={}, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Resposta: {response.text[:200]}")
    if response.status_code == 400:
        print("   ✅ OK - Retornou 400 (dados inválidos), como esperado")
    elif response.status_code == 500:
        print("   ❌ ERRO - Retornou 500 (erro interno)")
    else:
        print(f"   ⚠️ Status inesperado: {response.status_code}")
except Exception as e:
    print(f"   ❌ ERRO - Exceção: {e}")

print("\n" + "=" * 50)
print("✅ Teste concluído!")
