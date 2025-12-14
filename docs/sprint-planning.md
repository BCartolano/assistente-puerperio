# Planejamento de Sprints - Chatbot Médico

**Scrum Master:** SM Agent  
**Data:** 2025-01-12  
**Duração do Sprint:** 2 semanas

## 📋 RESUMO EXECUTIVO

**Total de Sprints Planejadas:** 5  
**Duração Total Estimada:** 10 semanas  
**Equipe:** Dev, QA, Architect (consultoria)

---

## 🎯 BACKLOG PRIORITIZADO

### Épico 1: Fundação e Infraestrutura

**Stories:**
1. ✅ Criar estrutura de pastas e modelos base
2. ✅ Implementar migração de banco de dados
3. ✅ Implementar BusinessHoursService
4. ⏳ Configurar ambiente de desenvolvimento
5. ⏳ Setup de testes básicos

**Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 1 sprint

---

### Épico 2: Integração WhatsApp

**Stories:**
1. ⏳ Implementar WhatsAppIntegrationService
2. ⏳ Criar handlers de webhook
3. ⏳ Implementar envio de mensagens
4. ⏳ Validação de assinatura de webhook
5. ⏳ Testes de integração WhatsApp

**Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 1-2 sprints

---

### Épico 3: Identificação de Especialidade

**Stories:**
1. ⏳ Implementar SpecialtyIdentificationService
2. ⏳ Integrar com OpenAI para classificação
3. ⏳ Criar SpecialtyMapping model
4. ⏳ Implementar fallback quando confiança baixa
5. ⏳ Testes de classificação

**Prioridade:** 🟠 ALTA  
**Estimativa:** 1 sprint

---

### Épico 4: Sistema de Agendamento

**Stories:**
1. ⏳ Implementar AppointmentService
2. ⏳ Validação de disponibilidade
3. ⏳ Confirmação de agendamento
4. ⏳ Cancelamento e reagendamento
5. ⏳ Notificações de confirmação
6. ⏳ Testes E2E de agendamento

**Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 2 sprints

---

### Épico 5: Integração com Sistemas Externos

**Stories:**
1. ⏳ Implementar ExternalSystemAdapter (base)
2. ⏳ Criar adapter mock para desenvolvimento
3. ⏳ Implementar sincronização
4. ⏳ Tratamento de erros e retry
5. ⏳ Dashboard de sincronização
6. ⏳ Testes de integração externa

**Prioridade:** 🟠 ALTA  
**Estimativa:** 1-2 sprints

---

## 📅 PLANO DE SPRINTS

### Sprint 1: Fundação (Semanas 1-2)

**Objetivo:** Estabelecer base técnica sólida

**Stories:**
- Criar estrutura de pastas
- Implementar migração de banco
- Implementar BusinessHoursService
- Setup de testes
- Configurar ambiente

**Entregáveis:**
- ✅ Estrutura de código criada
- ✅ Banco de dados migrado
- ✅ BusinessHoursService funcionando
- ✅ Testes básicos passando

**Cerimônias:**
- Planning: Dia 1
- Daily: Diário
- Review: Dia 10
- Retrospectiva: Dia 10

---

### Sprint 2: Integração WhatsApp Básica (Semanas 3-4)

**Objetivo:** Receber e enviar mensagens via WhatsApp

**Stories:**
- WhatsAppIntegrationService básico
- Handlers de webhook
- Envio de mensagens
- Validação de webhook
- Testes de integração

**Entregáveis:**
- ✅ Sistema recebe mensagens do WhatsApp
- ✅ Sistema envia respostas
- ✅ Webhook validado
- ✅ Testes passando

---

### Sprint 3: Identificação de Especialidade (Semanas 5-6)

**Objetivo:** Identificar especialidade médica automaticamente

**Stories:**
- SpecialtyIdentificationService
- Integração OpenAI
- SpecialtyMapping model
- Fallback de baixa confiança
- Testes de classificação

**Entregáveis:**
- ✅ Sistema identifica especialidades
- ✅ Integração com OpenAI funcionando
- ✅ Fallback implementado
- ✅ Testes passando

---

### Sprint 4: Sistema de Agendamento (Semanas 7-8)

**Objetivo:** Agendar consultas via chatbot

**Stories:**
- AppointmentService completo
- Validação de disponibilidade
- Confirmação de agendamento
- Cancelamento/reagendamento
- Notificações
- Testes E2E

**Entregáveis:**
- ✅ Agendamento funcionando end-to-end
- ✅ Validações implementadas
- ✅ Notificações enviadas
- ✅ Testes E2E passando

---

### Sprint 5: Integração Externa (Semanas 9-10)

**Objetivo:** Sincronizar com sistemas de gestão

**Stories:**
- ExternalSystemAdapter
- Adapter mock
- Sincronização
- Tratamento de erros
- Dashboard
- Testes de integração

**Entregáveis:**
- ✅ Sincronização funcionando
- ✅ Adapter mock para desenvolvimento
- ✅ Dashboard de monitoramento
- ✅ Testes passando

---

## 📊 MÉTRICAS DE SPRINT

### Velocity
- Sprint 1: Estabelecer baseline
- Sprints seguintes: Ajustar baseado em histórico

### Definição de Pronto (DoD)
- [ ] Código revisado
- [ ] Testes passando (unit + integration)
- [ ] Documentação atualizada
- [ ] Deploy em staging
- [ ] Aprovado por QA

### Definição de Pronto para Produção
- [ ] Todos os testes passando
- [ ] Cobertura mínima atingida
- [ ] Testes de segurança passando
- [ ] Performance validada
- [ ] Documentação completa
- [ ] Aprovado por PM

---

## 🎯 RISCO E DEPENDÊNCIAS

### Dependências Entre Sprints

```
Sprint 1 (Fundação)
    ↓
Sprint 2 (WhatsApp) ──┐
    ↓                 │
Sprint 3 (Especialidade) ──┐
    ↓                      │
Sprint 4 (Agendamento) ←───┘
    ↓
Sprint 5 (Integração Externa)
```

### Riscos Identificados

1. **WhatsApp API pode ter atrasos**
   - Mitigação: Começar cedo, ter fallback

2. **Integração externa complexa**
   - Mitigação: Adapter mock primeiro, depois real

3. **Performance pode ser problema**
   - Mitigação: Testes de carga desde cedo

---

## ✅ CONCLUSÃO

O planejamento de sprints está **bem estruturado** e **realista**. A sequência permite desenvolvimento incremental e testável.

**Principais Destaques:**
- Sprints focadas e entregáveis
- Dependências claras
- Riscos identificados
- Métricas definidas

**Próximos Passos:**
1. Aprovar planejamento com equipe
2. Iniciar Sprint 1
3. Ajustar baseado em aprendizado

---

**Documento criado por:** SM Agent  
**Versão:** 1.0

