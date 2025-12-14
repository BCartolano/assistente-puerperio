# 🎭 Trabalhando com Todos os Agentes BMAD

## 🚀 Método 1: Team All Bundle (Recomendado para Plataformas Web)

O **Team All** é um bundle que contém TODOS os 10 agentes em um único arquivo, permitindo que você trabalhe com toda a equipe de uma vez.

### Como Usar:

1. **Abra o arquivo:**
   ```
   web-bundles/teams/team-all.txt
   ```

2. **Copie TODO o conteúdo** (é um arquivo grande)

3. **Cole no ChatGPT, Claude ou Gemini**

4. **Adicione o contexto do projeto:**
   ```
   [Cole o conteúdo do team-all.txt aqui]
   
   CONTEXTO DO PROJETO:
   [Copie o conteúdo de .bmad-core/project-context.md]
   
   PRD:
   [Copie o conteúdo de docs/prd.md]
   
   ARQUITETURA:
   [Copie o conteúdo de docs/architecture.md]
   ```

5. **Agora você pode usar todos os agentes:**
   ```
   Ative o PM e revise o PRD.
   Depois, ative o Architect e valide a arquitetura.
   Em seguida, ative o Dev e comece a implementação.
   ```

## 🔄 Método 2: Alternar Agentes no Cursor IDE

No Cursor, você pode alternar entre agentes na mesma conversa:

### Sequência Recomendada:

```
1. @pm
   "Revise o PRD do chatbot médico e valide os requisitos"

2. @architect  
   "Valide a arquitetura de integração criada"

3. @analyst
   "Analise os requisitos e identifique riscos"

4. @ux-expert
   "Analise a experiência do usuário no fluxo de agendamento"

5. @dev
   "Comece a implementar o WhatsAppIntegrationService"

6. @qa
   "Crie testes para o sistema de agendamento"

7. @sm
   "Organize as tarefas em sprints"
```

### Exemplo Prático:

```
Você: @pm
PM: "Olá! Sou John, Product Manager..."

Você: "Revise o PRD e identifique gaps"

[PM trabalha...]

Você: @architect
Architect: "Olá! Sou Winston, Architect..."

Você: "Valide a arquitetura baseada no PRD revisado"

[Architect trabalha...]

Você: @dev
Dev: "Olá! Sou Alex, Developer..."

Você: "Implemente a primeira funcionalidade conforme a arquitetura"
```

## 🎯 Método 3: Workflow Completo com Todos os Agentes

### Fase 1: Planejamento (PM + Analyst + PO)

```
@pm
"Crie o PRD completo do chatbot médico"

@analyst
"Analise os requisitos do PRD e identifique riscos e dependências"

@po
"Priorize as funcionalidades do PRD e crie o backlog"
```

### Fase 2: Design (Architect + UX Expert)

```
@architect
"Crie a arquitetura de integração baseada no PRD"

@ux-expert
"Desenhe a experiência do usuário para o fluxo de agendamento via WhatsApp"
```

### Fase 3: Desenvolvimento (Dev)

```
@dev
"Implemente o sistema seguindo a arquitetura e o design UX"
```

### Fase 4: Qualidade (QA)

```
@qa
"Crie testes completos para todas as funcionalidades implementadas"
```

### Fase 5: Gestão (SM)

```
@sm
"Organize o trabalho em sprints e gerencie o progresso"
```

## 🧙 Método 4: Usando BMad Master e Orchestrator

Para coordenação avançada:

```
@bmad-orchestrator
"Orquestre o trabalho de todos os agentes para completar o projeto do chatbot médico"

@bmad-master
"Execute a tarefa de criar o sistema completo de agendamento usando todos os agentes necessários"
```

## 📋 Checklist: Trabalhando com Todos os Agentes

### ✅ Preparação

- [ ] PRD criado e revisado (PM)
- [ ] Arquitetura definida (Architect)
- [ ] Requisitos analisados (Analyst)
- [ ] UX definido (UX Expert)
- [ ] Backlog priorizado (PO)

### ✅ Desenvolvimento

- [ ] Código implementado (Dev)
- [ ] Testes criados (QA)
- [ ] Documentação atualizada (Dev/Architect)

### ✅ Gestão

- [ ] Sprints organizados (SM)
- [ ] Progresso acompanhado (SM)
- [ ] Retrospectiva realizada (SM)

## 🎨 Exemplo de Sessão Completa

```
=== INÍCIO DA SESSÃO ===

@pm
"Vamos revisar o PRD do chatbot médico e garantir que está completo"

[PM revisa e sugere melhorias]

@architect
"Baseado no PRD revisado, valide a arquitetura de integração"

[Architect valida e sugere ajustes]

@analyst
"Analise os riscos técnicos e de negócio do projeto"

[Analyst identifica riscos e sugere mitigação]

@ux-expert
"Desenhe a jornada do usuário para agendar uma consulta via WhatsApp"

[UX Expert cria fluxo de usuário]

@dev
"Implemente o WhatsAppIntegrationService conforme a arquitetura e UX"

[Dev implementa código]

@qa
"Crie testes para o WhatsAppIntegrationService implementado"

[QA cria testes]

@sm
"Organize essas tarefas em um sprint de 2 semanas"

[SM cria sprint e organiza trabalho]

=== FIM DA SESSÃO ===
```

## 💡 Dicas Importantes

### 1. Contexto Compartilhado

Quando alternar entre agentes, sempre mencione o contexto:
```
@dev
"Baseado na arquitetura que o Architect criou, implemente..."
```

### 2. Referências Cruzadas

Agentes podem referenciar trabalho de outros:
```
@qa
"Teste a funcionalidade que o Dev implementou baseada no PRD do PM"
```

### 3. Validação Contínua

Use múltiplos agentes para validar:
```
@architect
"O Dev implementou X. Valide se está conforme a arquitetura."

@qa
"O Dev implementou X. Crie testes para validar."
```

### 4. Orquestração Inteligente

Use BMad Orchestrator para coordenar:
```
@bmad-orchestrator
"Coordene o PM, Architect e Dev para completar a feature de agendamento"
```

## 🚨 Limitações

- No Cursor IDE, você não pode ativar múltiplos agentes simultaneamente em uma única mensagem
- Você precisa alternar entre agentes na mesma conversa
- Cada agente mantém contexto da conversa, mas não vê trabalho de outros agentes automaticamente (você precisa mencionar)

## ✅ Solução: Team All Bundle

Para trabalhar com TODOS os agentes simultaneamente, use o **team-all.txt** em plataformas web (ChatGPT/Claude/Gemini), onde você pode ativar múltiplos agentes na mesma conversa.

---

**🎉 Agora você está pronto para trabalhar com toda sua equipe de agentes AI!**

Experimente começar com o workflow completo acima!

