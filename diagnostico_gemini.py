# -*- coding: utf-8 -*-
"""Script de diagnóstico para verificar se o Gemini está funcionando"""
import os
import sys

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

print("=" * 60)
print("DIAGNOSTICO DO GEMINI")
print("=" * 60)

# 1. Verifica se a chave está configurada
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"\n1. GEMINI_API_KEY configurada: {'SIM' if GEMINI_API_KEY else 'NAO'}")
if GEMINI_API_KEY:
    print(f"   - Tamanho da chave: {len(GEMINI_API_KEY)} caracteres")
    print(f"   - Primeiros 10 caracteres: {GEMINI_API_KEY[:10]}...")
else:
    print("   ERRO: GEMINI_API_KEY nao encontrada no arquivo .env")
    print("   Verifique se o arquivo .env existe na raiz do projeto")
    print("   Verifique se contem a linha: GEMINI_API_KEY=sua_chave_aqui")
    sys.exit(1)

# 2. Verifica se a biblioteca está instalada
print("\n2. Biblioteca google-generativeai:")
try:
    import google.generativeai as genai
    print("   OK: Biblioteca instalada")
    print(f"   - Versao: {genai.__version__ if hasattr(genai, '__version__') else 'N/A'}")
except ImportError as e:
    print(f"   ERRO: Biblioteca nao instalada: {e}")
    print("   Execute: pip install google-generativeai")
    sys.exit(1)

# 3. Tenta configurar a API
print("\n3. Configuracao da API:")
try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("   OK: API configurada com sucesso")
except Exception as e:
    print(f"   ERRO ao configurar API: {e}")
    sys.exit(1)

# 4. Tenta criar o modelo
print("\n4. Criacao do modelo GenerativeModel:")
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("   OK: Modelo criado com sucesso")
    print(f"   - Tipo: {type(model)}")
except Exception as e:
    print(f"   ERRO ao criar modelo: {e}")
    print(f"   - Tipo do erro: {type(e).__name__}")
    sys.exit(1)

# 5. Tenta gerar uma resposta de teste
print("\n5. Teste de geracao de resposta:")
try:
    response = model.generate_content("Oi, como voce esta?")
    if hasattr(response, 'text') and response.text:
        print("   OK: Resposta gerada com sucesso!")
        print(f"   - Resposta: {response.text[:100]}...")
    else:
        print("   ERRO: Resposta nao contem texto")
        print(f"   - Response type: {type(response)}")
        if hasattr(response, 'candidates'):
            print(f"   - Candidates: {response.candidates}")
except Exception as e:
    print(f"   ERRO ao gerar resposta: {e}")
    print(f"   - Tipo do erro: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("OK: DIAGNOSTICO COMPLETO - TUDO FUNCIONANDO!")
print("=" * 60)
print("\nSe o Gemini nao esta funcionando no app, verifique:")
print("1. Se o servidor Flask esta rodando com as mesmas variaveis de ambiente")
print("2. Se ha erros nos logs do servidor")
print("3. Se o arquivo .env esta na raiz do projeto (nao na pasta backend)")

