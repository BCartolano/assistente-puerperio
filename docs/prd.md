# Chatbot Médico de Atendimento Automático - Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Criar um sistema de chatbot médico completo que identifique automaticamente a especialidade médica necessária baseada nos sintomas e necessidades da paciente
- Implementar sistema de agendamento de consultas integrado com a agenda do consultório médico
- Fornecer atendimento automatizado via WhatsApp durante horários comerciais com suporte de emergência
- Integrar o chatbot com sistemas internos de gestão do consultório para sincronização de dados e agendamentos
- Expandir o chatbot atual (focado em puerpério) para um sistema completo de atendimento médico multiespecialidade
- Garantir que o chatbot forneça informações confiáveis e orientações precisas, mantendo a qualidade do atendimento médico

### Background Context

O **Chatbot Puerpério da Sophia** atualmente é um sistema especializado em fornecer suporte, informações e orientações para mulheres no período puerperal (pós-parto). O sistema já possui uma base sólida de conhecimento, sistema RAG (Retrieval Augmented Generation) implementado, interface web funcional e integração parcial com WhatsApp.

O projeto atual precisa evoluir de um chatbot especializado em puerpério para um **sistema completo de atendimento médico automático** que possa:
- Identificar qual especialidade médica é necessária baseada nos sintomas relatados
- Agendar consultas automaticamente integrando com sistemas de gestão do consultório
- Funcionar como interface principal de comunicação via WhatsApp
- Operar dentro de horários comerciais com capacidade de escalar para emergências
- Integrar-se com sistemas internos existentes do consultório

Esta expansão é crítica para transformar o chatbot de uma ferramenta de informação em uma solução completa de triagem e agendamento médico, reduzindo a carga administrativa do consultório e melhorando o acesso das pacientes aos cuidados de saúde.

### Change Log

| Date | Version | Description | Author |
|------|---------|------------|--------|
| 2025-01-12 | 1.0 | Criação inicial do PRD | PM Agent |
| 2025-01-08 | 1.1 | Adicionados requisitos de UX/Desktop (FR16-FR18, NFR8.1-8.2) baseado em análise de UX Expert | PO (Sarah) |
| 2025-01-08 | 1.2 | FR16, FR17, NFR8.1, NFR8.2 marcados como concluídos (Sprint UX-1). Adicionado NFR8.3 (Privacidade conteúdo externo) | UX Expert (Sally) |
| 2025-01-08 | 1.3 | Fechamento formal Sprint UX-1 e UX-2. Análise de prioridades para próximas fases (Agenda Vacinação vs Personalização Chat) | PO (Sarah) |
| 2025-01-27 | 1.4 | Épico 6 concluído - V1.0 PROD (DESKTOP). Funcionalidades de Chat Inteligente e Agenda de Vacinação marcadas como V1.0 PROD. Criado Épico 7: Experiência Mobile First. | PO (Sarah) |

## Requirements

### Functional

1. **FR1**: O sistema deve identificar automaticamente a especialidade médica necessária baseada nos sintomas, histórico e necessidades relatadas pela paciente através de análise de linguagem natural e classificação de intenção.

2. **FR2**: O sistema deve permitir agendamento de consultas médicas através do chatbot, verificando disponibilidade na agenda do consultório em tempo real.

3. **FR3**: O sistema deve integrar-se com a API do WhatsApp para receber e enviar mensagens, permitindo atendimento completo via esta plataforma.

4. **FR4**: O sistema deve operar durante horários comerciais configuráveis (ex: segunda a sexta, 8h às 18h) e detectar mensagens fora do horário, oferecendo opções de agendamento ou encaminhamento para emergência.

5. **FR5**: O sistema deve integrar-se com sistemas internos de gestão do consultório (ex: sistemas de prontuário eletrônico, agenda médica) através de APIs ou integrações configuráveis.

6. **FR6**: O sistema deve manter histórico completo de conversas e interações com cada paciente, incluindo sintomas relatados, especialidades identificadas e consultas agendadas.

7. **FR7**: O sistema deve validar e confirmar informações de agendamento (data, horário, especialidade, paciente) antes de finalizar o agendamento.

8. **FR8**: O sistema deve enviar confirmações de agendamento via WhatsApp com detalhes da consulta (data, horário, especialista, localização).

9. **FR9**: O sistema deve permitir cancelamento e reagendamento de consultas através do chatbot, com validação de prazos mínimos.

10. **FR10**: O sistema deve fornecer informações sobre especialidades médicas disponíveis, incluindo descrição de cada especialidade e quando procurar cada uma.

11. **FR11**: O sistema deve detectar casos de emergência através de palavras-chave e sintomas críticos, oferecendo orientação imediata e números de emergência.

12. **FR12**: O sistema deve manter a base de conhecimento existente sobre puerpério e expandir para outras especialidades médicas.

13. **FR13**: O sistema deve permitir que administradores configurem horários comerciais, especialidades disponíveis e regras de agendamento.

14. **FR14**: O sistema deve sincronizar agendamentos em tempo real entre o chatbot e o sistema de gestão do consultório, evitando conflitos de horário.

15. **FR15**: O sistema deve fornecer interface web alternativa para pacientes que preferem não usar WhatsApp, mantendo funcionalidades equivalentes.

16. ✅ **FR16**: O sistema deve apresentar paleta de cores quentes e acolhedoras na interface desktop, utilizando tons vibrantes de rosa coral, pêssego e creme rosado para criar sensação de calor visual e acolhimento. **[V1.0 PROD (DESKTOP) - Sprint UX-1]**

17. ✅ **FR17**: O sistema deve implementar layout de 3 colunas em telas desktop (≥1200px), com painel esquerdo para dicas rápidas e ícones decorativos, conteúdo principal centralizado, e painel direito para vídeos recomendados, testemunhos e ações rápidas. **[V1.0 PROD (DESKTOP) - Sprint UX-2]**

18. ✅ **FR18**: O sistema deve incluir seção de vídeos do YouTube colapsável no conteúdo principal, além de miniaturas de vídeos no painel direito, permitindo acesso ao conteúdo educativo sem poluir a interface principal. **[V1.0 PROD (DESKTOP) - Sprint UX-3]**

19. ✅ **FR19**: O sistema deve implementar Chat Inteligente com contexto personalizado (nome do bebê, idade, próxima vacina), streaming de respostas (typewriter effect), Quick Replies contextuais, e detecção de tags de contexto emocional. **[V1.0 PROD (DESKTOP)]**

20. ✅ **FR20**: O sistema deve implementar Agenda de Vacinação Interativa com timeline visual, cálculo automático de datas baseado no calendário PNI 2026, lembretes por email 2 dias antes, e modal de celebração ao marcar vacina aplicada. **[V1.0 PROD (DESKTOP)]**

21. ✅ **FR21**: O sistema deve detectar cansaço extremo crítico após 3 mensagens consecutivas e sugerir proativamente autocuidado (ex: banho relaxante) de forma empática e integrada à resposta. **[V1.0 PROD (DESKTOP)]**

### Non Functional

1. **NFR1**: O sistema deve responder a mensagens do WhatsApp em menos de 3 segundos para 95% das requisições, garantindo experiência fluida de conversação.

2. **NFR2**: O sistema deve manter disponibilidade de 99.5% durante horários comerciais, com capacidade de escalar automaticamente em picos de demanda.

3. **NFR3**: O sistema deve garantir segurança e privacidade de dados médicos, seguindo LGPD (Lei Geral de Proteção de Dados) e boas práticas de segurança da informação.

4. **NFR4**: O sistema deve armazenar dados de forma criptografada, especialmente informações sensíveis de saúde das pacientes.

5. **NFR5**: O sistema deve ser capaz de processar até 100 conversas simultâneas sem degradação significativa de performance.

6. **NFR6**: O sistema deve manter logs detalhados de todas as interações para auditoria e melhoria contínua, com retenção mínima de 1 ano.

7. **NFR7**: O sistema deve ser desenvolvido de forma a permitir fácil manutenção e expansão, com código modular e documentado.

8. **NFR8**: O sistema deve ter interface responsiva que funcione adequadamente em dispositivos móveis e desktop, com layout otimizado para telas grandes (≥1200px) aproveitando espaço lateral disponível.

8.1. ✅ **NFR8.1**: A interface desktop deve utilizar layout de 3 colunas quando em telas ≥1200px, preenchendo efetivamente o espaço disponível e evitando sensação de conteúdo "soltando" no meio da tela. **[V1.0 PROD (DESKTOP) - Sprint UX-2]**

8.2. ✅ **NFR8.2**: A paleta de cores deve transmitir sensação de calor e acolhimento, utilizando gradientes quentes e elementos visuais decorativos que criem ambiente acolhedor. **[V1.0 PROD (DESKTOP) - Sprint UX-1]**

8.3. ✅ **NFR8.3**: O sistema deve incorporar conteúdo externo (vídeos do YouTube) utilizando modo de privacidade aprimorada (`youtube-nocookie.com`) para minimizar rastreamento de usuários até interação com o conteúdo, e deve informar usuários sobre a presença de conteúdo externo conforme LGPD. **[V1.0 PROD (DESKTOP) - Sprint UX-3]**

8.4. ✅ **NFR8.4**: O sistema deve implementar interface mobile-first responsiva que funcione adequadamente em dispositivos móveis (smartphones e tablets), com layout adaptado para telas pequenas e interações touch-friendly. **[PENDENTE - Épico 7]**

9. **NFR9**: O sistema deve implementar tratamento de erros robusto, fornecendo mensagens claras ao usuário e logs detalhados para desenvolvedores.

10. **NFR10**: O sistema deve ter capacidade de backup automático de dados críticos (agendamentos, histórico de conversas) com recuperação em caso de falhas.

