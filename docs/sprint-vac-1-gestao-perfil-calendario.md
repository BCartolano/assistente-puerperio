# Sprint VAC-1: Gestão de Perfil e Calendário

**Product Owner:** Sarah (PO)  
**Data de Criação:** 2025-01-08  
**Sprint:** VAC-1  
**Duração Estimada:** 2 semanas  
**Prioridade:** 🔴 CRÍTICA

---

## 🎯 OBJETIVO DA SPRINT

Implementar funcionalidade completa de gestão de perfil do bebê e visualização do calendário de vacinação, permitindo às mães acompanhar a jornada de vacinação de seus filhos de forma acolhedora e visualmente rica.

---

## 📋 USER STORIES

### Story 1: Cadastro de Perfil do Bebê
**Como** mãe do puerpério,  
**Eu quero** cadastrar o perfil do meu bebê (nome, data de nascimento)  
**Para que** o sistema calcule automaticamente o calendário de vacinação personalizado.

**Critérios de Aceite:**
- ✅ Formulário de cadastro com campos: Nome (obrigatório), Data de Nascimento (obrigatório), Gênero (opcional)
- ✅ Validação: Data de nascimento não pode ser futura
- ✅ Após cadastro, sistema calcula automaticamente todas as vacinas do PNI
- ✅ Calendário é criado automaticamente baseado na data de nascimento
- ✅ Mensagem de sucesso após cadastro
- ✅ Redirecionamento para visualização do calendário

**Estimativa:** 3 pontos  
**Dependências:** Backend já implementado (VaccinationService)

---

### Story 2: Visualização do Calendário (Timeline)
**Como** mãe do puerpério,  
**Eu quero** visualizar o calendário de vacinação do meu bebê em formato de timeline  
**Para que** eu entenda claramente quais vacinas já foram aplicadas e quais estão por vir.

**Critérios de Aceite:**
- ✅ Timeline visual organizada por idade (ao nascer, 2 meses, 3 meses, etc.)
- ✅ Vacinas concluídas exibidas com check (✓) e data de aplicação
- ✅ Vacinas pendentes exibidas com ícone de relógio (⏳)
- ✅ Próxima vacina destacada visualmente (cor quente, borda destacada)
- ✅ Indicador de progresso geral (barra de progresso ou percentual)
- ✅ Design acolhedor usando paleta quente (#ff8fa3, #ffb3c6, #ffe8f0)
- ✅ Responsivo para desktop, tablet e mobile

**Estimativa:** 5 pontos  
**Dependências:** Story 1, Especificação UX (Sally)

---

### Story 3: Marcar Vacina como Aplicada
**Como** mãe do puerpério,  
**Eu quero** marcar uma vacina como aplicada após levá-la ao posto de saúde  
**Para que** o calendário seja atualizado e eu tenha registro do progresso.

**Critérios de Aceite:**
- ✅ Botão "Marcar como Aplicada" em cada vacina pendente
- ✅ Modal/Formulário opcional para adicionar detalhes (local, profissional, lote)
- ✅ Validação: Data de aplicação não pode ser anterior à data de nascimento
- ✅ Feedback visual imediato (card muda de pendente para concluída)
- ✅ Modal de comemoração aparece após marcar (🎉)
- ✅ Progresso geral atualiza automaticamente
- ✅ Chamada para API `/api/vaccination/mark-done`

**Estimativa:** 5 pontos  
**Dependências:** Story 2, Backend já implementado

---

### Story 4: Sistema de Lembretes por E-mail
**Como** mãe do puerpério,  
**Eu quero** receber lembretes por e-mail 2 dias antes de cada vacina  
**Para que** eu não esqueça de levar meu bebê ao posto de saúde.

**Critérios de Aceite:**
- ✅ E-mail enviado automaticamente 2 dias antes da data recomendada
- ✅ E-mail contém:
  - Nome da vacina
  - Data recomendada
  - Dias até a vacina
  - Idade do bebê
  - Número da dose
  - O que a vacina protege
  - **Sugestão de posto de saúde mais próximo** (UBS/posto de saúde)
  - Link para ver calendário completo
- ✅ E-mail usa template HTML responsivo com paleta quente
- ✅ Apenas usuários com e-mail verificado recebem lembretes
- ✅ Lembrete não é reenviado (flag `reminder_sent` controla)
- ✅ Tarefa agendada executa diariamente (configurar cron/APScheduler)

**Estimativa:** 3 pontos  
**Dependências:** Backend já implementado (VaccinationReminderService)

**Nota Técnica:** Backend já implementado. Necessário apenas configurar tarefa agendada.

---

## 🔍 CRITÉRIOS DE ACEITE ESPECÍFICOS - LEMBRETES

### E-mail de Lembrete DEVE conter:

1. **Cabeçalho Visual**
   - ✅ Título: "💉 Lembrete de Vacinação"
   - ✅ Saudação personalizada: "Olá [Nome da Mãe]!"
   - ✅ Paleta quente (#ff8fa3)

2. **Informações da Vacina**
   - ✅ Nome completo da vacina
   - ✅ Data recomendada (formato DD/MM/YYYY)
   - ✅ Dias até a vacina ("Faltam X dias")
   - ✅ Idade do bebê ("X meses")
   - ✅ Número da dose ("Xª dose")

3. **Informações Educativas**
   - ✅ "O que esta vacina protege:" + descrição clara

4. **Sugestão de Local**
   - ✅ Seção: "📍 Onde aplicar:"
   - ✅ Texto: "Procure uma unidade básica de saúde (UBS) próxima ou posto de saúde mais próximo da sua residência. As vacinas do calendário PNI são oferecidas gratuitamente pelo SUS."
   - ⚠️ **Nota:** Integração com geolocalização/API de UBS pode ser adicionada futuramente

5. **Call-to-Action**
   - ✅ Botão: "📋 Ver Calendário Completo"
   - ✅ Link funcional para `/vaccination`

6. **Rodapé**
   - ✅ Mensagem: "Este lembrete foi enviado automaticamente 2 dias antes da data recomendada."
   - ✅ Assinatura: "Sophia - Sua Amiga do Puerpério"

---

## 📊 DEFINITION OF DONE

### Para cada Story:
- ✅ Código implementado e revisado
- ✅ Testes funcionais realizados
- ✅ Design implementado conforme especificação UX
- ✅ Responsividade validada (desktop, tablet, mobile)
- ✅ Integração com backend funcionando
- ✅ Documentação atualizada (se necessário)

### Para a Sprint:
- ✅ Todas as stories concluídas
- ✅ Testes end-to-end passando
- ✅ Validação com usuário final (ou PO)
- ✅ Deploy em ambiente de staging
- ✅ Documentação de uso atualizada

---

## ⚠️ CONSIDERAÇÕES IMPORTANTES

### Peso e Medidas
**Decisão da PO:** Por enquanto, **NÃO** adicionar campo de "Peso e Medidas" ao perfil do bebê.

**Justificativa:**
1. **Foco no MVP:** Agenda de vacinação é funcionalidade core. Peso/medidas é complementar.
2. **Complexidade adicional:** Peso/medidas requerem:
   - Formulário de cadastro/edição
   - Gráficos de crescimento
   - Validações (curvas de crescimento da OMS)
   - Integração com percentis
3. **Priorização:** Melhor adicionar depois de validar a agenda de vacinação com usuárias.

**Recomendação:** Criar Story futura "VAC-2: Acompanhamento de Crescimento" após validação da VAC-1.

---

## 📅 CRONOGRAMA SUGERIDO

### Semana 1
- **Dia 1-2:** Story 1 (Cadastro de Perfil)
- **Dia 3-5:** Story 2 (Visualização Timeline)

### Semana 2
- **Dia 1-3:** Story 3 (Marcar como Aplicada)
- **Dia 4:** Story 4 (Configurar Lembretes - backend já pronto)
- **Dia 5:** Testes, refinamentos, validação

---

## 🔗 DEPENDÊNCIAS EXTERNAS

- ✅ Backend já implementado (VaccinationService, VaccinationReminderService)
- ✅ API endpoints já criados (`/api/vaccination/status`, `/api/vaccination/mark-done`)
- ✅ Especificação UX disponível (Sally)
- ⏳ Frontend Timeline ainda não implementado

---

## 📝 NOTAS ADICIONAIS

### Integração com Geolocalização (Futuro)
- Para sugestão de posto de saúde mais próximo, considerar:
  - API do Google Maps (Geocoding + Places)
  - API do OpenStreetMap
  - Banco de dados de UBS do Ministério da Saúde

### Melhorias Futuras
- Notificações push (além de e-mail)
- Compartilhamento do calendário (PDF)
- Histórico completo de vacinas aplicadas
- Lembretes personalizáveis (1 dia, 3 dias, etc.)

---

**Sprint criada por:** Sarah (Product Owner)  
**Data:** 2025-01-08  
**Versão:** 1.0  
**Status:** Pronta para Planning
