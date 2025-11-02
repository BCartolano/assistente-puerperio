# 📋 Funcionalidades Planejadas - Assistente Puerpério Completo

## ✅ Já Implementado

### Base de Conhecimento
- ✅ 79 perguntas e respostas sobre gestação, parto, puerpério, amamentação, cuidados com bebê
- ✅ 10 mensagens de apoio empáticas para quando não houver resposta específica
- ✅ Sistema de alertas médicos
- ✅ Chatbot inteligente com fallback para OpenAI

### Interface
- ✅ Design responsivo e moderno
- ✅ Chat em tempo real
- ✅ Perguntas rápidas
- ✅ Histórico de conversas
- ✅ Modal de alertas médicos

---

## 🚀 Funcionalidades a Implementar

### 1. 📞 Telefones Úteis ✅ IMPLEMENTADO
- ✅ Arquivo `telefones_uteis.json` criado
- ✅ Integrado ao backend
- ✅ Rota `/api/telefones` criada
- ✅ Telefones adicionados automaticamente nas respostas
- ✅ CVV 188 incluído em respostas sobre depressão
- ✅ Telefones de emergência em casos de alerta médico
- ⏳ Interface para exibir telefones no frontend
- ⏳ Botão de ligação direta no modal de alerta

### 2. 🩺 Guias Práticos com Imagens
**Status:** A CRIAR

**Conteúdo:**
- Cólica do bebê: passos com imagens
- Manobra de Heimlich: passos com imagens
- Primeiros socorros básicos
- Técnicas de amamentação
- Posições para dormir
- Banho do bebê

**Estrutura:**
```json
{
  "colica": {
    "titulo": "Como aliviar cólicas do bebê",
    "passos": [
      {"numero": 1, "texto": "Aqueça uma compressa...", "imagem": "colica1.jpg"},
      {...}
    ]
  }
}
```

### 3. 👤 Sistema de Cadastro
**Status:** A CRIAR

**Campos:**
- Nome completo
- Data prevista do parto / Data do parto
- Email
- Telefone
- Endereço (cidade, estado)
- Tipo de parto planejado (normal/cesárea)
- Histórico médico relevante

**Funcionalidades:**
- Personalizar conteúdo conforme etapa
- Alertas relevantes para a gestação/puerpério
- Histórico personalizado

### 4. 📅 Cuidados Semanais - Gestação
**Status:** A CRIAR

**Estrutura:**
- Semana 1-40
- Cuidados físicos
- Desenvolvimento do bebê
- Exames necessários
- Alimentação
- Sinais de alerta

### 5. 📅 Cuidados Semanais - Pós-Parto
**Status:** A CRIAR

**Estrutura:**
- Semana 1-24 (primeiros 6 meses)
- Recuperação física
- Cuidados emocionais
- Desenvolvimento do bebê
- Amamentação
- Sinais de alerta

### 6. 💉 Carteira de Vacinação
**Status:** A CRIAR

**Carteira da Mãe:**
- Vacinas importantes no pré-natal
- Vacinas pós-parto
- Calendário completo

**Carteira da Criança:**
- Vacinas do recém-nascido
- Calendário 0-12 meses
- Quando e onde vacinar
- Efeitos colaterais comuns

---

## 🎯 Prioridade de Implementação

### Fase 1 - Essencial (AGORA)
1. ✅ Telefones úteis - JSON criado
2. Integrar telefones ao sistema de alertas
3. Adicionar links para CVV nas respostas sobre depressão
4. Atualizar base de conhecimento com referências

### Fase 2 - Importante
1. Cuidados semanais gestação (40 semanas)
2. Cuidados semanais puerpério (24 semanas)
3. Sistema de cadastro básico

### Fase 3 - Melhorias
1. Guias práticos com imagens
2. Carteira de vacinação completa
3. Cadastro avançado com personalização

---

## 📁 Estrutura de Arquivos

```
dados/
├── base_conhecimento.json ✅ (79 categorias)
├── mensagens_apoio.json ✅ (10 mensagens)
├── alertas.json ✅
├── telefones_uteis.json ✅ NOVO
├── guias_praticos.json ⏳ A CRIAR
├── cuidados_gestacao.json ⏳ A CRIAR
├── cuidados_pos_parto.json ⏳ A CRIAR
├── vacinas_mae.json ⏳ A CRIAR
└── vacinas_bebe.json ⏳ A CRIAR
```

---

## 🔗 Integrações Necessárias

### Backend (app.py)
- Nova rota: `/api/telefones`
- Nova rota: `/api/guias`
- Nova rota: `/api/cuidados/gestacao/<semana>`
- Nova rota: `/api/cuidados/puerperio/<semana>`
- Nova rota: `/api/vacinas/mae`
- Nova rota: `/api/vacinas/bebe`
- Modificar `/api/chat` para incluir links de telefones quando relevante

### Frontend
- Nova seção: "Telefones Úteis" no sidebar
- Nova seção: "Guias Práticos"
- Nova seção: "Meus Cuidados Semanais"
- Nova seção: "Carteira de Vacinação"
- Modificar modal de alerta para exibir telefones clicáveis
- Adicionar imagens aos guias

---

## 🎨 Melhorias de UI/UX

1. **Dashboard Personalizado**
   - Mostrar semana atual da gestação/puerpério
   - Cuidados do dia
   - Próximas vacinas
   - Alertas importantes

2. **Mensagens de Apoio Aprimoradas**
   - Incluir links para telefones quando relevante
   - Botão "Preciso de ajuda profissional"
   - Botão "Ligar CVV 188" nas respostas sobre depressão

3. **Alertas Inteligentes**
   - Baseado na semana atual
   - Sinais de alerta específicos
   - Próximos exames
   - Vacinas próximas

---

## 📝 Próximos Passos

### PASSO 1: Integrar Telefones ✅ COMPLETO
- [x] Carregar `telefones_uteis.json` no backend
- [x] Criar rota `/api/telefones`
- [x] Adicionar telefones automaticamente nas respostas relevantes
- [x] Incluir telefone CVV nas respostas sobre depressão
- [x] Incluir telefones de emergência em alertas médicos

### PASSO 2: Expandir Base de Conhecimento
- [ ] Adicionar referências a telefones úteis
- [ ] Adicionar links para guias futuros
- [ ] Melhorar mensagens de alerta

### PASSO 3: Criar Cuidados Semanais
- [ ] Pesquisar conteúdo para gestação (40 semanas)
- [ ] Pesquisar conteúdo para puerpério (24 semanas)
- [ ] Criar JSONs estruturados
- [ ] Implementar rotas API

### PASSO 4: Sistema de Cadastro
- [ ] Criar modelo de usuário
- [ ] Implementar login/registro
- [ ] Personalizar conteúdo por usuário

---

**Status Atual:** Fase 1, Passo 1 - Telefones integrados ✅ - Próximo: Guias Práticos e Cuidados Semanais

