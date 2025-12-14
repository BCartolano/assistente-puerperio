#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de verificação de configuração"""

import sys
import os

# Configura encoding UTF-8 para Windows (melhorado para PowerShell)
if sys.platform == 'win32':
    # Define variável de ambiente ANTES de qualquer operação de I/O
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'  # Usa UTF-8 nativo no Windows
    
    # Tenta configurar o console para UTF-8 (se disponível)
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        # Se não conseguir reconfigurar, apenas usa a variável de ambiente
        pass
    
    # Tenta configurar o console do Windows diretamente (Python 3.7+)
    try:
        import io
        if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if hasattr(sys.stderr, 'buffer') and sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except (AttributeError, ValueError, OSError):
        # Se não conseguir, continua com a configuração padrão
        pass

from dotenv import load_dotenv

print('='*60)
print('VERIFICACAO FINAL DE CONFIGURACAO')
print('='*60)

load_dotenv()

print(f'\nVariaveis de Ambiente:')
print(f'  SECRET_KEY: {"[OK] Configurada" if os.getenv("SECRET_KEY") else "[ERRO] Faltando"}')
print(f'  USE_AI: {os.getenv("USE_AI", "nao definido")}')
print(f'  FLASK_ENV: {os.getenv("FLASK_ENV", "nao definido")}')
print(f'  PORT: {os.getenv("PORT", "nao definido")}')
print(f'  BASE_URL: {os.getenv("BASE_URL", "nao definido")}')

print(f'\nBibliotecas:')
try:
    from openai import OpenAI
    print('  [OK] openai instalado e funcionando')
except Exception as e:
    print(f'  [ERRO] openai: {e}')

try:
    import nltk
    from nltk.stem import RSLPStemmer
    print('  [OK] nltk instalado e funcionando')
except Exception as e:
    print(f'  [ERRO] nltk: {e}')

print(f'\nEmail:')
if os.getenv('MAIL_USERNAME') and os.getenv('MAIL_PASSWORD'):
    print('  [OK] Configurado')
else:
    print('  [AVISO] Nao configurado (opcional - emails serao logados no console)')

print(f'\nOpenAI API:')
if os.getenv('OPENAI_API_KEY'):
    print('  [OK] OPENAI_API_KEY configurada')
else:
    print('  [AVISO] OPENAI_API_KEY nao configurada (opcional)')

print('='*60)
print('[OK] Configuracao concluida!')
print('='*60)

