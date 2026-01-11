#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificação de Deploy Mobile
Verifica se todos os arquivos estáticos necessários para mobile estão sendo servidos corretamente
"""

import requests
import sys
import os

# Cores para output (Windows PowerShell)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

# URL base do servidor
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]

print("=" * 60)
print("Verificação de Deploy Mobile - Sophia")
print("=" * 60)
print(f"URL Base: {BASE_URL}")
print("")

# Lista de arquivos estáticos críticos para mobile
STATIC_FILES = [
    # JavaScript Mobile
    '/static/js/mobile-navigation.js',
    '/static/js/toast-notification.js',
    '/static/js/api-client.js',
    '/static/js/chat.js',
    '/static/js/vaccination-timeline.js',
    '/static/js/sidebar-content.js',
    
    # CSS Mobile
    '/static/css/style.css',
    '/static/css/vaccination-timeline.css',
    
    # HTML
    '/',
    
    # API Endpoints críticos
    '/api/user',
    '/api/chat',
    '/api/vaccination/status',
    '/api/vaccination/mark-done',
]

# Resultados
results = {
    'success': [],
    'failed': [],
    'warnings': []
}

# Verifica cada arquivo
for file_path in STATIC_FILES:
    url = f"{BASE_URL}{file_path}"
    
    try:
        response = requests.get(url, timeout=5, allow_redirects=False)
        
        if response.status_code == 200:
            # Verifica se não está vazio (para JS/CSS)
            if file_path.endswith(('.js', '.css')):
                if len(response.content) < 100:
                    results['warnings'].append({
                        'file': file_path,
                        'status': response.status_code,
                        'size': len(response.content),
                        'message': 'Arquivo muito pequeno (possível erro 404 ou vazio)'
                    })
                    print_warning(f"{file_path} - Arquivo muito pequeno ({len(response.content)} bytes)")
                else:
                    results['success'].append({
                        'file': file_path,
                        'status': response.status_code,
                        'size': len(response.content)
                    })
                    print_success(f"{file_path} ({len(response.content)} bytes)")
            else:
                results['success'].append({
                    'file': file_path,
                    'status': response.status_code
                })
                print_success(f"{file_path}")
                
        elif response.status_code == 404:
            results['failed'].append({
                'file': file_path,
                'status': response.status_code,
                'message': 'Arquivo não encontrado (404)'
            })
            print_error(f"{file_path} - 404 NOT FOUND")
            
        elif response.status_code in [301, 302, 307, 308]:
            results['warnings'].append({
                'file': file_path,
                'status': response.status_code,
                'message': f'Redirecionamento (código {response.status_code})'
            })
            print_warning(f"{file_path} - Redirecionamento ({response.status_code})")
            
        else:
            results['failed'].append({
                'file': file_path,
                'status': response.status_code,
                'message': f'Erro HTTP {response.status_code}'
            })
            print_error(f"{file_path} - HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        results['failed'].append({
            'file': file_path,
            'status': 'N/A',
            'message': 'Erro de conexão - Servidor não está rodando ou URL incorreta'
        })
        print_error(f"{file_path} - ERRO DE CONEXÃO (servidor não está rodando?)")
        break  # Se não consegue conectar, para os testes
        
    except requests.exceptions.Timeout:
        results['failed'].append({
            'file': file_path,
            'status': 'TIMEOUT',
            'message': 'Timeout na requisição (servidor muito lento ou travado)'
        })
        print_error(f"{file_path} - TIMEOUT")
        
    except Exception as e:
        results['failed'].append({
            'file': file_path,
            'status': 'ERROR',
            'message': str(e)
        })
        print_error(f"{file_path} - ERRO: {e}")

# Resumo
print("")
print("=" * 60)
print("RESUMO")
print("=" * 60)
print(f"{Colors.GREEN}✓ Sucessos: {len(results['success'])}{Colors.RESET}")
print(f"{Colors.RED}✗ Falhas: {len(results['failed'])}{Colors.RESET}")
print(f"{Colors.YELLOW}⚠ Avisos: {len(results['warnings'])}{Colors.RESET}")
print("")

# Se houver falhas, lista
if results['failed']:
    print("ARQUIVOS COM ERRO:")
    for item in results['failed']:
        print(f"  ✗ {item['file']} - {item['message']}")
    print("")

# Se houver avisos, lista
if results['warnings']:
    print("AVISOS:")
    for item in results['warnings']:
        print(f"  ⚠ {item['file']} - {item['message']}")
    print("")

# Verifica se todos os arquivos críticos passaram
CRITICAL_FILES = [
    '/static/js/mobile-navigation.js',
    '/static/js/toast-notification.js',
    '/static/js/api-client.js',
    '/static/js/chat.js',
]

critical_failed = [f for f in results['failed'] if f['file'] in CRITICAL_FILES]

if critical_failed:
    print_error("ERRO CRÍTICO: Arquivos essenciais não estão disponíveis!")
    print_error("O deploy mobile não funcionará corretamente.")
    sys.exit(1)
elif results['failed']:
    print_warning("Alguns arquivos não estão disponíveis, mas os críticos estão OK.")
    sys.exit(0)
else:
    print_success("Todos os arquivos estão sendo servidos corretamente!")
    print_success("Deploy mobile está pronto para testes!")
    sys.exit(0)
