#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se todas as dependências foram instaladas corretamente
"""
import sys

def verificar_modulo(nome, versao_atributo=None):
    """Verifica se um módulo está instalado"""
    try:
        modulo = __import__(nome)
        if versao_atributo:
            versao = getattr(modulo, versao_atributo, "N/A")
            print(f"[OK] {nome}: {versao}")
        else:
            print(f"[OK] {nome}: instalado")
        return True
    except ImportError:
        print(f"[ERRO] {nome}: NAO instalado")
        return False

print("=" * 50)
print("Verificando instalação das dependências")
print("=" * 50)

todas_ok = True

# Dependências principais
print("\n[Dependencias Principais]")
todas_ok &= verificar_modulo("flask", "__version__")
todas_ok &= verificar_modulo("openai", "__version__")
todas_ok &= verificar_modulo("nltk", "__version__")
todas_ok &= verificar_modulo("bcrypt", "__version__")
todas_ok &= verificar_modulo("flask_login")
todas_ok &= verificar_modulo("flask_mail")
todas_ok &= verificar_modulo("flask_compress")
todas_ok &= verificar_modulo("gunicorn", "__version__")
todas_ok &= verificar_modulo("dotenv")

# Outras dependências importantes
print("\n[Outras Dependencias]")
todas_ok &= verificar_modulo("pydantic", "__version__")
todas_ok &= verificar_modulo("httpx", "__version__")
todas_ok &= verificar_modulo("jinja2", "__version__")
todas_ok &= verificar_modulo("werkzeug", "__version__")

# Verificar dados do NLTK
print("\n[Dados do NLTK]")
try:
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
        print("[OK] punkt: instalado")
    except LookupError:
        print("[ERRO] punkt: NAO instalado")
        todas_ok = False
    
    try:
        nltk.data.find('corpora/stopwords')
        print("[OK] stopwords: instalado")
    except LookupError:
        print("[ERRO] stopwords: NAO instalado")
        todas_ok = False
except ImportError:
    print("[ERRO] NLTK nao esta instalado")
    todas_ok = False

print("\n" + "=" * 50)
if todas_ok:
    print("[OK] TODAS as dependencias foram instaladas com sucesso!")
    sys.exit(0)
else:
    print("[ERRO] Algumas dependencias estao faltando")
    print("Execute: pip install -r requirements.txt")
    sys.exit(1)
