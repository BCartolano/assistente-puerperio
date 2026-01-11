# Canal de Feedback - Soft Launch - Product Owner

**Criado por:** Sarah (Product Owner)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Estratégia Definida

---

## 🎯 ESTRATÉGIA DE FEEDBACK PÓS-SOFT LAUNCH

### **Objetivo:**
Criar canais de feedback acessíveis e não intrusivos para coletar insights das primeiras mães usuárias da Sophia V1.0 PROD.

---

## 📊 CANAIS DE FEEDBACK PROPOSTOS

### **1. Feedback In-App (RECOMENDADO - Primário)**

**Implementação:**
- Botão discreto "Enviar Feedback" na aba de Dicas (mobile) ou Sidebar Direita (desktop)
- Modal simples com:
  - Campo de texto (textarea)
  - Classificação de satisfação (1-5 estrelas ou emoji)
  - Opcional: screenshot automático do problema (se houver)

**Vantagens:**
- ✅ Não intrusivo
- ✅ Contextual (mãe está usando o app)
- ✅ Feedback imediato sobre problema encontrado
- ✅ Não requer sair do app

**Endpoint:**
- `POST /api/feedback` - Salva feedback no banco de dados

**Quando exibir:**
- Sempre disponível (botão fixo)
- OU após 3 usos do app (não intrusivo)

---

### **2. Email Direto**

**Implementação:**
- Email de feedback: `feedback@sophia-puerperio.com` (ou email do projeto)
- Link no footer: "Envie seu feedback"

**Vantagens:**
- ✅ Familiar (mães conhecem email)
- ✅ Permite feedback detalhado
- ✅ Permite anexar screenshots

**Desvantagens:**
- ⚠️ Requer sair do app
- ⚠️ Pode ser esquecido

---

### **3. Formulário Web (Opcional)**

**Implementação:**
- Página `/feedback` com formulário
- Similar ao feedback in-app, mas mais completo
- Possibilidade de feedback anônimo

**Vantagens:**
- ✅ Permite feedback detalhado
- ✅ Pode ser compartilhado via link
- ✅ Não requer app aberto

**Quando usar:**
- Para feedback extenso
- Para sugestões de funcionalidades

---

## 📋 ESTRUTURA DE FEEDBACK

### **Campos Obrigatórios:**
- Tipo de feedback: Bug / Sugestão / Dúvida / Elogio
- Mensagem (textarea, mínimo 10 caracteres)
- Classificação (1-5 estrelas ou emoji)

### **Campos Opcionais:**
- Email (para resposta)
- Screenshot (upload)
- Dispositivo/Navegador (auto-detectado)

---

## 🔄 PROCESSO DE TRIAGEM

### **Fase 1: Coleta (Semana 1-2)**
- Monitorar feedbacks diariamente
- Responder feedbacks dentro de 24-48h
- Agradecer cada feedback

### **Fase 2: Análise (Semana 2-3)**
- Agrupar feedbacks por categoria
- Identificar padrões (bugs recorrentes, solicitações comuns)
- Priorizar ajustes

### **Fase 3: Ação (Semana 3-4)**
- Implementar correções críticas
- Planejar melhorias para V1.1
- Comunicar melhorias implementadas aos usuários que reportaram

---

## 📧 COMUNICAÇÃO COM USUÁRIAS

### **Template de Resposta:**

**Para Bugs:**
```
Olá [Nome]!

Obrigada por reportar esse problema. Ele foi registrado e nossa equipe está trabalhando para corrigi-lo.

Você será notificada quando a correção estiver disponível.

Obrigada por ajudar a melhorar a Sophia! 💕

Equipe Sophia
```

**Para Sugestões:**
```
Olá [Nome]!

Que sugestão incrível! Vamos analisar e considerar para uma futura atualização.

Suas ideias são muito importantes para nós!

Obrigada! 💕

Equipe Sophia
```

---

## 🎯 MÉTRICAS DE SUCESSO

### **KPIs:**
- Taxa de resposta de feedback: ≥ 80% respondidos em 48h
- Taxa de resolução de bugs críticos: ≤ 7 dias
- Taxa de satisfação geral: ≥ 4.0/5.0

### **Coleta de Métricas:**
- Número de feedbacks recebidos por semana
- Distribuição por tipo (bug, sugestão, etc.)
- Tempo médio de resolução
- Taxa de satisfação (estrelas/emoji)

---

## 📱 IMPLEMENTAÇÃO TÉCNICA (V1.1)

### **Tabela no Banco:**
```sql
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT NOT NULL, -- 'bug', 'suggestion', 'question', 'praise'
    message TEXT NOT NULL,
    rating INTEGER, -- 1-5
    email TEXT,
    device_info TEXT,
    screenshot_path TEXT,
    status TEXT DEFAULT 'new', -- 'new', 'acknowledged', 'resolved', 'closed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### **Endpoint:**
- `POST /api/feedback` - Cria novo feedback
- `GET /api/feedback` (admin) - Lista feedbacks

---

## ✅ CONCLUSÃO

**Canal Primário:** Feedback In-App (botão discreto)  
**Canal Secundário:** Email direto (footer)  
**Implementação:** V1.1 (após validação de Soft Launch)

**Por enquanto (Soft Launch):**
- Usar email direto ou feedback via contato do projeto
- Documentar feedbacks manualmente
- Preparar estrutura técnica para V1.1

---

**Versão:** 1.0  
**Status:** ✅ Estratégia Definida  
**Próxima Revisão:** Após Soft Launch (V1.1)
