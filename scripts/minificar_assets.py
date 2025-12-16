#!/usr/bin/env python3
"""
Script para minificar CSS e JavaScript automaticamente
Uso: python scripts/minificar_assets.py
"""

import os
import re
import sys
from pathlib import Path

def minify_css(css_content):
    """Minifica CSS removendo espaços, comentários e quebras de linha"""
    # Remove comentários
    css = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # Remove espaços extras
    css = re.sub(r'\s+', ' ', css)
    # Remove espaços antes e depois de caracteres especiais
    css = re.sub(r'\s*([{}:;,])\s*', r'\1', css)
    # Remove espaços no início e fim
    css = css.strip()
    return css

def minify_js(js_content):
    """Minifica JavaScript básico (remove comentários e espaços extras)"""
    # Remove comentários de linha
    js = re.sub(r'//.*', '', js_content)
    # Remove comentários de bloco
    js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)
    # Remove espaços extras (cuidado com strings)
    js = re.sub(r'\s+', ' ', js)
    # Remove espaços antes e depois de operadores (cuidado)
    js = re.sub(r'\s*([=+\-*/%<>!&|,;:{}()\[\]])\s*', r'\1', js)
    return js.strip()

def main():
    """Função principal"""
    # Caminhos
    base_dir = Path(__file__).parent.parent
    static_dir = base_dir / 'backend' / 'static'
    css_file = static_dir / 'css' / 'style.css'
    js_file = static_dir / 'js' / 'chat.js'
    
    print("=" * 50)
    print("MINIFICADOR DE ASSETS")
    print("=" * 50)
    print()
    
    # Minificar CSS
    if css_file.exists():
        print(f"Minificando CSS: {css_file.name}")
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        original_size = len(css_content)
        minified_css = minify_css(css_content)
        new_size = len(minified_css)
        
        # Salvar minificado
        css_min_file = static_dir / 'css' / 'style.min.css'
        with open(css_min_file, 'w', encoding='utf-8') as f:
            f.write(minified_css)
        
        reduction = ((original_size - new_size) / original_size) * 100
        print(f"  [OK] Original: {original_size:,} bytes")
        print(f"  [OK] Minificado: {new_size:,} bytes")
        print(f"  [OK] Reducao: {reduction:.1f}%")
        print()
    else:
        print(f"[AVISO] CSS nao encontrado: {css_file}")
        print()
    
    # Minificar JavaScript
    if js_file.exists():
        print(f"Minificando JavaScript: {js_file.name}")
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        original_size = len(js_content)
        minified_js = minify_js(js_content)
        new_size = len(minified_js)
        
        # Salvar minificado
        js_min_file = static_dir / 'js' / 'chat.min.js'
        with open(js_min_file, 'w', encoding='utf-8') as f:
            f.write(minified_js)
        
        reduction = ((original_size - new_size) / original_size) * 100
        print(f"  [OK] Original: {original_size:,} bytes")
        print(f"  [OK] Minificado: {new_size:,} bytes")
        print(f"  [OK] Reducao: {reduction:.1f}%")
        print()
    else:
        print(f"[AVISO] JavaScript nao encontrado: {js_file}")
        print()
    
    print("=" * 50)
    print("[OK] Minificacao concluida!")
    print("=" * 50)
    print()
    print("PROXIMOS PASSOS:")
    print("1. Atualizar templates para usar arquivos .min.css e .min.js")
    print("2. Testar se tudo funciona corretamente")
    print("3. Reiniciar o servidor")
    print()

if __name__ == '__main__':
    main()
