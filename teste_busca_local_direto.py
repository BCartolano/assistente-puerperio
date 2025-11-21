#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste DIRETO do Sistema de Busca Local Otimizado
Testa APENAS a busca local (sem passar pelo Gemini) para medir precisão e velocidade reais.
"""

import sys
import os
import time
import json

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importa após adicionar ao path
from app import ChatbotPuerperio, base_conhecimento

def testar_busca_local_direta(pergunta, categoria_esperada=None, palavras_esperadas=None):
    """Testa busca local diretamente (sem Gemini)"""
    print(f"\n{'='*70}")
    print(f"🔍 TESTE DIRETO DE BUSCA LOCAL")
    print(f"{'='*70}\n")
    print(f"📝 Pergunta: {pergunta}")
    if categoria_esperada:
        print(f"🎯 Categoria esperada: {categoria_esperada}")
    if palavras_esperadas:
        print(f"🎯 Palavras esperadas na resposta: {', '.join(palavras_esperadas)}")
    print(f"{'='*70}\n")
    
    # Cria instância do chatbot (inicializa índice invertido)
    chatbot = ChatbotPuerperio()
    
    # Testa busca local diretamente
    inicio = time.time()
    resposta, categoria, similaridade = chatbot.buscar_resposta_local(pergunta)
    tempo_busca = (time.time() - inicio) * 1000  # Converte para milissegundos
    
    # Resultados
    print(f"⏱️  Tempo de busca: {tempo_busca:.2f}ms")
    print(f"📁 Categoria encontrada: {categoria}")
    print(f"📊 Similaridade: {similaridade:.3f}")
    print(f"📏 Tamanho da resposta: {len(resposta) if resposta else 0} caracteres")
    
    if resposta:
        print(f"\n💬 Resposta encontrada (primeiros 200 chars):")
        print(f"{'-'*70}")
        print(resposta[:200])
        print(f"{'-'*70}\n")
    else:
        print(f"\n❌ Nenhuma resposta encontrada\n")
    
    # Validação
    score = 0
    max_score = 100
    
    # 1. Verifica se encontrou resposta
    if resposta:
        print(f"✅ PASSOU! Resposta encontrada")
        score += 30
    else:
        print(f"❌ FALHOU! Nenhuma resposta encontrada")
        return score
    
    # 2. Verifica categoria (se esperada)
    if categoria_esperada:
        if categoria == categoria_esperada:
            print(f"✅ PASSOU! Categoria correta: {categoria}")
            score += 40
        else:
            print(f"⚠️  ATENÇÃO: Categoria diferente. Esperada: {categoria_esperada}, Encontrada: {categoria}")
            score += 20
    
    # 3. Verifica palavras esperadas na resposta
    if palavras_esperadas and resposta:
        palavras_encontradas = 0
        for palavra in palavras_esperadas:
            if palavra.lower() in resposta.lower():
                palavras_encontradas += 1
                print(f"✅ Palavra '{palavra}' encontrada na resposta")
        
        if palavras_encontradas == len(palavras_esperadas):
            print(f"✅ PASSOU! Todas as palavras esperadas encontradas ({palavras_encontradas}/{len(palavras_esperadas)})")
            score += 30
        elif palavras_encontradas > 0:
            print(f"⚠️  PARCIAL: {palavras_encontradas}/{len(palavras_esperadas)} palavras encontradas")
            score += 15
    
    # 4. Verifica velocidade (deve ser < 10ms para busca local)
    if tempo_busca < 10:
        print(f"✅ PASSOU! Busca rápida ({tempo_busca:.2f}ms < 10ms)")
        score += 20
    elif tempo_busca < 50:
        print(f"⚠️  ATENÇÃO: Busca um pouco lenta ({tempo_busca:.2f}ms < 50ms)")
        score += 10
    else:
        print(f"❌ FALHOU! Busca muito lenta ({tempo_busca:.2f}ms > 50ms)")
    
    print(f"\n📊 Score: {score}/100 ({score}%)")
    print(f"{'='*70}\n")
    
    return score

if __name__ == "__main__":
    print(f"\n{'='*70}")
    print(f"🧪 TESTE DIRETO DO SISTEMA DE BUSCA LOCAL OTIMIZADO")
    print(f"{'='*70}\n")
    print(f"Este teste valida APENAS a busca local (sem Gemini):")
    print(f"1. Precisão: Encontra a resposta correta?")
    print(f"2. Velocidade: Busca é rápida (< 10ms)?")
    print(f"3. Stemming: 'amamentar' encontra 'amamentação'?")
    print(f"4. Índice: Busca é O(1) em vez de O(n)?")
    print(f"{'='*70}\n")
    
    resultados = []
    
    # Teste 1: Stemming - "amamentar" deve encontrar "amamentação"
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 1: Stemming - 'Como amamentar?'")
    score1 = testar_busca_local_direta(
        "Como amamentar?",
        categoria_esperada=None,  # Não sabemos a categoria exata
        palavras_esperadas=["amamentação", "amamentar"]
    )
    resultados.append(("Teste 1: Stemming", score1))
    
    # Teste 2: Busca por "leite desce"
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 2: Busca específica - 'Quando o leite desce?'")
    score2 = testar_busca_local_direta(
        "Quando o leite desce?",
        categoria_esperada="leite_demorar_descer",
        palavras_esperadas=["leite", "desce", "descer"]
    )
    resultados.append(("Teste 2: Leite desce", score2))
    
    # Teste 3: Busca por "parto normal"
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 3: Busca específica - 'Parto normal ou cesárea?'")
    score3 = testar_busca_local_direta(
        "Parto normal ou cesárea?",
        categoria_esperada="parto_normal_vs_cesarea",
        palavras_esperadas=["parto", "normal", "cesárea"]
    )
    resultados.append(("Teste 3: Parto normal", score3))
    
    # Teste 4: Busca por "baby blues"
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 4: Busca específica - 'O que é baby blues?'")
    score4 = testar_busca_local_direta(
        "O que é baby blues?",
        categoria_esperada="baby_blues",
        palavras_esperadas=["baby blues", "tristeza"]
    )
    resultados.append(("Teste 4: Baby blues", score4))
    
    # Teste 5: Busca por variação - "amamentação" (testa stemming reverso)
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 5: Stemming reverso - 'Problemas na amamentação'")
    score5 = testar_busca_local_direta(
        "Problemas na amamentação",
        categoria_esperada=None,
        palavras_esperadas=["amamentação", "amamentar"]
    )
    resultados.append(("Teste 5: Stemming reverso", score5))
    
    # Resumo final
    print(f"\n{'='*70}")
    print(f"📊 RESUMO FINAL DOS TESTES")
    print(f"{'='*70}\n")
    
    total_score = sum(score for _, score in resultados)
    max_total = len(resultados) * 100
    porcentagem_total = (total_score / max_total) * 100 if max_total > 0 else 0
    
    for nome, score in resultados:
        status = "✅ PASSOU" if score >= 70 else "⚠️ ATENÇÃO" if score >= 50 else "❌ FALHOU"
        print(f"{nome}: {score}/100 ({status})")
    
    print(f"\n{'='*70}")
    print(f"📊 SCORE TOTAL: {total_score}/{max_total} ({porcentagem_total:.1f}%)")
    
    if porcentagem_total >= 80:
        print(f"✅✅✅ SISTEMA DE BUSCA FUNCIONANDO MUITO BEM!")
    elif porcentagem_total >= 60:
        print(f"✅ SISTEMA DE BUSCA FUNCIONANDO, MAS PODE MELHORAR")
    else:
        print(f"❌ SISTEMA DE BUSCA PRECISA DE AJUSTES")
    
    print(f"{'='*70}\n")

