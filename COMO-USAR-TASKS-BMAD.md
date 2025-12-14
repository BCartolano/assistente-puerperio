# 🎭 Como Usar o Sistema de Tasks BMAD - Método Profissional

## ✅ O QUE FOI CRIADO

1. **`tasks.md`** - Arquivo central com tarefas para TODOS os agentes
2. **`flattened-codebase.xml`** - Super prompt unificado com todos os agentes e tarefas

---

## 🚀 COMO USAR NO CHATGPT / CLAUDE / GEMINI

### Passo 1: Abrir o arquivo flattened-codebase.xml

O arquivo está na raiz do projeto:
```
chatbot-puerperio/flattened-codebase.xml
```

### Passo 2: Copiar TODO o conteúdo

- O arquivo tem ~1.9 MB
- Copie TUDO de uma vez
- Não precisa editar nada

### Passo 3: Colar no ChatGPT/Claude/Gemini

1. Abra ChatGPT, Claude ou Gemini
2. Cole TODO o conteúdo do `flattened-codebase.xml`
3. Aguarde a IA processar (pode levar alguns segundos)

### Passo 4: Trabalhar com a equipe completa

Agora você pode pedir para qualquer agente:

```
Ative o PM e crie o PRD completo do chatbot médico.

Depois, ative o Architect e valide a arquitetura.

Em seguida, ative o Dev e comece a implementação.
```

Ou simplesmente:

```
Execute todas as tarefas definidas no tasks.md
```

---

## 📝 COMO ADICIONAR NOVAS TAREFAS

### Para um agente específico:

1. **Edite o arquivo `tasks.md`**

2. **Adicione uma nova seção ou modifique existente:**

```markdown
## [DEV]

Agora gere o backend completo em Python/Flask para esse projeto.
Implemente todos os endpoints da API.
```

3. **Execute o flatten novamente:**

```bash
cd BMAD-METHOD-v5
node tools/flattener/main.js -i . -o ../flattened-codebase.xml
```

4. **Copie o novo arquivo e cole na IA**

---

## 🎯 EXEMPLOS DE USO

### Exemplo 1: Trabalhar com um agente específico

No ChatGPT/Claude, após colar o flattened-codebase.xml:

```
Ative o agente PM e revise o PRD do chatbot médico.
Identifique gaps e sugira melhorias.
```

### Exemplo 2: Trabalhar com múltiplos agentes

```
1. Ative o PM e crie o PRD completo
2. Depois, ative o Architect e valide a arquitetura baseada no PRD
3. Em seguida, ative o Dev e comece a implementação
4. Por fim, ative o QA e crie os testes
```

### Exemplo 3: Executar todas as tarefas

```
Execute todas as tarefas definidas no tasks.md na ordem correta:
1. PM primeiro
2. Architect segundo
3. Dev terceiro
4. E assim por diante
```

---

## 📋 ESTRUTURA DO TASKS.MD

O arquivo `tasks.md` segue este padrão:

```markdown
# TASKS - PROJETO [NOME]

## [PM]
[Tarefa para Product Manager]

## [PO]
[Tarefa para Product Owner]

## [ANALYST]
[Tarefa para Analyst]

## [ARCHITECT]
[Tarefa para Architect]

## [UX-EXPERT]
[Tarefa para UX Expert]

## [DEV]
[Tarefa para Developer]

## [QA]
[Tarefa para QA]

## [SM]
[Tarefa para Scrum Master]

## [BMAD-MASTER]
[Tarefa para BMad Master]

## [BMAD-ORCHESTRATOR]
[Tarefa para BMad Orchestrator]
```

---

## 🔄 WORKFLOW COMPLETO

### 1. Editar Tasks
```bash
# Edite tasks.md com suas tarefas
```

### 2. Gerar Super Prompt
```bash
cd BMAD-METHOD-v5
node tools/flattener/main.js -i . -o ../flattened-codebase.xml
```

### 3. Usar na IA
- Copie `flattened-codebase.xml`
- Cole no ChatGPT/Claude/Gemini
- Trabalhe com todos os agentes!

---

## 💡 DICAS IMPORTANTES

### ✅ FAÇA:
- Sempre copie TODO o conteúdo do flattened-codebase.xml
- Use o formato `[AGENTE]` no tasks.md
- Execute flatten após modificar tasks.md
- Seja específico nas tarefas

### ❌ NÃO FAÇA:
- Não edite o flattened-codebase.xml manualmente
- Não pule etapas do workflow
- Não use nomes de agentes diferentes do padrão

---

## 🎯 AGENTES DISPONÍVEIS

| Agente | Tag no tasks.md | Função |
|--------|----------------|--------|
| Product Manager | `[PM]` | PRDs, estratégia |
| Product Owner | `[PO]` | Backlog, prioridades |
| Analyst | `[ANALYST]` | Regras de negócio |
| Architect | `[ARCHITECT]` | Arquitetura técnica |
| UX Expert | `[UX-EXPERT]` | Design e experiência |
| Developer | `[DEV]` | Implementação |
| QA | `[QA]` | Testes e qualidade |
| Scrum Master | `[SM]` | Sprints e gestão |
| BMad Master | `[BMAD-MASTER]` | Revisão geral |
| BMad Orchestrator | `[BMAD-ORCHESTRATOR]` | Coordenação |

---

## ✅ STATUS ATUAL

- ✅ `tasks.md` criado com tarefas para todos os agentes
- ✅ `flattened-codebase.xml` gerado (1.9 MB)
- ✅ Pronto para usar no ChatGPT/Claude/Gemini

---

## 🚀 PRÓXIMOS PASSOS

1. **Abrir `flattened-codebase.xml`**
2. **Copiar TODO o conteúdo**
3. **Colar no ChatGPT/Claude/Gemini**
4. **Pedir para executar todas as tarefas do tasks.md**

---

**🎉 Pronto! Agora você tem acesso a TODA a equipe BMAD trabalhando junto!**

