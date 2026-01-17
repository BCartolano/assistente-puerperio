# Mensagem de Boas-vindas - Sophia Mobile V1.0

**Criado por:** Mary (Business Analyst)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Pronto para Implementação

---

## 🎯 OBJETIVO

Criar uma **mensagem de boas-vindas automática** que a Sophia enviará na primeira vez que uma mãe do Beta Fechado abrir o chat.

---

## ✅ MENSAGEM DEFINIDA

### **Versão Curta (Recomendada - ~150 caracteres):**

```
Olá, querida! 💕 Eu sou a Sophia, sua amiga digital do puerpério. 

Estou aqui para te escutar, te apoiar e te ajudar com informações sobre cuidados do bebê, amamentação e, claro, te lembrar das vacinas do seu pequeno através da nossa Agenda de Vacinação! 💉

Lembre-se: eu não substituo profissionais de saúde, mas estou sempre aqui quando você precisar de uma palavra amiga ou uma orientação rápida. 

Como você está se sentindo hoje? 💛
```

**Tamanho:** ~400 caracteres (ideal para mobile, não muito longo)

---

## 📋 VERSÃO ALTERNATIVA (Mais Curta - ~250 caracteres)

Se precisar de uma versão ainda mais curta:

```
Olá! 💕 Eu sou a Sophia, sua amiga digital do puerpério. 

Estou aqui para te apoiar e te ajudar com cuidados do bebê, amamentação e vacinas através da nossa Agenda de Vacinação! 💉

Lembre-se: não substituo profissionais de saúde, mas estou sempre aqui para uma palavra amiga. 

Como você está hoje? 💛
```

**Tamanho:** ~280 caracteres

---

## ✅ ELEMENTOS OBRIGATÓRIOS

### **1. Apresentação:**
- ✅ Nome: "Sophia"
- ✅ Função: "sua amiga digital do puerpério"
- ✅ Emoji acolhedor: 💕

### **2. Explicação do Papel:**
- ✅ O que a Sophia faz: "te escutar, te apoiar, te ajudar"
- ✅ Áreas de suporte: cuidados do bebê, amamentação, vacinas
- ✅ **Menciona Agenda de Vacinação** (encorajamento de uso)

### **3. Limitação Clara:**
- ✅ "Não substituo profissionais de saúde"
- ✅ Tom claro mas acolhedor (não soa como disclaimer legal)

### **4. Abertura para Conversa:**
- ✅ Pergunta aberta: "Como você está se sentindo hoje?"
- ✅ Emoji empático: 💛

---

## 🎯 TOM DE VOZ

- ✅ **Acolhedor e empático** (como uma amiga)
- ✅ **Claro sobre limitações** (sem soar como disclaimer)
- ✅ **Encorajador** (menciona Agenda de Vacinação como recurso)
- ✅ **Curto e direto** (ideal para mobile)

---

## 📱 CONSIDERAÇÕES PARA MOBILE

- ✅ **Tamanho adequado:** ~400 caracteres (não muito longo para ler no celular)
- ✅ **Quebras de linha:** Usa parágrafos curtos para facilitar leitura
- ✅ **Emojis estratégicos:** Ajudam na comunicação visual e emocional
- ✅ **Call-to-action claro:** Pergunta final encoraja interação

---

## 🔧 IMPLEMENTAÇÃO

### **Onde Implementar:**
- Primeira mensagem ao abrir o chat pela primeira vez
- Verificar se usuária já teve conversa anterior (não repetir)
- Exibir apenas para novas usuárias do Beta Fechado

### **Quando Mostrar:**
- Quando `historico_usuario` está vazio (primeira vez)
- Quando usuária é nova (criada após lançamento do Beta)

### **Variável:**
```javascript
const WELCOME_MESSAGE = `Olá, querida! 💕 Eu sou a Sophia, sua amiga digital do puerpério. 

Estou aqui para te escutar, te apoiar e te ajudar com informações sobre cuidados do bebê, amamentação e, claro, te lembrar das vacinas do seu pequeno através da nossa Agenda de Vacinação! 💉

Lembre-se: eu não substituo profissionais de saúde, mas estou sempre aqui quando você precisar de uma palavra amiga ou uma orientação rápida. 

Como você está se sentindo hoje? 💛`;
```

---

**Versão:** 1.0  
**Status:** ✅ Pronto para Implementação  
**Próxima Revisão:** Após feedback das primeiras usuárias do Beta
