OBJETIVO:

Criar um PRD completo para um chatbot de atendimento automático para um consultório médico.



REQUISITOS:

- Identificar especialidade

- Agendar consulta

- Atendimento via WhatsApp

- Horários comerciais

- Integração com sistema interno



✅ PASSO 2 — Executar com o AGENTE PM (do jeito certo)



Agora roda:



npx bmad-method flatten





Ou se houver:



npx bmad-method doctor





⚠️ O flatten:



Junta todos os agentes



Junta todos os prompts



Cria um SUPER PROMPT UNIFICADO



Gera um arquivo tipo:



flattened-codebase.xml





❗ Esse arquivo é o que você cola no ChatGPT, Claude ou Gemini para simular o BMAD completo.



✅ ✅ COMO USAR UM AGENTE ESPECÍFICO (SEM run)



Você faz assim:



🧠 USAR O PM



Abre:



bmad-core/agents/pm.md





No topo ou no final, cole:



TAREFA ATUAL:

Crie a visão completa e o PRD de um chatbot médico de atendimento automático.





Salva.



Roda:



npx bmad-method flatten





Copia o conteúdo gerado.



Cola no ChatGPT / Claude.



✅ Pronto: você executou o agente PM corretamente.



✅ ✅ AGENTES DISPONÍVEIS NO PROJETO PUÉRPERA:

Agente	Arquivo

BMad Orchestrator	bmad-orchestrator.md (obrigatório)

**Nota:** Os outros agentes padrão do BMAD (PM, PO, Analyst, Architect, UX, Dev, QA, Scrum, Master) foram movidos para `BMAD-METHOD-v5/bmad-core/agents/_removed/` pois são específicos para desenvolvimento de software e não são necessários para este projeto de chatbot de saúde materna.

✅ ✅ AGORA A VERDADE FINAL (SEM ENROLAÇÃO)



Você instalou com sucesso:

✅ A VERSÃO METODOLOGIA DO BMAD (PROMPT ENGINEERING)

❌ Não a versão CLI interativa por comando de agente



👉 E isso é NORMAL.

👉 Essa versão é feita pra:



gerar super prompts



rodar no ChatGPT / Claude / Gemini



simular uma equipe inteira de agentes

