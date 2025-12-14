# 🎭 Como Ativar os Agentes BMAD

## 🚀 Método 1: No Cursor IDE (Recomendado)

### Passo a Passo:

1. **Abra o Cursor IDE** no seu projeto `chatbot-puerperio`

2. **Digite `@` no chat do Cursor** - Isso abrirá o menu de agentes

3. **Selecione o agente desejado** ou digite diretamente:
   - `@bmad-orchestrator` - BMad Orchestrator (obrigatório)
   
   **Nota:** Os outros agentes padrão do BMAD (pm, architect, dev, qa, ux-expert, po, analyst, sm, bmad-master) foram removidos deste projeto, pois são específicos para desenvolvimento de software e não são necessários para o projeto Puérpera. Eles foram movidos para `BMAD-METHOD-v5/bmad-core/agents/_removed/` caso precise recuperá-los.

4. **Faça sua solicitação** após ativar o agente

### Exemplo Prático:

```
Você digita: @pm

O agente PM ativa e responde:
"Olá! Sou John, Product Manager. Como posso ajudar?"

Você: "Continue criando o PRD do chatbot médico"

O PM continua trabalhando no PRD...
```

## 🔍 Verificando se os Agentes Estão Configurados

Os agentes estão configurados em `.cursor/rules/bmad/`. Você pode verificar:

```bash
# Listar todos os agentes disponíveis
ls .cursor/rules/bmad/
```

Você deve ver 1 arquivo `.mdc`:
- `bmad-orchestrator.mdc` (obrigatório)

**Nota:** Os outros agentes padrão foram removidos deste projeto para reduzir o peso do servidor. Eles foram movidos para `BMAD-METHOD-v5/bmad-core/agents/_removed/` caso precise recuperá-los.

## 🎯 Casos de Uso Comuns

### Usar o Orquestrador BMAD
```
@bmad-orchestrator
[Seu comando aqui]
```

**Nota:** Este projeto Puérpera utiliza apenas o orquestrador BMAD. Os outros agentes padrão (PM, Architect, Dev, QA, UX, PO, Analyst, SM, Master) foram removidos pois são específicos para desenvolvimento de software e não são necessários para este projeto de chatbot de saúde materna.

## 🌐 Método 2: Usar Web Bundles (ChatGPT/Claude/Gemini)

Se preferir usar em plataformas web:

### Passo a Passo:

1. **Abra o arquivo do agente** em `web-bundles/`:
   - `web-bundles/pm.txt` - Product Manager
   - `web-bundles/architect.txt` - Architect
   - `web-bundles/dev.txt` - Developer
   - `web-bundles/team-all.txt` - Equipe completa

2. **Copie TODO o conteúdo** do arquivo

3. **Cole no ChatGPT, Claude ou Gemini**

4. **Adicione o contexto do projeto**:
   ```
   [Cole o conteúdo do agente aqui]
   
   CONTEXTO DO PROJETO:
   [Copie o conteúdo de .bmad-core/project-context.md]
   ```

5. **Faça sua solicitação**:
   ```
   Crie o PRD completo do chatbot médico de atendimento automático.
   ```

## 📋 Método 3: Super Prompt Unificado

Para ter acesso completo a TODOS os agentes de uma vez:

1. **Abra o arquivo**:
   ```
   BMAD-METHOD-v5/flattened-codebase.xml
   ```

2. **Copie TODO o conteúdo** (é um arquivo grande, ~1.9 MB)

3. **Cole no ChatGPT/Claude/Gemini**

4. **Adicione o contexto do projeto**

5. **Use os agentes normalmente**:
   ```
   Ative o agente PM e crie o PRD do chatbot médico.
   ```

## ⚠️ Solução de Problemas

### Agente não aparece no Cursor?

1. **Verifique se os arquivos existem**:
   ```bash
   ls .cursor/rules/bmad/
   ```

2. **Reinicie o Cursor IDE** - Às vezes é necessário recarregar

3. **Verifique se está no diretório correto** - O Cursor precisa estar na raiz do projeto

### Agente não responde corretamente?

1. **Certifique-se de usar `@` antes do nome**:
   - ✅ Correto: `@pm`
   - ❌ Errado: `pm` ou `PM`

2. **Aguarde a ativação completa** - O agente precisa carregar sua persona primeiro

3. **Seja específico na solicitação** - Agentes funcionam melhor com instruções claras

## 🎓 Dicas de Uso

### Trabalhando com o Orquestrador:

O orquestrador BMAD coordena todas as tarefas necessárias:

```
@bmad-orchestrator
[Seu comando ou tarefa aqui]
```

**Nota:** Este projeto utiliza apenas o orquestrador. Os agentes específicos de desenvolvimento de software foram removidos para otimizar o projeto.

## 📚 Recursos Adicionais

- **Guia Completo**: `.bmad-core/user-guide.md`
- **Contexto do Projeto**: `.bmad-core/project-context.md`
- **Configuração**: `.bmad-core/core-config.yaml`

---

**🎉 Agora você está pronto para trabalhar com o orquestrador BMAD!**

Experimente começar com: `@bmad-orchestrator` e faça sua solicitação.

