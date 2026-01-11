# Checklist de Teste Mobile - Sophia

**Criado por:** Sally (UX Expert)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Pronto para Uso

---

## 📱 INSTRUÇÕES DE USO

**Como usar este checklist:**
1. Abra este documento no seu computador ou imprima
2. Teste cada tarefa no seu celular
3. Marque ✅ (passou) ou ❌ (falhou) para cada item
4. Anote observações na coluna "Observações"
5. Foque especialmente na **transição Chat → Vacinas** quando o teclado virtual está aberto

---

## ✅ CHECKLIST DE TESTE

### **Tarefa 1: Mudar para aba Vacinas e marcar vacina de 2 meses**

| Item | Critério | ✅/❌ | Observações |
|------|----------|------|-------------|
| 1.1 | Aba "Vacinas" alcançável com polegar (zona inferior) | | |
| 1.2 | Toque abre aba Vacinas sem delay perceptível | | |
| 1.3 | Timeline de vacinas carrega corretamente | | |
| 1.4 | Scroll da timeline funciona com um dedo | | |
| 1.5 | Vacina de 2 meses visível e legível | | |
| 1.6 | Botão de marcar vacina tem ≥ 44px × 44px | | |
| 1.7 | Ao marcar, confirmação visual aparece | | |
| 1.8 | Modal de comemoração aparece com efeito de confetes | | |

**Tempo total:** _____ segundos  
**Usou duas mãos?** Sim / Não

---

### **Tarefa 2: Enviar mensagem no chat com teclado virtual aberto**

| Item | Critério | ✅/❌ | Observações |
|------|----------|------|-------------|
| 2.1 | Campo de input acessível na parte inferior | | |
| 2.2 | Ao tocar no input, teclado virtual abre | | |
| 2.3 | **Input permanece visível acima do teclado** | | |
| 2.4 | Histórico de mensagens permanece visível (acima do input) | | |
| 2.5 | Botão de enviar acessível com teclado aberto | | |
| 2.6 | Ao digitar "Estou muito cansada", texto é visível | | |
| 2.7 | Ao enviar, mensagem aparece no chat | | |
| 2.8 | Indicador de digitação da Sophia aparece no topo (sticky) | | |
| 2.9 | **Indicador NÃO "come" muito espaço vertical** | | |

**Tempo total:** _____ segundos  
**Conseguiu ver tudo enquanto digitava?** Sim / Não  
**Indicador sticky incomodou?** Sim / Não

---

### **Tarefa 3: Ver Quick Replies e responder com uma delas**

| Item | Critério | ✅/❌ | Observações |
|------|----------|------|-------------|
| 3.1 | Após resposta da Sophia, Quick Replies aparecem | | |
| 3.2 | Quick Replies estão na zona de alcance (não muito acima) | | |
| 3.3 | Botões têm altura mínima de 44px | | |
| 3.4 | Espaçamento entre botões é adequado (≥ 8px) | | |
| 3.5 | Ao tocar em "Preciso de um incentivo", ação é executada | | |
| 3.6 | Resposta aparece corretamente no chat | | |

**Tempo total:** _____ segundos  
**Botões eram fáceis de tocar?** Sim / Não

---

### **Tarefa 4: Assistir vídeo na aba Dicas e fechar**

| Item | Critério | ✅/❌ | Observações |
|------|----------|------|-------------|
| 4.1 | Aba "Dicas" acessível na bottom navigation | | |
| 4.2 | Lista de cards aparece (Dica do Dia, Afirmação, etc.) | | |
| 4.3 | Seção de vídeos aparece na lista | | |
| 4.4 | **Aviso de uso de dados visível mas não irritante** | | |
| 4.5 | Ao tocar em vídeo, modal abre em fullscreen | | |
| 4.6 | Vídeo carrega corretamente (sem erros de Toast) | | |
| 4.7 | Botão de fechar (44px × 44px) é fácil de tocar | | |
| 4.8 | Ao fechar, vídeo para imediatamente (sem áudio) | | |
| 4.9 | **Scroll volta para posição original** | | |

**Tempo total:** _____ segundos  
**O aviso de dados te incomodou?** Sim / Não / Não percebi  
**Vídeo carregou rápido?** Sim / Não

---

### **Tarefa 5: Navegar entre as 3 abas rapidamente**

| Item | Critério | ✅/❌ | Observações |
|------|----------|------|-------------|
| 5.1 | Chat → Vacinas: transição fluida (sem lag) | | |
| 5.2 | Vacinas → Dicas: transição fluida (sem lag) | | |
| 5.3 | Dicas → Chat: transição fluida (sem lag) | | |
| 5.4 | **Chat → Vacinas com teclado aberto: sem "engasgar"** | | |
| 5.5 | Ao voltar para Chat, histórico preservado | | |
| 5.6 | Ao voltar para Vacinas, posição de scroll preservada | | |
| 5.7 | Sem travamentos ou erros durante navegação | | |

**Repetir 3 vezes:** ✅ Passou / ❌ Falhou  
**Observações sobre "engasgar":** ________________________________

---

## 🔍 VALIDAÇÃO ESPECIAL: TRANSIÇÃO CHAT → VACINAS COM TECLADO

### **Cenário de Teste:**
1. Abrir Chat
2. Tocar no input (teclado virtual abre)
3. **Imediatamente** tocar na aba Vacinas (teclado fecha)
4. Observar animação da Bottom Navigation

### **O que observar:**

| Item | Critério | ✅/❌ | Observações |
|------|----------|------|-------------|
| TE1 | Teclado fecha suavemente (sem "pulo") | | |
| TE2 | Bottom Navigation anima corretamente | | |
| TE3 | Input area retorna à posição normal | | |
| TE4 | **Sem "engasgar" ou lag perceptível** | | |
| TE5 | Aba Vacinas abre corretamente | | |

**Detalhar qualquer "engasgar":** ________________________________

---

## 📊 AVALIAÇÃO DO AVISO DE USO DE DADOS

### **Teste A/B Sugerido:**

**Versão A (Atual):**
- Texto abaixo do título "Vídeos Educativos"
- Sempre visível
- Cor: cinza (#999)
- Tamanho: 0.75rem

**Avaliação:**

| Pergunta | Resposta | Observações |
|----------|----------|-------------|
| Você percebeu o aviso? | Sim / Não | |
| O aviso te incomodou? | Sim / Não | |
| Ele te impediu de assistir algum vídeo? | Sim / Não | |
| Qual sua opinião sobre o aviso? | | |

**Recomendação:** Manter Versão A / Implementar Versão B mais discreta / Remover

---

## 📊 AVALIAÇÃO DO INDICADOR STICKY

### **Teste Especial:**
1. Abrir Chat
2. Enviar mensagem (indicador aparece no topo)
3. Abrir teclado virtual
4. Observar espaço vertical disponível

| Pergunta | Resposta | Observações |
|----------|----------|-------------|
| O indicador ocupa muito espaço? | Sim / Não | |
| Mensagens continuam legíveis? | Sim / Não | |
| Scroll funciona bem com indicador + teclado? | Sim / Não | |
| Altura aproximada do indicador: | _____ px | |

**Recomendação:** Manter / Reduzir altura / Mover para outra posição

---

## ✅ RESUMO FINAL

### **Tarefas Completadas:**
- ✅ Tarefa 1: _____ / 8 itens
- ✅ Tarefa 2: _____ / 9 itens
- ✅ Tarefa 3: _____ / 6 itens
- ✅ Tarefa 4: _____ / 9 itens
- ✅ Tarefa 5: _____ / 7 itens

### **Taxa de Sucesso Geral:**
- **Total de itens passou:** _____ / 39
- **Percentual:** _____%

### **Problemas Críticos Encontrados:**
1. ________________________________
2. ________________________________
3. ________________________________

### **Observações Gerais:**
________________________________
________________________________
________________________________

---

## 📝 PRÓXIMOS PASSOS

1. ✅ Completar checklist durante testes
2. ⏳ Anotar todas as observações
3. ⏳ Reportar problemas críticos
4. ⏳ Avaliar feedback sobre aviso de dados
5. ⏳ Decidir ajustes necessários

---

**Versão:** 1.0  
**Status:** ✅ Pronto para Uso  
**Próxima Revisão:** Após realização dos testes
