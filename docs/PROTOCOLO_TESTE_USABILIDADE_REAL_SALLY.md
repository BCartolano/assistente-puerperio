# Protocolo de Teste de Usabilidade Real - Mobile

**Criado por:** Sally (UX Expert)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Aprovado

---

## 🎯 OBJETIVO

Validar se a Sophia Mobile é **100% utilizável com apenas uma mão** (uso real de mães segurando bebês) e se todos os elementos interativos estão acessíveis.

---

## 📋 LISTA DE 5 TAREFAS ONE-HANDED

### **Tarefa 1: Mudar para aba Vacinas e marcar a dose de 2 meses**
**Instrução:** "Usando apenas o polegar da mão dominante, toque na aba 'Vacinas' na parte inferior da tela. Role a timeline até encontrar a vacina de 2 meses e toque para marcar como aplicada."

**O que validar:**
- ✅ Aba "Vacinas" é alcançável com polegar (zona de alcance 30-40% inferior)
- ✅ Botão de marcar vacina é grande o suficiente (≥ 44px × 44px)
- ✅ Scroll da timeline funciona com um dedo
- ✅ Confirmação visual aparece após marcar

**Critérios de sucesso:**
- Tarefa completada em ≤ 30 segundos
- Sem necessidade de usar duas mãos
- Sem dificuldade para alcançar elementos

---

### **Tarefa 2: Enviar mensagem no chat com teclado virtual aberto**
**Instrução:** "Toque no campo de mensagem na parte inferior. Com o teclado virtual aberto, digite 'Estou muito cansada' e envie a mensagem. Verifique se consegue ver o campo de input enquanto digita."

**O que validar:**
- ✅ Input permanece visível acima do teclado virtual
- ✅ Botão de enviar é acessível com teclado aberto
- ✅ Histórico de mensagens permanece visível
- ✅ Indicador de digitação da Sophia aparece no topo

**Critérios de sucesso:**
- Campo de input sempre visível
- Botão de enviar alcançável
- Sem necessidade de rolar para ver input

---

### **Tarefa 3: Ver Quick Replies e responder com uma delas**
**Instrução:** "Depois que a Sophia responder sua mensagem anterior, veja as opções de Quick Replies abaixo da resposta. Toque em 'Preciso de um incentivo' usando apenas o polegar."

**O que validar:**
- ✅ Quick Replies estão na zona de alcance (não muito acima)
- ✅ Botões têm altura mínima de 44px
- ✅ Espaçamento entre botões é adequado (≥ 8px)
- ✅ Feedback visual ao tocar

**Critérios de sucesso:**
- Quick Replies alcançáveis sem precisar ajustar a mão
- Botões não muito próximos (sem toques acidentais)
- Resposta rápida ao tocar

---

### **Tarefa 4: Assistir um vídeo na aba Dicas e fechar**
**Instrução:** "Toque na aba 'Dicas' na parte inferior. Role até encontrar a seção de vídeos. Toque em um vídeo para abrir. Depois, feche o vídeo usando o botão X no canto superior direito."

**O que validar:**
- ✅ Aba "Dicas" é acessível
- ✅ Vídeos carregam apenas quando necessário (lazy loading)
- ✅ Modal abre em fullscreen
- ✅ Botão de fechar (44px × 44px) é fácil de tocar
- ✅ Posição de scroll é restaurada após fechar

**Critérios de sucesso:**
- Vídeo abre em tela cheia
- Botão de fechar grande o suficiente
- Scroll volta para posição original após fechar
- Sem lag ou travamento

---

### **Tarefa 5: Navegar entre as 3 abas rapidamente**
**Instrução:** "Toque rapidamente nas abas Chat, Vacinas e Dicas (nesta ordem). Repita 3 vezes. Verifique se a navegação é fluida e se o conteúdo carrega corretamente."

**O que validar:**
- ✅ Navegação entre abas é instantânea
- ✅ Conteúdo não é perdido ao trocar de aba
- ✅ Histórico de chat é preservado
- ✅ Sem travamentos ou erros

**Critérios de sucesso:**
- Navegação fluida (sem delay perceptível)
- Estado preservado ao voltar para aba anterior
- Sem perda de dados ou conteúdo

---

## 🔍 VALIDAÇÃO DO AVISO DE USO DE DADOS

### **Problema:**
O aviso "📱 Vídeos podem consumir dados móveis" pode ser **irritante** para quem só quer ver o vídeo rapidamente.

### **Teste A/B Sugerido:**

#### **Versão A: Aviso Visível (Atual)**
- Texto abaixo do título "Vídeos Educativos"
- Cor: cinza (#999)
- Tamanho: 0.75rem
- Visível sempre

#### **Versão B: Aviso Discreto (Alternativa)**
- Texto menor (0.7rem)
- Opacidade reduzida (0.7)
- Aparece apenas no primeiro carregamento
- Desaparece após 5 segundos

### **Métricas de Validação:**

1. **Questionário Pós-Uso:**
   - "O aviso sobre uso de dados te incomodou?" (Escala 1-5)
   - "Você percebeu o aviso?" (Sim/Não)
   - "O aviso te impediu de assistir algum vídeo?" (Sim/Não)

2. **Observação:**
   - Tempo até primeiro vídeo ser aberto
   - Número de vídeos assistidos por sessão
   - Se usuário fecha modal imediatamente após ver aviso

3. **Decisão:**
   - Se ≥ 70% responderem "Não me incomodou" → **Manter Versão A**
   - Se ≥ 70% responderem "Me incomodou" → **Implementar Versão B**

---

## 📐 AVALIAÇÃO DO INDICADOR DE DIGITAÇÃO STICKY

### **Problema:**
O indicador sticky no topo do chat pode "comer" muito espaço vertical quando o teclado está aberto, reduzindo a área visível de mensagens.

### **Análise de Espaço:**

**Elementos na tela quando teclado está aberto:**
1. Indicador de digitação: ~40px (sticky no topo)
2. Histórico de mensagens: altura variável (scrollável)
3. Input area: ~70px (fixo acima do teclado)
4. Teclado virtual: ~250-300px (altura variável por dispositivo)

**Total de espaço vertical ocupado:** ~360-410px  
**Espaço disponível para mensagens (iPhone 12, altura 844px):** ~434-484px

### **Recomendação:**

✅ **Indicador sticky é aceitável** se:
- Altura do indicador ≤ 40px
- Não ocupa mais de 5% da altura total da tela
- Mensagens ainda são legíveis (fonte ≥ 0.9rem)

⚠️ **Ajustar se:**
- Usuários reclamarem de espaço reduzido
- Mensagens ficarem muito pequenas
- Scroll ficar difícil com teclado aberto

### **Alternativa (Futuro):**
Se indicador sticky causar problemas:
- Mover indicador para **dentro do input area** (ao lado do botão enviar)
- Ou fazer indicador **sumir quando teclado abre** (mostrar apenas quando teclado fechado)

---

## ✅ CHECKLIST DE TESTE

### **Pré-Teste:**
- [ ] Dispositivo carregado com bateria ≥ 50%
- [ ] Conexão 4G/5G ativa (não WiFi)
- [ ] Aplicativo limpo (sem cache)
- [ ] Testador em posição confortável (sentado ou em pé)

### **Durante o Teste:**
- [ ] Gravar tela (para análise posterior)
- [ ] Cronometrar cada tarefa
- [ ] Anotar dificuldades ou erros
- [ ] Observar expressões faciais (frustração/alívio)

### **Pós-Teste:**
- [ ] Questionário de satisfação (escala 1-5)
- [ ] Entrevista curta (5 minutos)
- [ ] Coletar feedback sobre aviso de dados
- [ ] Avaliar necessidade de ajustes

---

## 📊 MÉTRICAS DE SUCESSO

### **Critérios de Aceitação:**

1. **Acessibilidade One-Handed:**
   - ✅ 100% das tarefas completadas sem usar duas mãos
   - ✅ Tempo médio por tarefa ≤ 30 segundos
   - ✅ Taxa de erro ≤ 10%

2. **Usabilidade:**
   - ✅ Satisfação geral ≥ 4.0/5.0
   - ✅ 90% dos usuários conseguem completar todas as tarefas
   - ✅ Sem reclamações sobre elementos muito pequenos

3. **Performance:**
   - ✅ Navegação sem lag perceptível
   - ✅ Conteúdo carrega em ≤ 2 segundos
   - ✅ Sem travamentos ou crashes

---

## 📝 PRÓXIMOS PASSOS

1. **Realizar testes** com 5-10 mães reais
2. **Coletar feedback** sobre aviso de dados
3. **Avaliar espaço do indicador** sticky
4. **Documentar resultados** e sugerir ajustes
5. **Iterar** com base no feedback

---

**Versão:** 1.0  
**Status:** ✅ Aprovado  
**Próxima Revisão:** Após realização dos testes
