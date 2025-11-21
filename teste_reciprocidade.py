#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste específico para validar a melhoria de reciprocidade da Sophia
Testa se respostas sobre a Sophia estão detalhadas e demonstram reciprocidade
"""

import requests
import json
import time

# URL do servidor (ajuste se necessário)
BASE_URL = "http://localhost:5000"

def testar_reciprocidade(pergunta, user_id="test_reciprocidade"):
    """Testa uma pergunta sobre reciprocidade no chat da Sophia"""
    print(f"\n{'='*70}")
    print(f"🧪 TESTE DE RECIPROCIDADE")
    print(f"{'='*70}\n")
    print(f"📝 Pergunta: {pergunta}")
    print(f"{'='*70}\n")
    
    try:
        # Faz requisição para a API
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
            alerta_ativo = data.get("alerta_ativo", False)
            
            print(f"✅ Resposta recebida!")
            print(f"📊 Fonte: {fonte}")
            print(f"📏 Tamanho: {len(resposta)} caracteres")
            print(f"🔢 Palavras: {len(resposta.split())} palavras")
            print(f"⚠️ Alerta ativo: {alerta_ativo}")
            print(f"\n💬 Resposta da Sophia:")
            print(f"{'-'*70}")
            print(resposta)
            print(f"{'-'*70}\n")
            
            # Análise detalhada da resposta
            print(f"📈 ANÁLISE DETALHADA:\n")
            
            # 1. Verifica se é longa e detalhada
            print(f"1️⃣ TAMANHO DA RESPOSTA:")
            if len(resposta) >= 300:
                print(f"   ✅ EXCELENTE! Resposta MUITO LONGA ({len(resposta)} caracteres) - Esperado: ≥200-300")
                print(f"   🎯 Status: PASSOU - Resposta está dentro do esperado para reciprocidade")
            elif len(resposta) >= 200:
                print(f"   ✅ BOM! Resposta LONGA ({len(resposta)} caracteres) - Esperado: ≥200-300")
                print(f"   🎯 Status: PASSOU - Resposta está no mínimo esperado para reciprocidade")
            elif len(resposta) >= 150:
                print(f"   ⚠️ ATENÇÃO! Resposta MÉDIA ({len(resposta)} caracteres) - Esperado: ≥200-300")
                print(f"   🎯 Status: PARCIALMENTE - Resposta está um pouco abaixo do esperado")
            else:
                print(f"   ❌ FALHOU! Resposta CURTA ({len(resposta)} caracteres) - Esperado: ≥200-300")
                print(f"   🎯 Status: FALHOU - Resposta está muito curta para demonstrar reciprocidade")
            
            # 2. Verifica tom empático e reciprocidade
            print(f"\n2️⃣ TOM EMPÁTICO E RECIPROCIDADE:")
            palavras_reciprocidade = ['meu dia', 'estou', 'sendo', 'aprendendo', 'conversando', 
                                     'pessoas', 'incríveis', 'feliz', 'gratificante', 'conectada',
                                     'útil', 'sinto', 'sentindo', 'me ensina', 'me deixa']
            tem_reciprocidade = any(palavra in resposta.lower() for palavra in palavras_reciprocidade)
            
            if tem_reciprocidade:
                print(f"   ✅ Detectado! Resposta demonstra reciprocidade (compartilha sentimentos/experiências)")
            else:
                print(f"   ⚠️ Não detectado claramente - resposta pode não estar demonstrando reciprocidade")
            
            # 3. Verifica perguntas abertas
            print(f"\n3️⃣ PERGUNTAS ABERTAS:")
            tem_pergunta = '?' in resposta
            num_perguntas = resposta.count('?')
            
            if tem_pergunta and num_perguntas >= 2:
                print(f"   ✅ EXCELENTE! Contém {num_perguntas} perguntas abertas - demonstra interesse genuíno")
            elif tem_pergunta:
                print(f"   ✅ BOM! Contém {num_perguntas} pergunta(s) aberta(s)")
            else:
                print(f"   ⚠️ Não contém perguntas abertas - pode estar faltando retorno do foco para o usuário")
            
            # 4. Verifica detalhamento e desenvolvimento
            print(f"\n4️⃣ DETALHAMENTO E DESENVOLVIMENTO:")
            tem_detalhes = any(palavra in resposta.lower() for palavra in ['cada', 'conversa', 'interação', 
                                                                           'momento', 'especial', 'experiência',
                                                                           'aprender', 'ajudar', 'apoiar'])
            
            if tem_detalhes and len(resposta) >= 200:
                print(f"   ✅ EXCELENTE! Resposta contém detalhes e desenvolve o tema adequadamente")
            elif tem_detalhes:
                print(f"   ⚠️ BOM! Resposta contém detalhes, mas poderia ser mais desenvolvida")
            else:
                print(f"   ⚠️ Resposta pode estar faltando detalhamento")
            
            # 5. Verifica se não é resposta genérica
            print(f"\n5️⃣ ORIGINALIDADE:")
            frases_genericas = ['tudo bem por aí', 'como posso te ajudar', 'em que posso ajudar']
            tem_generica = any(frase in resposta.lower() for frase in frases_genericas)
            
            if not tem_generica:
                print(f"   ✅ BOM! Resposta não contém frases genéricas - parece personalizada")
            else:
                print(f"   ⚠️ Resposta contém frases genéricas - pode estar faltando personalização")
            
            # Resultado final
            print(f"\n{'='*70}")
            print(f"📊 RESULTADO FINAL:")
            print(f"{'='*70}\n")
            
            # Calcula score (0-100)
            score = 0
            if len(resposta) >= 200:
                score += 40
            elif len(resposta) >= 150:
                score += 20
            
            if tem_reciprocidade:
                score += 30
            
            if tem_pergunta:
                score += 15
            
            if tem_detalhes:
                score += 10
            
            if not tem_generica:
                score += 5
            
            print(f"🎯 Score: {score}/100\n")
            
            if score >= 80:
                print(f"✅✅✅ EXCELENTE! A melhoria de reciprocidade está funcionando PERFEITAMENTE!")
                print(f"   A resposta está detalhada, demonstra reciprocidade e mantém o estilo de amiga próxima.")
            elif score >= 60:
                print(f"✅✅ BOM! A melhoria de reciprocidade está funcionando BEM!")
                print(f"   A resposta está adequada, mas pode ser melhorada com mais detalhamento.")
            elif score >= 40:
                print(f"⚠️ PARCIAL! A melhoria de reciprocidade está funcionando PARCIALMENTE.")
                print(f"   A resposta precisa ser mais detalhada para demonstrar reciprocidade adequadamente.")
            else:
                print(f"❌ FALHOU! A melhoria de reciprocidade NÃO está funcionando como esperado.")
                print(f"   A resposta está muito curta e não demonstra reciprocidade adequadamente.")
            
            print(f"\n{'='*70}\n")
            
            return {
                "sucesso": score >= 60,
                "score": score,
                "tamanho": len(resposta),
                "fonte": fonte,
                "resposta": resposta
            }
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Resposta: {response.text}")
            return {"sucesso": False, "erro": f"Status {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO: Não foi possível conectar ao servidor em {BASE_URL}")
        print(f"💡 Certifique-se de que o servidor está rodando:")
        print(f"   python start.py")
        return {"sucesso": False, "erro": "Servidor não acessível"}
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"sucesso": False, "erro": str(e)}

def main():
    """Executa teste de reciprocidade"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║  🧪 TESTE DE VALIDAÇÃO - RECIPROCIDADE                                  ║
║  Testando se respostas sobre a Sophia estão detalhadas e demonstram     ║
║  reciprocidade adequada (mínimo 200-300 caracteres)                     ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Verifica se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/teste", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!\n")
        else:
            print("⚠️ Servidor respondeu, mas com status diferente de 200\n")
    except:
        print("❌ Servidor não está acessível!")
        print("💡 Inicie o servidor primeiro:")
        print("   python start.py\n")
        return
    
    # Lista de perguntas sobre reciprocidade
    perguntas_reciprocidade = [
        "Sophia, como foi o seu dia hoje?",
        "Como você está?",
        "Sophia, como você está se sentindo?",
        "Como foi seu dia?",
        "Sophia, você está bem?"
    ]
    
    resultados = []
    
    for i, pergunta in enumerate(perguntas_reciprocidade, 1):
        print(f"\n{'#'*70}")
        print(f"TESTE {i}/{len(perguntas_reciprocidade)}")
        print(f"{'#'*70}")
        
        # Usa user_id único para cada teste para evitar interferência de histórico
        import uuid
        user_id = f"test_reciprocidade_{uuid.uuid4().hex[:8]}"
        
        resultado = testar_reciprocidade(pergunta, user_id=user_id)
        resultados.append((pergunta, resultado))
        
        # Aguarda um pouco entre testes
        if i < len(perguntas_reciprocidade):
            time.sleep(3)
    
    # Resumo final
    print(f"\n\n{'='*70}")
    print("📊 RESUMO FINAL DOS TESTES")
    print(f"{'='*70}\n")
    
    sucessos = sum(1 for _, r in resultados if r.get("sucesso", False))
    total = len(resultados)
    score_medio = sum(r.get("score", 0) for _, r in resultados) / total if total > 0 else 0
    
    for pergunta, resultado in resultados:
        status = "✅" if resultado.get("sucesso", False) else "❌"
        score = resultado.get("score", 0)
        tamanho = resultado.get("tamanho", 0)
        print(f"{status} {pergunta[:50]}...")
        print(f"   Score: {score}/100 | Tamanho: {tamanho} chars | Fonte: {resultado.get('fonte', 'N/A')}")
        print()
    
    print(f"{'='*70}")
    print(f"✅ Testes bem-sucedidos: {sucessos}/{total}")
    print(f"📊 Score médio: {score_medio:.1f}/100")
    print(f"{'='*70}\n")
    
    if sucessos == total and score_medio >= 80:
        print("🎉🎉🎉 PERFEITO! Todas as melhorias de reciprocidade estão funcionando EXCELENTEMENTE!")
        print("   As respostas estão detalhadas, demonstram reciprocidade e mantêm o estilo de amiga próxima.")
    elif sucessos == total:
        print("🎉 MUITO BOM! As melhorias de reciprocidade estão funcionando BEM!")
        print("   As respostas estão adequadas, mas podem ser melhoradas com mais detalhamento.")
    elif sucessos >= total * 0.7:
        print("⚠️ BOM! A maioria das melhorias de reciprocidade está funcionando.")
        print("   Algumas respostas precisam ser mais detalhadas.")
    else:
        print("❌ ATENÇÃO! As melhorias de reciprocidade precisam de ajustes.")
        print("   Muitas respostas estão muito curtas e não demonstram reciprocidade adequadamente.")

if __name__ == "__main__":
    main()

