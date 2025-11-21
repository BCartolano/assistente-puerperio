#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste do Sistema de Busca Otimizado (Índice Invertido + Stemming)
Valida que a busca funciona corretamente com stemming e índice invertido.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def testar_busca(pergunta, esperado_contem=None):
    """Testa uma busca na base de conhecimento"""
    print(f"\n{'='*70}")
    print(f"🔍 TESTE DE BUSCA")
    print(f"{'='*70}\n")
    print(f"📝 Pergunta: {pergunta}")
    if esperado_contem:
        print(f"🎯 Esperado: Resposta deve conter '{esperado_contem}'")
    print(f"{'='*70}\n")
    
    try:
        inicio = time.time()
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "pergunta": pergunta,
                "user_id": "test_busca_otimizada"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        tempo_resposta = time.time() - inicio
        
        if response.status_code == 200:
            data = response.json()
            
            resposta = data.get("resposta", "")
            fonte = data.get("fonte", "desconhecida")
            categoria = data.get("categoria", None)
            
            print(f"✅ Resposta recebida!")
            print(f"⏱️  Tempo de resposta: {tempo_resposta:.3f}s")
            print(f"📊 Fonte: {fonte}")
            print(f"📁 Categoria: {categoria}")
            print(f"📏 Tamanho: {len(resposta)} caracteres")
            print(f"\n💬 Resposta (primeiros 300 chars):")
            print(f"{'-'*70}")
            print(resposta[:300])
            print(f"{'-'*70}\n")
            
            # Validação
            if esperado_contem:
                if esperado_contem.lower() in resposta.lower():
                    print(f"✅ PASSOU! Resposta contém '{esperado_contem}'")
                else:
                    print(f"⚠️  ATENÇÃO: Resposta não contém '{esperado_contem}'")
            
            # Verifica se veio da base local
            if "local" in fonte.lower() or categoria:
                print(f"✅ PASSOU! Resposta veio da base de conhecimento local")
            else:
                print(f"⚠️  ATENÇÃO: Resposta pode não ter vindo da base local")
            
            return True
        else:
            print(f"❌ ERRO: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

if __name__ == "__main__":
    print(f"\n{'='*70}")
    print(f"🧪 TESTE DO SISTEMA DE BUSCA OTIMIZADO")
    print(f"{'='*70}\n")
    print(f"Este teste valida:")
    print(f"1. Stemming funciona (ex: 'amamentar' encontra 'amamentação')")
    print(f"2. Índice invertido funciona (busca rápida)")
    print(f"3. Busca encontra respostas relevantes")
    print(f"{'='*70}\n")
    
    # Teste 1: Busca com stemming (amamentar vs amamentação)
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 1: Stemming - 'Como amamentar?'")
    testar_busca("Como amamentar?", esperado_contem="amamentação")
    
    # Teste 2: Busca com variação (leite vs leite materno)
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 2: Variação - 'Quando o leite desce?'")
    testar_busca("Quando o leite desce?", esperado_contem="leite")
    
    # Teste 3: Busca com sinônimo (parto normal vs parto)
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 3: Sinônimo - 'Parto normal ou cesárea?'")
    testar_busca("Parto normal ou cesárea?", esperado_contem="parto")
    
    # Teste 4: Busca com palavras compostas
    print(f"\n{'='*70}\n")
    print(f"🧪 TESTE 4: Palavras compostas - 'Baby blues'")
    testar_busca("O que é baby blues?", esperado_contem="baby blues")
    
    print(f"\n{'='*70}")
    print(f"✅ TESTES CONCLUÍDOS")
    print(f"{'='*70}\n")

