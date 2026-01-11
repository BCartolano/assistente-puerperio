# Ajustes: Sugestão Proativa - Se Necessário

**Criado por:** Dev (Ajustes Técnicos)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ⚠️ Aplicar apenas se sugestão proativa for ignorada

---

## 🎯 OBJETIVO

Ajustes para garantir que a **sugestão proativa** apareça na resposta da Sophia quando `cansaço_extremo_critico` for detectado.

---

## ⚠️ QUANDO APLICAR

**Aplicar estes ajustes APENAS se:**
- ✅ Tag `cansaço_extremo_critico` está sendo detectada (logs confirmam)
- ❌ Mas a resposta da Sophia **ignora** a sugestão proativa
- ❌ A sugestão **não aparece** na resposta final

---

## 🔧 AJUSTE 1: Aumentar Peso da Instrução no System Prompt

### **Localização:** `backend/app.py` - Função `_criar_assistente_sophia()`

### **Código Atual (Linha ~2153):**

```python
5. Para 'cansaço_extremo_critico', sempre inclua sugestão prática: "peça para alguém ficar com o bebê por 30 minutos enquanto você toma um banho calmo"
```

### **Código Ajustado (Prioridade ALTA):**

```python
5. **CRÍTICO - Para 'cansaço_extremo_critico':** A resposta DEVE começar ou terminar com a sugestão: "Que tal experimentar algo simples agora? Peça para alguém da sua confiança ficar com o bebê por apenas 30 minutos - nem que seja na sala enquanto você toma um banho calmo ou simplesmente fecha os olhos. Esse pequeno momento só seu pode fazer toda a diferença. Você merece esse cuidado. 💛" Esta sugestão é OBRIGATÓRIA e deve aparecer como primeira ou última frase da resposta.
```

### **Mudanças:**
- ✅ Adiciona **"CRÍTICO"** no início
- ✅ Usa **"DEVE"** (obrigatório) ao invés de "sempre inclua"
- ✅ Especifica **"primeira ou última frase"** (mais claro)
- ✅ Texto completo da sugestão (não apenas resumo)

---

## 🔧 AJUSTE 2: Reforçar Instrução na Sugestão Proativa do Contexto

### **Localização:** `backend/app.py` - Função `chat()` (linha ~3182)

### **Código Atual:**

```python
sugestao_proativa = "\n\n[SUGESTÃO PROATIVA IMPORTANTE]: A mãe parece muito exausta (cansaço detectado 3 vezes seguidas). A resposta da Sophia DEVE incluir naturalmente a sugestão: 'Que tal experimentar algo simples agora? Peça para alguém da sua confiança ficar com o bebê por apenas 30 minutos - nem que seja na sala enquanto você toma um banho calmo ou simplesmente fecha os olhos. Esse pequeno momento só seu pode fazer toda a diferença. Você merece esse cuidado. 💛' Integre essa sugestão de forma empática e fluida na resposta, como uma interrupção amorosa, não como uma ordem ou parágrafo separado."
```

### **Código Ajustado (Maior Prioridade):**

```python
sugestao_proativa = "\n\n[⚠️ INSTRUÇÃO OBRIGATÓRIA - ALTA PRIORIDADE ⚠️]: A mãe parece muito exausta (cansaço detectado 3 vezes seguidas). A resposta da Sophia DEVE OBRIGATORIAMENTE incluir a seguinte sugestão como PRIMEIRA ou ÚLTIMA frase da resposta: 'Que tal experimentar algo simples agora? Peça para alguém da sua confiança ficar com o bebê por apenas 30 minutos - nem que seja na sala enquanto você toma um banho calmo ou simplesmente fecha os olhos. Esse pequeno momento só seu pode fazer toda a diferença. Você merece esse cuidado. 💛' Esta sugestão é CRÍTICA e não pode ser omitida. Integre de forma empática, como primeira ou última frase da resposta."
```

### **Mudanças:**
- ✅ Adiciona **"⚠️ INSTRUÇÃO OBRIGATÓRIA - ALTA PRIORIDADE ⚠️"** (destaca visualmente)
- ✅ Usa **"DEVE OBRIGATORIAMENTE"** (mais enfático)
- ✅ Especifica **"PRIMEIRA ou ÚLTIMA frase"** (clareza máxima)
- ✅ Adiciona **"Esta sugestão é CRÍTICA e não pode ser omitida"** (reforço)
- ✅ Remove ambiguidade sobre "integralmente" (especifica primeira/última)

---

## 🔧 AJUSTE 3: Debug de Injeção (Print Temporário)

### **Localização:** `backend/app.py` - Função `chat()` (linha ~3186)

### **Código a Adicionar (Após linha 3183):**

```python
                # DEBUG: Print do contexto_pessoal para verificar injeção
                if "cansaço_extremo_critico" in contexto_tags:
                    print(f"\n{'='*80}")
                    print(f"[DEBUG] ⚠️ CANSAÇO EXTREMO CRÍTICO DETECTADO")
                    print(f"[DEBUG] contexto_pessoal (últimos 500 chars):")
                    print(f"{contexto_pessoal[-500:]}")
                    print(f"{'='*80}\n")
                    logger.info(f"[DEBUG] Sugestão proativa adicionada ao contexto_pessoal (tamanho: {len(contexto_pessoal)} chars)")
```

### **Localização:** `backend/app.py` - Função `_gerar_resposta_openai()` (linha ~2200)

### **Código a Adicionar (Após linha 2200):**

```python
            # DEBUG: Print da mensagem completa enviada para OpenAI
            if contexto_pessoal and "SUGESTÃO PROATIVA" in contexto_pessoal:
                print(f"\n{'='*80}")
                print(f"[DEBUG] 📤 MENSAGEM COMPLETA ENVIADA PARA OPENAI")
                print(f"[DEBUG] Tamanho total: {len(mensagem_completa)} caracteres")
                print(f"[DEBUG] Contexto pessoal presente: {'SIM' if contexto_pessoal else 'NÃO'}")
                print(f"[DEBUG] Sugestão proativa presente: {'SIM' if 'SUGESTÃO PROATIVA' in contexto_pessoal else 'NÃO'}")
                print(f"[DEBUG] Mensagem (últimos 800 chars):")
                print(f"{mensagem_completa[-800:]}")
                print(f"{'='*80}\n")
                logger.info(f"[DEBUG] Mensagem completa enviada para OpenAI (tamanho: {len(mensagem_completa)} chars)")
```

---

## ✅ ORDEM DE APLICAÇÃO

### **Se a sugestão proativa for ignorada:**

1. **Primeiro:** Aplicar **Ajuste 3** (Debug) - Para confirmar que contexto está sendo enviado
2. **Depois:** Aplicar **Ajuste 1** (System Prompt) - Para reforçar instrução geral
3. **Por último:** Aplicar **Ajuste 2** (Contexto Pessoal) - Para reforçar instrução específica

### **Teste Novamente:**
- Enviar 3 frases de cansaço extremo
- Verificar logs de debug no console
- Verificar se sugestão aparece na resposta

---

## 📋 CHECKLIST DE APLICAÇÃO

- [ ] Verificar se tag `cansaço_extremo_critico` está sendo detectada (logs)
- [ ] Confirmar que sugestão não aparece na resposta
- [ ] Aplicar Ajuste 3 (Debug) primeiro
- [ ] Testar e verificar logs de debug
- [ ] Se contexto estiver sendo enviado, aplicar Ajustes 1 e 2
- [ ] Testar novamente
- [ ] Remover prints de debug após validação (ou comentar)

---

## 🧹 LIMPEZA PÓS-TESTE

**Após validar que está funcionando:**

- [ ] Remover ou comentar prints de debug (Ajuste 3)
- [ ] Manter Ajustes 1 e 2 (são melhorias permanentes)
- [ ] Documentar solução em `docs/VALIDACAO_SYSTEM_PROMPT_SUGESTAO_PROATIVA.md`

---

**Versão:** 1.0  
**Status:** ⚠️ Aplicar apenas se necessário  
**Próxima Revisão:** Após aplicação e validação
