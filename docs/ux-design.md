# Design UX - Chatbot Médico de Atendimento Automático

**Designer:** UX Expert Agent  
**Data:** 2025-01-12  
**Projeto:** Sistema de Agendamento via WhatsApp

## 🎨 RESUMO EXECUTIVO

**Foco Principal:** Experiência de agendamento médico via WhatsApp  
**Princípios de Design:** Simplicidade, Empatia, Confiança, Acessibilidade  
**Canais:** WhatsApp (primário), Web (alternativo)

---

## 👥 PERSONAS

### Persona 1: Maria - Paciente Buscando Agendamento

**Idade:** 32 anos  
**Perfil:** Mãe de primeira viagem, 3 meses pós-parto  
**Contexto:** Busca agendar consulta para sintomas de ansiedade

**Características:**
- Usa WhatsApp diariamente
- Prefere comunicação rápida e direta
- Ansiosa sobre saúde do bebê
- Tem pouco tempo livre
- Confortável com tecnologia básica

**Necessidades:**
- Agendar consulta rapidamente
- Entender qual especialidade precisa
- Receber confirmação clara
- Poder cancelar/reagendar facilmente

**Dores:**
- Ligar e ficar em espera
- Não saber qual especialidade procurar
- Horários limitados do consultório
- Esquecer detalhes da consulta

---

### Persona 2: Dr. Carlos - Administrador do Consultório

**Idade:** 45 anos  
**Perfil:** Gerente administrativo do consultório  
**Contexto:** Gerencia agendamentos e operações

**Características:**
- Usa sistema de gestão diariamente
- Prefere eficiência e organização
- Precisa de visibilidade sobre agendamentos
- Responsável por configurações

**Necessidades:**
- Reduzir carga de trabalho administrativo
- Evitar conflitos de agendamento
- Configurar horários e especialidades
- Monitorar uso do sistema

**Dores:**
- Muitas ligações para agendamento
- Conflitos de horário
- Falta de sincronização entre sistemas
- Dificuldade em gerenciar múltiplas especialidades

---

## 🗺️ JORNADAS DO USUÁRIO

### Jornada 1: Agendar Consulta via WhatsApp

```
1. INÍCIO
   └─ Maria abre WhatsApp e encontra número do consultório
   
2. PRIMEIRO CONTATO
   └─ Envia mensagem: "Olá, preciso agendar uma consulta"
   └─ Bot responde: "Olá Maria! Como posso ajudar?"
   
3. DESCRIÇÃO DO PROBLEMA
   └─ Maria: "Estou com muita ansiedade e não estou dormindo bem"
   └─ Bot identifica: Especialidade sugerida - Psiquiatria/Psicologia
   └─ Bot: "Entendo. Baseado no que você descreveu, recomendo uma consulta com Psiquiatria ou Psicologia. Qual você prefere?"
   
4. SELEÇÃO DE ESPECIALIDADE
   └─ Maria: "Psiquiatria"
   └─ Bot: "Perfeito! Vou verificar horários disponíveis..."
   
5. SELEÇÃO DE DATA/HORA
   └─ Bot mostra opções:
      "📅 Horários disponíveis:
       - 15/01 às 10h
       - 15/01 às 14h
       - 16/01 às 9h
      Qual prefere?"
   └─ Maria: "15/01 às 10h"
   
6. CONFIRMAÇÃO
   └─ Bot: "Agendamento confirmado! 
      📅 Data: 15/01/2025
      ⏰ Horário: 10h
      👩‍⚕️ Especialidade: Psiquiatria
      📍 Local: Rua X, 123
      
      Confirma? (Sim/Não)"
   └─ Maria: "Sim"
   
7. FINALIZAÇÃO
   └─ Bot: "✅ Agendamento confirmado! Você receberá um lembrete 24h antes. Precisa de mais alguma coisa?"
   └─ Maria: "Não, obrigada!"
   └─ Bot: "Por nada! Estou aqui se precisar. 😊"
```

**Pontos de Dor Identificados:**
- ⚠️ Se identificação de especialidade estiver errada
- ⚠️ Se não houver horários disponíveis
- ⚠️ Se usuário mudar de ideia

**Oportunidades de Melhoria:**
- ✅ Oferecer múltiplas opções quando confiança baixa
- ✅ Sugerir horários alternativos
- ✅ Permitir fácil cancelamento

---

### Jornada 2: Identificar Especialidade Necessária

```
1. INÍCIO
   └─ Usuário: "Tenho dor de cabeça forte há 3 dias"
   
2. ANÁLISE
   └─ Bot analisa sintomas usando IA
   └─ Bot identifica: Neurologia (confiança: 85%)
   
3. APRESENTAÇÃO
   └─ Bot: "Baseado nos seus sintomas, recomendo uma consulta com Neurologia.
      
      📋 Por quê?
      - Dor de cabeça forte e persistente
      - Duração de 3 dias
      
      💡 Outras opções:
      - Clínica Geral (se preferir começar por aqui)
      - Oftalmologia (se tiver problemas de visão também)
      
      Qual você prefere?"
   
4. DECISÃO DO USUÁRIO
   └─ Usuário escolhe especialidade
   └─ Bot prossegue com agendamento
```

---

### Jornada 3: Cancelar/Reagendar Consulta

```
1. INÍCIO
   └─ Usuário: "Preciso cancelar minha consulta"
   
2. IDENTIFICAÇÃO
   └─ Bot: "Qual consulta você gostaria de cancelar?"
   └─ Bot mostra próximas consultas:
      "1. 15/01 - 10h - Psiquiatria
       2. 20/01 - 14h - Ginecologia"
   
3. SELEÇÃO
   └─ Usuário: "1"
   
4. OPÇÕES
   └─ Bot: "Deseja:
      1. Cancelar
      2. Reagendar
      3. Voltar"
   └─ Usuário: "2"
   
5. REAGENDAMENTO
   └─ Bot mostra novos horários disponíveis
   └─ Usuário seleciona novo horário
   └─ Bot confirma reagendamento
```

---

## 💬 DESIGN DE CONVERSAÇÃO

### Princípios de Conversação

1. **Tom Empático e Acolhedor**
   - Usar linguagem calorosa mas profissional
   - Reconhecer sentimentos do usuário
   - Evitar jargão médico complexo

2. **Clareza e Simplicidade**
   - Mensagens curtas e diretas
   - Uma informação por vez
   - Usar emojis com moderação

3. **Confiança e Transparência**
   - Deixar claro quando é um bot
   - Oferecer opção de falar com humano
   - Ser honesto sobre limitações

### Templates de Mensagens

#### Saudação Inicial
```
Olá! 👋 Sou a Sophia, assistente virtual do Consultório [Nome].

Posso ajudar você a:
• Agendar consultas
• Identificar qual especialidade você precisa
• Informações sobre horários
• Cancelar ou reagendar consultas

Como posso ajudar?
```

#### Identificação de Especialidade
```
Baseado no que você descreveu, recomendo uma consulta com [Especialidade].

📋 Por quê?
[Explicação breve dos sintomas que levaram a essa recomendação]

💡 Outras opções:
• [Alternativa 1] - se [condição]
• [Alternativa 2] - se [condição]

Qual você prefere?
```

#### Confirmação de Agendamento
```
✅ Agendamento confirmado!

📅 Data: [data]
⏰ Horário: [hora]
👩‍⚕️ Especialidade: [especialidade]
📍 Local: [endereço]
👤 Profissional: [nome]

Você receberá um lembrete 24h antes da consulta.

Precisa de mais alguma coisa?
```

#### Fora do Horário Comercial
```
Olá! 👋 

No momento estamos fora do horário de atendimento.
🕐 Horário: Segunda a Sexta, 8h às 18h

Posso ajudar você a:
1. Agendar uma consulta para quando abrirmos
2. Ver informações sobre especialidades
3. Deixar uma mensagem

Em caso de emergência, ligue: 192 (SAMU)

Como posso ajudar?
```

---

## 🎨 COMPONENTES DE INTERFACE

### WhatsApp (Canal Principal)

**Características:**
- Mensagens de texto simples
- Botões de ação rápida (quando disponível)
- Listas interativas
- Emojis para melhor comunicação

**Limitações:**
- Sem rich media complexo
- Depende de recursos do WhatsApp
- Texto deve ser autoexplicativo

### Web (Canal Alternativo)

**Componentes Principais:**

1. **Chat Interface**
   - Balao de mensagens (usuário/bot)
   - Indicador de digitação
   - Timestamp
   - Status de entrega

2. **Seletor de Especialidade**
   - Cards com especialidades
   - Descrição breve
   - Ícone visual
   - Botão de seleção

3. **Calendário de Agendamento**
   - Visualização mensal
   - Horários disponíveis destacados
   - Seleção por clique
   - Confirmação visual

4. **Confirmação de Agendamento**
   - Resumo visual
   - Detalhes destacados
   - Botões de ação (Confirmar/Cancelar)
   - QR Code para adicionar ao calendário

---

## ♿ ACESSIBILIDADE

### Requisitos de Acessibilidade

1. **Linguagem Clara**
   - Evitar termos técnicos complexos
   - Explicar quando necessário
   - Oferecer definições

2. **Navegação Simples**
   - Opções numeradas
   - Comandos de texto simples
   - Menus claros

3. **Suporte a Diferentes Habilidades**
   - Texto alternativo para imagens
   - Contraste adequado (web)
   - Tamanho de fonte legível

4. **Múltiplos Canais**
   - WhatsApp para quem prefere
   - Web para quem precisa de mais recursos
   - Opção de falar com humano

---

## 📱 RESPONSIVIDADE

### WhatsApp
- Otimizado para mobile (nativo)
- Funciona em desktop também
- Mensagens adaptam-se ao tamanho da tela

### Web
- Mobile-first design
- Breakpoints:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
- Touch-friendly (botões grandes)
- Swipe gestures onde apropriado

---

## 🎯 MÉTRICAS DE SUCESSO UX

1. **Taxa de Conclusão de Agendamento**
   - Meta: > 80% dos usuários que iniciam completam

2. **Tempo Médio de Agendamento**
   - Meta: < 3 minutos do início ao fim

3. **Taxa de Erro na Identificação de Especialidade**
   - Meta: < 10% de correções necessárias

4. **Satisfação do Usuário (NPS)**
   - Meta: NPS > 50

5. **Taxa de Uso de Fallback Humano**
   - Meta: < 5% precisam de intervenção humana

---

## ✅ CONCLUSÃO

O design UX foca em **simplicidade, empatia e eficiência**. As jornadas foram mapeadas considerando os pontos de dor dos usuários e oportunidades de melhoria.

**Principais Destaques:**
- Conversação natural e empática
- Múltiplas opções quando confiança baixa
- Processo de agendamento simples e rápido
- Fallbacks para diferentes situações

**Próximos Passos:**
1. Prototipar fluxos principais
2. Testar com usuários reais
3. Iterar baseado em feedback
4. Implementar no desenvolvimento

---

**Documento criado por:** UX Expert Agent  
**Versão:** 1.0

