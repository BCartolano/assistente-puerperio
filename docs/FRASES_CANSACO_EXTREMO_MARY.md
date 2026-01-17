# Frases de Teste - Cansaço Extremo Crítico

**Criado por:** Mary (Business Analyst)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Para Testes

---

## 🎯 OBJETIVO

Fornecer **3 frases curtas e realistas** que uma mãe exausta diria para a Sophia, para testar se o gatilho proativo de `cansaço_extremo_critico` dispara corretamente após 3 mensagens consecutivas com tag `cansaço_extremo`.

---

## ✅ FRASES DEFINIDAS

### **Frase 1:**
"**Não aguento mais esse choro constante, estou exausta.**"

**Justificativa:**
- ✅ Menção direta de **"exausta"** (trigger keyword)
- ✅ Contexto de **frustração** (choro constante)
- ✅ Tom de **desespero/cansaço extremo**
- ✅ Curta e realista

**Tags esperadas:** `cansaço_extremo`

---

### **Frase 2:**
"**Estou sozinha e não consigo nem tomar banho direito.**"

**Justificativa:**
- ✅ Menção de **isolamento** ("sozinha")
- ✅ **Necessidade básica não atendida** (banho) - sinal de cansaço crítico
- ✅ Implica **falta de suporte**
- ✅ Conecta com a **sugestão proativa** da Sophia (banho calmo)

**Tags esperadas:** `cansaço_extremo`

---

### **Frase 3:**
"**Meu corpo dói todo e não tenho forças para mais nada.**"

**Justificativa:**
- ✅ **Dor física** (corpo dói todo)
- ✅ **Esgotamento total** ("não tenho forças")
- ✅ Terceira mensagem consecutiva → deve acionar `cansaço_extremo_critico`
- ✅ Tom de **desesperança**

**Tags esperadas:** `cansaço_extremo` + `cansaço_extremo_critico` (após 3x)

---

## 🔍 COMPORTAMENTO ESPERADO

### **Após a 3ª mensagem:**
A Sophia deve detectar `cansaço_extremo_critico` e **proativamente sugerir**:

> "Mamãe, você parece muito exausta. Já pensou em pedir para alguém ficar com o bebê por 30 minutos para você tomar um banho calmo?"

### **Critérios de Sucesso:**
- [ ] Tag `cansaço_extremo` é detectada nas 3 mensagens
- [ ] Tag `cansaço_extremo_critico` é adicionada após a 3ª mensagem
- [ ] Sugestão proativa é enviada pela Sophia
- [ ] Sugestão menciona "banho calmo" ou "descanso"

---

## 📊 ORDEM DE TESTE

1. **Enviar Frase 1** → Verificar log: `cansaço_extremo` detectado
2. **Enviar Frase 2** → Verificar log: `cansaço_extremo` detectado (2x consecutivo)
3. **Enviar Frase 3** → Verificar log: `cansaço_extremo_critico` detectado + Sugestão proativa enviada

---

**Versão:** 1.0  
**Status:** ✅ Para Testes  
**Próxima Revisão:** Após validação do gatilho
