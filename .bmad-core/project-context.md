# Contexto do Projeto: Chatbot Puerpério da Sophia

## Visão Geral do Projeto

O **Chatbot Puerpério da Sophia** é um sistema de atendimento automático especializado em fornecer suporte, informações e orientações para mulheres no período puerperal (pós-parto). O chatbot oferece assistência 24/7 via WhatsApp e interface web, focando em cuidados maternos e do bebê.

## Objetivo Principal

Criar um chatbot inteligente que:
- Fornece informações confiáveis sobre cuidados pós-parto
- Orienta sobre cuidados com o bebê
- Oferece suporte emocional durante o puerpério
- Agenda consultas médicas
- Integra com sistemas internos do consultório

## Requisitos Principais

### Funcionalidades Core
- **Identificação de Especialidade**: O chatbot deve identificar a especialidade médica necessária baseada nos sintomas e necessidades da paciente
- **Agendamento de Consultas**: Sistema de agendamento integrado com a agenda do consultório
- **Atendimento via WhatsApp**: Interface principal de comunicação
- **Horários Comerciais**: Funcionamento durante horários comerciais com suporte de emergência
- **Integração com Sistema Interno**: Conexão com sistemas de gestão do consultório

### Tecnologias Utilizadas
- **Backend**: Python (Flask)
- **Frontend**: HTML/CSS/JavaScript
- **Banco de Dados**: SQLite (users.db)
- **IA/ML**: Sistema RAG (Retrieval Augmented Generation) para busca de conhecimento
- **Integração**: WhatsApp API, Sistema de agendamento

## Estrutura do Projeto

```
chatbot-puerperio/
├── backend/              # Aplicação Flask principal
│   ├── app.py          # Servidor principal
│   ├── loader.py       # Carregador de base de conhecimento
│   ├── base_conhecimento.json  # Base de dados RAG
│   └── templates/      # Templates HTML
├── .bmad-core/         # Framework BMAD instalado
├── docs/               # Documentação do projeto
└── web-bundles/        # Bundles BMAD para uso web
```

## Base de Conhecimento

O projeto possui uma base de conhecimento extensa em JSON contendo:
- Cuidados na gestação
- Cuidados pós-parto
- Cuidados com o bebê
- Guias práticos
- Mensagens de apoio
- Alertas importantes
- Telefones úteis
- Informações sobre vacinas (mãe e bebê)

## Estado Atual do Projeto

- ✅ Backend Flask funcional
- ✅ Sistema RAG implementado
- ✅ Interface web básica
- ✅ Integração WhatsApp (parcial)
- ✅ Base de conhecimento populada
- ⚠️ Sistema de agendamento (em desenvolvimento)
- ⚠️ Integração com sistema interno (pendente)

## Próximos Passos com BMAD

1. **PM (Product Manager)**: Criar PRD completo para o chatbot médico
2. **Architect**: Definir arquitetura de integração com sistemas internos
3. **Dev**: Implementar funcionalidades de agendamento
4. **QA**: Testar fluxos de atendimento e agendamento
5. **UX**: Melhorar experiência do usuário no WhatsApp

## Tarefa Atual do PM

**Criar a visão completa e o PRD de um chatbot médico de atendimento automático** com foco em:
- Identificação de especialidade
- Agendamento de consulta
- Atendimento via WhatsApp
- Horários comerciais
- Integração com sistema interno

## Notas Importantes

- O projeto já possui uma base sólida de conhecimento e funcionalidades básicas
- O foco atual é expandir para um sistema completo de atendimento médico
- A integração com sistemas internos é crítica para o sucesso
- O atendimento via WhatsApp é a interface principal de comunicação

