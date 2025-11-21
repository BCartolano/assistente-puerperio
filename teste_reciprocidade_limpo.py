#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste limpo - sem histórico prévio
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:5000"

def testar_pergunta(pergunta):
    """Testa uma pergunta com user_id único para evitar histórico"""
    user_id = f"teste_limpo_{uuid.uuid4().hex[:8]}"
    
    print(f"\n{'='*70}")
    print(f"🧪 TESTE LIMPO (user_id único: {user_id})")
    print(f"{'='*70}\n")
    print(f"📝 Pergunta: {pergunta}")
    print(f"{'='*70}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "pergunta": pergunta,
                "user_id": user_id
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            resposta = data.get("resposta", "")
            fonte = data.get("fonte", "desconhecida")
            
            print(f"✅ Resposta recebida!")
            print(f"📊 Fonte: {fonte}")
            print(f"📏 Tamanho: {len(resposta)} caracteres")
            print(f"🔢 Palavras: {len(resposta.split())} palavras")
            print(f"\n💬 Resposta da Sophia:")
            print(f"{'-'*70}")
            print(resposta)
            print(f"{'-'*70}\n")
            
            # Análise
            if fonte in ["resposta_alternativa_anti_repeticao", "resposta_variada"]:
                print(f"❌❌❌ PROBLEMA CRÍTICO: Resposta veio de sistema de anti-repetição!")
                print(f"   Fonte: {fonte}")
                print(f"   Isso significa que a detecção de reciprocidade NÃO funcionou ou foi ignorada.")
                print(f"   A pergunta deveria gerar resposta do Gemini, não do sistema de anti-repetição.")
            elif fonte.startswith("gemini") or fonte == "resposta_reciprocidade_fallback_detalhada":
                if len(resposta) >= 200:
                    print(f"✅✅✅ SUCESSO: Resposta adequada com {len(resposta)} caracteres")
                    print(f"   Fonte: {fonte}")
                    print(f"   A detecção de reciprocidade funcionou corretamente!")
                else:
                    print(f"⚠️ PARCIAL: Resposta do Gemini mas curta ({len(resposta)} chars)")
                    print(f"   Fonte: {fonte}")
                    print(f"   Esperado: ≥200-300 caracteres")
            else:
                print(f"⚠️ Fonte: {fonte}")
                print(f"   Verificar se é apropriada para pergunta de reciprocidade")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║  🧪 TESTE LIMPO - RECIPROCIDADE (SEM HISTÓRICO)                         ║
║  Testa com user_id único para evitar interferência de histórico         ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Testa apenas uma pergunta com user_id único
    testar_pergunta("Sophia, como foi o seu dia hoje?")

