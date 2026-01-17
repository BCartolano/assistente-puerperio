# Arquitetura - Streaming de Respostas e Persistência de Histórico

**Arquiteto:** Winston (Architect)  
**Data:** 2025-01-08  
**Solicitante:** Dev  

---

## 🎯 OBJETIVOS

1. Implementar streaming de respostas (efeito máquina de escrever) para melhorar UX
2. Persistir últimas 5 mensagens da conversa no localStorage
3. Restaurar histórico ao recarregar página
4. Otimizar performance e experiência do usuário

---

## 🚀 STREAMING DE RESPOSTAS

### Estratégia: Token-by-Token com SSE (Server-Sent Events) ou Simulação

**Opção 1: SSE (Recomendado para produção)**
- Backend envia resposta via Server-Sent Events
- Frontend recebe tokens progressivamente
- Melhor experiência do usuário

**Opção 2: Simulação (Implementação rápida)**
- Backend retorna resposta completa
- Frontend simula streaming token por token
- Mais simples de implementar

**Recomendação:** Implementar Opção 2 primeiro (simulação), depois migrar para SSE se necessário.

### Implementação: Simulação de Streaming

#### Backend: API Retorna Resposta Completa (sem mudanças)
A API `/api/chat` continua retornando a resposta completa.

#### Frontend: Função de Streaming

```javascript
async typewriterEffect(element, text, speed = 30) {
    // Limpa elemento
    element.textContent = '';
    
    // Cria span para animação
    const textSpan = document.createElement('span');
    element.appendChild(textSpan);
    
    // Adiciona caractere por caractere
    for (let i = 0; i < text.length; i++) {
        textSpan.textContent += text[i];
        
        // Pausa entre caracteres (velocidade adaptável)
        await new Promise(resolve => setTimeout(resolve, speed));
        
        // Scroll automático durante digitação
        if (i % 10 === 0) { // A cada 10 caracteres
            this.scrollToBottom();
        }
    }
    
    // Scroll final
    this.scrollToBottom();
}
```

#### Atualização do addMessage:

```javascript
addMessage(content, sender, metadata = {}, useStreaming = true) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    
    // ... código de avatar, time, etc. ...
    
    const messageTextElement = document.createElement('div');
    messageTextElement.className = 'message-text';
    
    // Se for assistente e streaming habilitado, usa efeito máquina de escrever
    if (sender === 'assistant' && useStreaming) {
        // Renderiza estrutura primeiro
        messageElement.innerHTML = `
            <div class="message-avatar">🤱</div>
            <div class="message-content">
                <div class="message-text"></div>
                ${categoryBadge}
                ${alertSection}
                <div class="message-time">${time}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageElement);
        
        // Aplica streaming no elemento de texto
        const textElement = messageElement.querySelector('.message-text');
        this.typewriterEffect(textElement, content, 25); // 25ms por caractere
    } else {
        // Renderização normal (instantânea)
        messageTextElement.innerHTML = this.formatMessage(content);
        messageElement.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(content)}</div>
                ${categoryBadge}
                ${alertSection}
                <div class="message-time">${time}</div>
            </div>
        `;
        this.chatMessages.appendChild(messageElement);
    }
    
    this.scrollToBottom();
}
```

---

## 💾 PERSISTÊNCIA DE HISTÓRICO

### Estratégia: localStorage + Últimas 5 Mensagens

#### Estrutura de Dados:

```javascript
{
    "chat_history": [
        {
            "content": "Como está o bebê?",
            "sender": "user",
            "timestamp": "2025-01-08T10:30:00Z",
            "metadata": {}
        },
        {
            "content": "Oi! Que bom te ver por aqui! ...",
            "sender": "assistant",
            "timestamp": "2025-01-08T10:30:05Z",
            "metadata": {
                "fonte": "openai",
                "categoria": "saudacao"
            }
        }
        // ... até 5 mensagens (3 user + 2 assistant ou equivalente)
    ],
    "last_updated": "2025-01-08T10:30:05Z"
}
```

#### Funções de Persistência:

```javascript
// Salvar histórico
saveChatHistory() {
    try {
        const messages = Array.from(this.chatMessages.children)
            .slice(-5) // Últimas 5 mensagens
            .map(msgEl => {
                const sender = msgEl.classList.contains('user') ? 'user' : 'assistant';
                const content = msgEl.querySelector('.message-text')?.textContent || '';
                const time = msgEl.querySelector('.message-time')?.textContent || '';
                
                return {
                    content: content,
                    sender: sender,
                    timestamp: new Date().toISOString(),
                    metadata: this.getMessageMetadata(msgEl) // Extrai categoria, etc.
                };
            });
        
        localStorage.setItem('sophia_chat_history', JSON.stringify({
            chat_history: messages,
            last_updated: new Date().toISOString()
        }));
        
        this.log('✅ Histórico salvo no localStorage');
    } catch (error) {
        this.error('Erro ao salvar histórico:', error);
    }
}

// Carregar histórico
loadChatHistory() {
    try {
        const saved = localStorage.getItem('sophia_chat_history');
        if (!saved) return [];
        
        const data = JSON.parse(saved);
        
        // Verifica se histórico não é muito antigo (últimas 24h)
        const lastUpdated = new Date(data.last_updated);
        const now = new Date();
        const hoursSinceUpdate = (now - lastUpdated) / (1000 * 60 * 60);
        
        if (hoursSinceUpdate > 24) {
            // Histórico muito antigo, limpa
            localStorage.removeItem('sophia_chat_history');
            return [];
        }
        
        return data.chat_history || [];
    } catch (error) {
        this.error('Erro ao carregar histórico:', error);
        return [];
    }
}

// Restaurar histórico na tela
restoreChatHistory() {
    const history = this.loadChatHistory();
    
    if (history.length === 0) return;
    
    // Limpa mensagens atuais
    if (this.chatMessages) {
        this.chatMessages.innerHTML = '';
    }
    
    // Restaura mensagens (sem streaming, instantâneo)
    history.forEach(msg => {
        this.addMessage(msg.content, msg.sender, msg.metadata || {}, false); // false = sem streaming
    });
    
    // Scroll para o final
    this.scrollToBottom();
    
    this.log(`✅ Histórico restaurado: ${history.length} mensagens`);
}
```

#### Integração:

```javascript
// No sendMessage(), após receber resposta
// Salva histórico após adicionar mensagem
this.saveChatHistory();

// No initMainApp(), ao inicializar
// Restaura histórico ao carregar
this.restoreChatHistory();
```

---

## 🏷️ SISTEMA DE TAGS DE CONTEXTO

### Implementação: Tags Passadas para OpenAI

#### Backend (já implementado):

```python
def _detectar_contexto_tags(self, pergunta, user_id):
    tags = []
    
    # Verifica crise emocional
    if user_id in SESSION_ALERT and SESSION_ALERT[user_id].get("ativo", False):
        tags.append("crise_emocional")
        nivel = SESSION_ALERT[user_id].get("nivel", "leve")
        tags.append(f"nivel_risco_{nivel}")
    
    # Detecta emoções
    # ... código de detecção ...
    
    return tags
```

#### Integração no System Prompt:

As tags são enviadas como parte do contexto para a OpenAI:

```
[Tags de Contexto: 
- crise_emocional
- nivel_risco_alto
- busca_apoio_emocional
]

[Contexto: ...]

Pergunta do usuário
```

#### Ajuste do System Prompt para Usar Tags:

```
Você é a Sophia, uma Inteligência Artificial EMPÁTICA...

**TAGS DE CONTEXTO:**
Quando receber tags de contexto, ajuste seu tom:

- **crise_emocional**: Priorize empatia, validação e orientação para ajuda profissional. 
  Seja EXTRA acolhedora e paciente.

- **celebração**: Seja entusiasmada e genuinamente feliz. Celebre com a mãe!

- **cansaço_extremo**: Valide o cansaço, ofereça suporte prático sem minimizar.

- **busca_orientação**: Forneça informações claras e práticas, integrando dados 
  disponíveis (vacinas, dicas, etc.).

- **dúvida_vacina**: Consulte o contexto da próxima vacina e forneça informações precisas.

- **dúvida_amamentação**: Ofereça orientações práticas baseadas na idade do bebê.
```

---

## 🎨 CSS PARA STREAMING

### Efeito Visual Durante Streaming:

```css
.message.assistant .message-text.streaming {
    position: relative;
}

.message.assistant .message-text.streaming::after {
    content: '▋';
    animation: blink 1s infinite;
    color: var(--color-primary-warm, #ff8fa3);
    margin-left: 2px;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
```

---

## 📊 ESTRUTURA DE DADOS DE HISTÓRICO

### localStorage Key: `sophia_chat_history`

```json
{
    "chat_history": [
        {
            "content": "Como está o bebê?",
            "sender": "user",
            "timestamp": "2025-01-08T10:30:00.000Z",
            "metadata": {
                "categoria": null,
                "fonte": null
            }
        },
        {
            "content": "Oi! Que bom te ver...",
            "sender": "assistant",
            "timestamp": "2025-01-08T10:30:05.000Z",
            "metadata": {
                "categoria": "saudacao",
                "fonte": "openai"
            }
        }
    ],
    "last_updated": "2025-01-08T10:30:05.000Z"
}
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Streaming:
- [ ] Função `typewriterEffect()` implementada
- [ ] `addMessage()` atualizado para usar streaming
- [ ] CSS para cursor piscante durante streaming
- [ ] Scroll automático durante digitação
- [ ] Velocidade ajustável (rápida/lenta)

### Persistência:
- [ ] Função `saveChatHistory()` implementada
- [ ] Função `loadChatHistory()` implementada
- [ ] Função `restoreChatHistory()` implementada
- [ ] Limpeza automática de histórico antigo (>24h)
- [ ] Integração no `sendMessage()` e `initMainApp()`

### Tags de Contexto:
- [x] Função `_detectar_contexto_tags()` implementada
- [x] Tags enviadas para OpenAI
- [ ] System Prompt atualizado para usar tags
- [ ] Testes com diferentes contextos

---

## 🔄 FLUXO COMPLETO

1. **Usuário envia mensagem**
2. **Frontend**: Mostra typing indicator
3. **Backend**: Processa, detecta tags, busca contexto
4. **Backend**: Retorna resposta completa
5. **Frontend**: Remove typing, aplica streaming
6. **Frontend**: Salva no histórico (localStorage)
7. **Usuário recarrega página**
8. **Frontend**: Restaura últimas 5 mensagens

---

**Arquitetura criada por:** Winston (Architect)  
**Data:** 2025-01-08  
**Versão:** 1.0
