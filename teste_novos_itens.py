#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste específico para validar que os novos itens são encontrados corretamente.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app import ChatbotPuerperio

chatbot = ChatbotPuerperio(gemini_client_param=None)

print("\n" + "="*70)
print("🧪 TESTE DE NOVOS ITENS ADICIONADOS")
print("="*70 + "\n")

testes = [
    {
        "pergunta": "Como estabelecer rotina de sono para o bebê?",
        "categoria_esperada": "sono_bebe",
        "palavras_esperadas": ["rotina", "sono", "bebê"]
    },
    {
        "pergunta": "Meu bebê está com febre. O que fazer?",
        "categoria_esperada": "bebe",
        "palavras_esperadas": ["febre", "bebê"]
    },
    {
        "pergunta": "Como usar bomba de leite?",
        "categoria_esperada": "amamentacao",
        "palavras_esperadas": ["bomba", "leite"]
    },
    {
        "pergunta": "Estou muito ansiosa. É normal?",
        "categoria_esperada": "saude_mental",
        "palavras_esperadas": ["ansiosa", "normal"]
    },
    {
        "pergunta": "Quais alimentos ajudam na produção de leite?",
        "categoria_esperada": "alimentacao",
        "palavras_esperadas": ["alimentos", "leite", "produção"]
    },
    {
        "pergunta": "Como fazer exercícios de Kegel?",
        "categoria_esperada": "exercicios",
        "palavras_esperadas": ["exercícios", "Kegel"]
    }
]

passou = 0
total = len(testes)

for i, teste in enumerate(testes):
    print(f"\n{'='*70}")
    print(f"🧪 TESTE {i+1}: {teste['pergunta']}")
    print(f"{'='*70}\n")
    
    start_time = time.perf_counter()
    resposta, categoria, similaridade = chatbot.buscar_resposta_local(teste['pergunta'])
    end_time = time.perf_counter()
    
    tempo = (end_time - start_time) * 1000
    
    print(f"⏱️  Tempo: {tempo:.2f}ms")
    print(f"📁 Categoria: {categoria}")
    print(f"📊 Similaridade: {similaridade:.3f}")
    print(f"📏 Resposta: {resposta[:100] if resposta else 'N/A'}...")
    
    # Validação
    categoria_ok = categoria == teste['categoria_esperada']
    palavras_ok = all(palavra.lower() in resposta.lower() for palavra in teste['palavras_esperadas']) if resposta else False
    
    if categoria_ok and palavras_ok and resposta:
        print(f"✅ PASSOU!")
        passou += 1
    else:
        print(f"⚠️  ATENÇÃO: Categoria esperada: {teste['categoria_esperada']}, Recebida: {categoria}")

print(f"\n{'='*70}")
print(f"📊 RESULTADO: {passou}/{total} testes passaram ({passou/total*100:.0f}%)")
print(f"{'='*70}\n")

