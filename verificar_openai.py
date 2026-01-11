#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar configuração do OpenAI
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

print("=" * 60)
print("DIAGNÓSTICO OPENAI - Sophia Chatbot")
print("=" * 60)
print()

# 1. Verifica se a biblioteca openai está instalada
print("1. Verificando biblioteca openai...")
try:
    import openai
    from openai import OpenAI
    print("   [OK] Biblioteca openai instalada")
    print(f"   Versao: {openai.__version__}")
except ImportError as e:
    print("   [ERRO] Biblioteca openai NAO instalada")
    print(f"   Erro: {e}")
    print("   Solução: Execute: pip install openai")
    sys.exit(1)

print()

# 2. Verifica variáveis de ambiente
print("2. Verificando variáveis de ambiente...")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
USE_AI = os.getenv("USE_AI", "true").lower() == "true"

if OPENAI_API_KEY:
    print(f"   [OK] OPENAI_API_KEY encontrada (tamanho: {len(OPENAI_API_KEY)} caracteres)")
    print(f"   Primeiros caracteres: {OPENAI_API_KEY[:10]}...")
    if not OPENAI_API_KEY.startswith("sk-"):
        print("   [AVISO] A chave nao comeca com 'sk-' - pode estar incorreta")
else:
    print("   [ERRO] OPENAI_API_KEY NAO encontrada")
    print("   Solucao: Adicione OPENAI_API_KEY no arquivo .env")

if OPENAI_ASSISTANT_ID:
    print(f"   [OK] OPENAI_ASSISTANT_ID encontrado: {OPENAI_ASSISTANT_ID}")
else:
    print("   [AVISO] OPENAI_ASSISTANT_ID nao encontrado (sera criado automaticamente)")

print(f"   USE_AI: {USE_AI}")
print()

# 3. Tenta inicializar cliente OpenAI
if OPENAI_API_KEY:
    print("3. Testando conexão com OpenAI...")
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("   [OK] Cliente OpenAI inicializado com sucesso")
        
        # Tenta listar modelos para verificar se a chave funciona
        print("   Testando autenticacao...")
        models = client.models.list()
        print(f"   [OK] Autenticacao OK - {len(list(models))} modelos disponiveis")
        
    except Exception as e:
        print(f"   [ERRO] Erro ao inicializar cliente: {e}")
        if "Incorrect API key" in str(e) or "Invalid API key" in str(e):
            print("   [AVISO] A chave API esta incorreta ou invalida")
            print("   Solucao: Verifique sua chave em https://platform.openai.com/api-keys")
        elif "rate_limit" in str(e).lower() or "quota" in str(e).lower():
            print("   [AVISO] Quota excedida ou limite de taxa atingido")
            print("   Solucao: Verifique sua conta em https://platform.openai.com/account/billing")
        else:
            print(f"   Erro desconhecido: {type(e).__name__}")
else:
    print("3. [PULADO] Pulando teste de conexao (sem OPENAI_API_KEY)")
print()

# 4. Verifica arquivo .env
print("4. Verificando arquivo .env...")
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    print(f"   [OK] Arquivo .env encontrado: {env_path}")
    with open(env_path, "r", encoding="utf-8") as f:
        linhas = f.readlines()
        tem_openai_key = any("OPENAI_API_KEY" in linha for linha in linhas)
        if tem_openai_key:
            print("   [OK] OPENAI_API_KEY encontrada no arquivo .env")
        else:
            print("   [AVISO] OPENAI_API_KEY nao encontrada no arquivo .env")
else:
    print(f"   [AVISO] Arquivo .env nao encontrado em: {env_path}")
    print("   Solucao: Crie um arquivo .env na raiz do projeto")
print()

# 5. Resumo e recomendações
print("=" * 60)
print("RESUMO E RECOMENDAÇÕES")
print("=" * 60)

problemas = []
if not OPENAI_API_KEY:
    problemas.append("OPENAI_API_KEY não configurada")
if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-"):
    problemas.append("OPENAI_API_KEY parece estar incorreta")

if problemas:
    print("\n[PROBLEMAS ENCONTRADOS]:")
    for i, problema in enumerate(problemas, 1):
        print(f"   {i}. {problema}")
    
    print("\n[PASSOS PARA RESOLVER]:")
    print("   1. Acesse https://platform.openai.com/api-keys")
    print("   2. Crie uma nova chave API (ou use uma existente)")
    print("   3. Adicione no arquivo .env:")
    print("      OPENAI_API_KEY=sk-sua-chave-aqui")
    print("   4. Se quiser usar um assistente especifico, adicione tambem:")
    print("      OPENAI_ASSISTANT_ID=asst_seu-id-aqui")
    print("   5. Reinicie o servidor")
else:
    print("\n[OK] Tudo parece estar configurado corretamente!")
    print("   Se ainda assim nao funcionar, verifique:")
    print("   - Se ha creditos na sua conta OpenAI")
    print("   - Se a chave nao expirou")
    print("   - Os logs do servidor para mais detalhes")

print()

