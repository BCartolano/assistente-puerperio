# Planejamento de Sprints - Chatbot Médico

**Scrum Master:** SM Agent  
**Data:** 2025-01-12  
**Duração do Sprint:** 2 semanas

## 📋 RESUMO EXECUTIVO

**Total de Sprints Planejadas:** 8 (5 backend + 3 UX/Desktop)  
**Duração Total Estimada:** 16 semanas  
**Equipe:** Dev, QA, Architect (consultoria), UX Expert (consultoria)

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

### Épico 6: Melhorias UX/UI Desktop (Sophia) ✅ CONCLUÍDO - V1.0 PROD (DESKTOP)

**Stories:**
1. ✅ Implementar nova paleta de cores quentes e gradiente de fundo (Sprint UX-1 - CONCLUÍDA)
2. ✅ Adicionar ícones decorativos flutuantes nas laterais (Sprint UX-1 - CONCLUÍDA)
3. ✅ Migrar para layout de 3 colunas (painéis laterais) (Sprint UX-2 - CONCLUÍDA)
4. ✅ Implementar painel esquerdo (dicas rápidas e ícones) (Sprint UX-2 - CONCLUÍDA)
5. ✅ Implementar painel direito (vídeos, testemunhos, ações) (Sprint UX-2 - CONCLUÍDA)
6. ✅ Criar seção de vídeos colapsável no conteúdo principal (Sprint UX-3 - CONCLUÍDA)
7. ✅ Implementar Chat Inteligente com contexto personalizado e Quick Replies (Sprint INT-1 - CONCLUÍDA)
8. ✅ Implementar Agenda de Vacinação Interativa com timeline visual (Sprint VAC-1 - CONCLUÍDA)
9. ✅ Testes de responsividade e validação UX (Sprint UX-1, UX-2, UX-3 - CONCLUÍDAS)

**Prioridade:** 🟡 MÉDIA (Alto impacto de experiência)  
**Estimativa:** 3 sprints  
**Status:** ✅ **CONCLUÍDO - V1.0 PROD (DESKTOP)**  
**Data de Conclusão:** 2025-01-27  
**Referência:** `ANALISE_UX_VISUAL_SOPHIA.md`, `REVISAO_UX_DESKTOP_FINAL.md`  
**Fechamento:** Sprint UX-1, UX-2 e UX-3 formalmente fechadas. Épico 6 concluído.

---

### Épico 7: Experiência Mobile First 📱 ✅ 100% ENTREGUE - V1.0 PROD (MOBILE)

**Objetivo:** Adaptar todas as funcionalidades da versão desktop para dispositivos móveis, garantindo experiência fluida e acessível em smartphones e tablets.

**Stories:**
1. ✅ Análise de Adaptação Mobile (UX Expert) - CONCLUÍDA
2. ✅ Transformar layout de 3 colunas em navegação mobile (Bottom Navigation) - CONCLUÍDA
3. ✅ Definir prioridade visual mobile (Chat como inicial) - CONCLUÍDA
4. ✅ Implementar acessibilidade one-handed (botões ≥ 44px) - CONCLUÍDA
5. ✅ Adaptar Quick Replies para mobile (largura total, altura ≥ 44px) - CONCLUÍDA
6. ✅ Adaptar Timeline de Vacinação para telas pequenas - CONCLUÍDA
7. ✅ Otimizar streaming de respostas para mobile (15ms) - CONCLUÍDA
8. ✅ Adaptar header fixo do chat para mobile (sticky typing indicator) - CONCLUÍDA
9. ✅ Testes de usabilidade em dispositivos reais (5/5 tarefas aprovadas) - CONCLUÍDA
10. ✅ Otimização de performance para touch devices (confetes reduzidos, requestAnimationFrame) - CONCLUÍDA
11. ✅ Mensagem de boas-vindas automática - CONCLUÍDA
12. ✅ Sistema de feedback integrado - CONCLUÍDA
13. ✅ Robustez técnica (RotatingFileHandler, timeout OpenAI, toast errors) - CONCLUÍDA

**Prioridade:** 🔴 CRÍTICA (Expansão de alcance)  
**Estimativa:** 2-3 sprints  
**Status:** ✅ **100% ENTREGUE - V1.0 PROD (MOBILE)**  
**Data de Conclusão:** 2025-01-27  
**Data de Entrega Final:** 2025-01-27  
**Referência:** `IMPLEMENTACAO_SPRINT_MOBILE_1.md`, `CONCLUSAO_SPRINT_MOBILE_2_SARAH.md`, `CONFIRMACAO_V1_0_ONLINE_SARAH.md`  
**Criado em:** 2025-01-27

**Critérios de Sucesso:**
- ✅ Interface funcional em telas < 480px (mobile portrait)
- ✅ Todos os botões alcançáveis com uma mão (zona de alcance)
- ✅ Chat e Timeline acessíveis via navegação intuitiva
- ✅ Performance otimizada para touch (scroll suave, sem lag)
- ✅ Quick Replies adaptados para mobile (tamanho e espaçamento)
- ✅ Testes de usabilidade aprovados com mães reais (5/5 tarefas)
- ✅ Sistema de feedback operacional
- ✅ Monitoramento e logs persistentes ativos

---

### Épico 8: Lançamento e Sustentação 🚀 ⏳ NOVO

**Objetivo:** Cuidar das primeiras usuárias reais após o sucesso do mobile, garantindo experiência de qualidade, coleta de feedback estruturada e ajustes rápidos baseados em necessidades reais.

**Stories:**
1. ⏳ Sistema de Monitoramento de Uso
2. ⏳ Processamento de Feedbacks (Automação)
3. ⏳ Ajustes Rápidos Baseados em Feedback
4. ⏳ Suporte às Primeiras Usuárias
5. ⏳ Melhorias Baseadas em Feedback (V1.1)
6. ⏳ Preparação para Lançamento Público

**Prioridade:** 🔴 CRÍTICA (Sustentação e Qualidade)  
**Estimativa:** 3-4 sprints  
**Status:** ⏳ **AUTORIZADO PARA PLANEJAMENTO**  
**Referência:** `EPICO_8_LANCAMENTO_SUSTENTACAO.md`  
**Criado em:** 2025-01-27

**Critérios de Sucesso:**
- ✅ Sistema de monitoramento operacional
- ✅ Processamento de feedbacks automatizado
- ✅ V1.1 lançada com melhorias prioritárias
- ✅ Métricas de sucesso atingidas (NPS ≥ 50, Taxa de retorno ≥ 70%)
- ✅ Preparação para lançamento público concluída

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

### Sprint UX-1: Visual & Calor (Semanas 11-12) 🎨 ✅ CONCLUÍDA

**Objetivo:** Implementar nova paleta de cores quentes e melhorar sensação visual de acolhimento

**Stories:**
- ✅ Implementar nova paleta de cores (FR16)
- ✅ Atualizar gradientes de fundo
- ✅ Adicionar variáveis CSS para cores quentes
- ✅ Implementar ícones decorativos flutuantes
- ✅ Animações suaves de elementos decorativos
- ✅ Validação visual com usuários

**Entregáveis:**
- ✅ Nova paleta de cores implementada
- ✅ Gradientes quentes aplicados
- ✅ Ícones decorativos animados funcionando
- ✅ Visual mais acolhedor e caloroso

**Referência:** `ANALISE_UX_VISUAL_SOPHIA.md` - Fase 1  
**Status:** Concluída em 2025-01-08

---

### Sprint UX-2: Estrutura Desktop (Semanas 13-14) 📐 ✅ CONCLUÍDA

**Objetivo:** Migrar para layout de 3 colunas e preencher laterais no desktop

**Stories:**
- ✅ Implementar layout de 3 colunas para desktop ≥1024px (FR17)
- ✅ Criar estrutura de painéis laterais
- ✅ Implementar painel esquerdo (dicas rápidas, ícones)
- ✅ Implementar painel direito (vídeos mini, testemunhos, ações)
- ✅ Responsividade mobile/tablet (ocultar painéis)
- ✅ Testes de layout em diferentes resoluções

**Entregáveis:**
- ✅ Layout de 3 colunas funcionando
- ✅ Painéis laterais implementados
- ✅ Conteúdo preenchendo laterais efetivamente
- ✅ Layout responsivo mantido

**Referência:** `ANALISE_UX_VISUAL_SOPHIA.md` - Fase 2  
**Status:** Concluída em 2025-01-08

---

### Sprint UX-3: Conteúdo Dinâmico (Semanas 15-16) 📺 ✅ CONCLUÍDA

**Objetivo:** Implementar seção de vídeos colapsável e integração de depoimentos

**Stories:**
- ✅ Criar estrutura de cards para painéis laterais
- ✅ Implementar seção de vídeos colapsável
- ✅ Integrar IDs reais de vídeos do YouTube
- ✅ Modal de vídeo com aspect ratio 16:9
- ✅ Fechamento com ESC limpa src do iframe

**Entregáveis:**
- ✅ Seção de vídeos colapsável funcionando
- ✅ Modal de vídeo respeitando aspect ratio
- ✅ Fechamento limpa áudio imediatamente

**Status:** Concluída em 2025-01-27

---

### Sprint MOBILE-1: Estrutura Base Mobile (Semanas 17-18) 📱 ✅ CONCLUÍDA

**Objetivo:** Criar estrutura de navegação mobile e adaptar layout para telas pequenas

**Stories:**
- ✅ Criar CSS Media Queries para mobile (ocultar 3 colunas)
- ✅ Implementar Bottom Navigation (Chat, Vacinas, Dicas)
- ✅ JavaScript para troca de telas entre abas
- ✅ Ajustar Quick Replies para mobile (largura total, 44px altura)
- ✅ Ocultar header fixo do chat em mobile

**Entregáveis:**
- ✅ Bottom Navigation funcional
- ✅ Navegação entre abas funcionando
- ✅ Quick Replies adaptados para mobile

**Status:** Concluída em 2025-01-27

---

### Sprint MOBILE-2: Chat e Interações (Semanas 19-20) 📱 ⏳ EM PROGRESSO

**Objetivo:** Adaptar chat e interações para mobile, garantindo funcionalidade com teclado virtual

**Stories:**
- ⏳ Implementar aba Dicas com lista vertical de cards
- ⏳ Modal de vídeo fullscreen no mobile
- ⏳ Lazy loading de vídeos YouTube (só carrega quando aba Dicas é ativada)
- ⏳ Input não coberto pelo teclado virtual
- ⏳ Streaming de respostas mais rápido no mobile (15ms vs 25ms)
- ⏳ Indicador de digitação da Sophia no mobile (topo sticky)
- ⏳ Aviso de uso de dados para vídeos YouTube (opcional)
- ✅ Implementar card "Dica do Dia" com rotação diária
- ✅ Implementar widget "Afirmação Positiva" com exibição aleatória
- ✅ Criar lista de miniaturas de vídeos no painel direito
- ✅ Criar modal de player de vídeo (com youtube-nocookie.com para privacidade)
- ⏳ Pesquisar e obter IDs reais do YouTube (4 vídeos)
- ⏳ Verificar permissão de embedding para cada vídeo
- ⏳ Criar descrições curtas (1 frase) para cada vídeo
- ⏳ Atualizar JavaScript com IDs reais dos vídeos
- ⏳ Implementar seção de testemunhos/depoimentos (futuro)
- ⏳ Integrar botões de ação rápida (futuro)
- ⏳ Validação de usabilidade completa

**Entregáveis:**
- ✅ Cards de dicas e afirmações funcionando
- ✅ Modal de vídeo implementado
- ✅ Estrutura de vídeos pronta
- ✅ IDs reais do YouTube integrados
- ✅ Descrições de vídeos adicionadas
- ✅ Testes de embedding validados
- ✅ Sistema de feedback integrado
- ✅ Mensagem de boas-vindas automática
- ✅ Robustez técnica (RotatingFileHandler, timeout OpenAI, toast errors)

**Status:** ✅ Concluída em 2025-01-27
- ⏳ Interface completa sem poluição visual

**Dependências:**
- **Analista:** Pesquisar e fornecer IDs reais do YouTube (ver `docs/pesquisa-videos-youtube.md`)
- **Dev:** Integrar IDs reais no JavaScript após recebimento

**Referência:** 
- `ANALISE_UX_VISUAL_SOPHIA.md` - Fase 3
- `docs/conteudo-paineis-laterais.md` - Conteúdo estruturado
- `docs/pesquisa-videos-youtube.md` - Instruções para pesquisa de vídeos

**Status:** Em progresso - Estrutura implementada, aguardando IDs de vídeos

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
    
    (Paralelo - não bloqueia backend)
    
Sprint UX-1 (Visual & Calor) ←───┐
    ↓                            │
Sprint UX-2 (Estrutura Desktop) ←┼─── Independentes do backend
    ↓                            │
Sprint UX-3 (Conteúdo Dinâmico) ←┘
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
**Atualizado por:** PO (Sarah), UX Expert (Sally)  
**Versão:** 1.2  
**Última Atualização:** 2025-01-08

