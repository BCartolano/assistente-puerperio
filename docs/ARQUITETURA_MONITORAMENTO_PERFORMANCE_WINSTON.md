# Arquitetura de Monitoramento e Performance - Mobile

**Criado por:** Winston (Architect)  
**Data:** 2025-01-27  
**Versão:** 1.0  
**Status:** ✅ Aprovado

---

## 🔍 MONITORAMENTO DE STREAMING ADAPTATIVO (15ms)

### **Problema:**
Em redes 3G lentas, o streaming adaptativo de 15ms pode causar **perda de pacotes** ou **requisições incompletas**, resultando em respostas truncadas.

### **Solução: Monitoramento de Erros de Rede**

#### **1. Implementar Logging de Erros de Streaming**

```javascript
// Em chat.js, método typewriterEffect
async typewriterEffect(element, text, speed = 25) {
    const isMobile = window.innerWidth <= 1023;
    const streamingSpeed = isMobile ? 15 : 25;
    
    // Monitora erros durante streaming
    let errorCount = 0;
    const maxErrors = 3;
    
    try {
        for (let i = 0; i < text.length; i++) {
            element.textContent += text[i];
            
            if (i < text.length - 1) {
                await new Promise(resolve => setTimeout(resolve, streamingSpeed));
                
                // Se streaming está muito lento (> 100ms por caractere), registra warning
                const startTime = performance.now();
                await new Promise(resolve => setTimeout(resolve, streamingSpeed));
                const endTime = performance.now();
                const actualDelay = endTime - startTime;
                
                if (actualDelay > streamingSpeed * 2) {
                    console.warn(`[STREAMING] Delay alto: ${actualDelay.toFixed(2)}ms (esperado: ${streamingSpeed}ms)`);
                    errorCount++;
                }
            }
        }
    } catch (error) {
        console.error('[STREAMING] Erro durante typewriter:', error);
        // Fallback: mostra texto completo se streaming falhar
        element.textContent = text;
    }
}
```

#### **2. Detecção de Velocidade de Conexão**

```javascript
// Em chat.js, detectar velocidade de conexão antes de streaming
function detectConnectionSpeed() {
    if (!navigator.connection) {
        return 'unknown';
    }
    
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const effectiveType = connection.effectiveType; // '2g', '3g', '4g'
    const downlink = connection.downlink; // Mbps
    
    return {
        effectiveType,
        downlink,
        rtt: connection.rtt // Round-trip time em ms
    };
}

// Ajusta velocidade de streaming baseado em conexão
function getAdaptiveStreamingSpeed() {
    const connection = detectConnectionSpeed();
    
    if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') {
        return 0; // Sem streaming, mostra texto completo
    } else if (connection.effectiveType === '3g' || connection.downlink < 1.5) {
        return 30; // Streaming mais lento para 3G
    } else if (connection.effectiveType === '4g' && connection.downlink >= 1.5) {
        return 15; // Streaming rápido para 4G
    }
    
    return 15; // Padrão mobile
}
```

#### **3. Métricas a Monitorar:**

- **Taxa de erros de streaming:** Número de falhas durante typewriter
- **Delay real vs esperado:** Diferença entre delay real e delay esperado
- **Tempo total de streaming:** Tempo necessário para exibir resposta completa
- **Perda de caracteres:** Se algum caractere foi perdido durante streaming

#### **4. Logging Estruturado:**

```javascript
// Em logs/streaming-metrics.log (futuro)
{
    "timestamp": "2025-01-27T17:00:00Z",
    "device": "mobile",
    "connection": {
        "effectiveType": "3g",
        "downlink": 1.2,
        "rtt": 150
    },
    "streaming": {
        "speed": 30,
        "textLength": 150,
        "duration": 4500,
        "errors": 0,
        "avgDelay": 28.5
    }
}
```

---

## 🧹 CANCELAMENTO DE REQUISIÇÃO E LIBERAÇÃO DE MEMÓRIA

### **Análise da Implementação Atual:**

O `APIClient` já implementa cancelamento de requisições:

```javascript
// api-client.js
async request(endpoint, options = {}) {
    const { cancelPrevious = true } = options;
    
    // Cancela requisição anterior ao mesmo endpoint
    if (cancelPrevious && this.activeRequests.has(endpoint)) {
        const previousController = this.activeRequests.get(endpoint);
        previousController.abort(); // ✅ Cancela requisição
        this.activeRequests.delete(endpoint); // ✅ Remove do Map
    }
    
    // Cria novo AbortController
    const controller = new AbortController();
    this.activeRequests.set(endpoint, controller);
    
    // ...
}
```

### **Verificação de Liberação de Memória:**

#### **1. Verificar se AbortController realmente cancela:**

```javascript
// Teste: Verificar se requisição cancelada libera memória
const controller = new AbortController();
const signal = controller.signal;

const promise = fetch('/api/chat', { signal });

// Cancela após 1 segundo
setTimeout(() => {
    controller.abort();
    console.log('Requisição cancelada:', signal.aborted); // Deve ser true
}, 1000);

promise
    .then(() => console.log('Requisição completada'))
    .catch(err => {
        if (err.name === 'AbortError') {
            console.log('✅ Requisição cancelada corretamente');
        } else {
            console.error('Erro:', err);
        }
    });
```

#### **2. Monitorar uso de memória no Mobile:**

```javascript
// Em chat.js, monitorar uso de memória
function monitorMemoryUsage() {
    if (performance.memory) {
        const memory = {
            used: (performance.memory.usedJSHeapSize / 1048576).toFixed(2), // MB
            total: (performance.memory.totalJSHeapSize / 1048576).toFixed(2), // MB
            limit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2) // MB
        };
        
        console.log('[MEMORY]', memory);
        
        // Se uso de memória > 80% do limite, limpa cache
        if (memory.used / memory.limit > 0.8) {
            console.warn('[MEMORY] Uso de memória alto, limpando cache...');
            // Limpa histórico antigo do localStorage
            clearOldCache();
        }
    }
}

// Limpa cache antigo
function clearOldCache() {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
        if (key.startsWith('sophia_') && key.includes('history')) {
            const data = JSON.parse(localStorage.getItem(key));
            const age = Date.now() - new Date(data.last_updated).getTime();
            if (age > 24 * 60 * 60 * 1000) { // 24 horas
                localStorage.removeItem(key);
            }
        }
    });
}
```

#### **3. Garantir limpeza ao trocar de aba:**

```javascript
// Em mobile-navigation.js, garantir limpeza ao trocar de aba
switchSection(sectionName) {
    // Se estava em Chat e está mudando, cancela requisições ativas
    if (this.currentSection === 'chat' && sectionName !== 'chat') {
        if (window.apiClient && typeof window.apiClient.cancelAll === 'function') {
            window.apiClient.cancelAll(); // Cancela todas as requisições ativas
        }
    }
    
    this.currentSection = sectionName;
    this.hideAllSections();
    this.showSection(sectionName);
    this.updateNavButtons(sectionName);
}
```

#### **4. Adicionar método cancelAll ao APIClient:**

```javascript
// Em api-client.js
cancelAll() {
    this.activeRequests.forEach((controller, endpoint) => {
        this.log(`🛑 Cancelando requisição para ${endpoint}`);
        controller.abort();
    });
    this.activeRequests.clear();
    this.log('✅ Todas as requisições canceladas');
}
```

---

## 🍞 SISTEMA DE TOAST NOTIFICATION PARA ERROS

### **Design:**

#### **1. Posicionamento:**
- **Desktop:** Canto superior direito (top: 1rem, right: 1rem)
- **Mobile:** Canto superior direito, abaixo do header (top: 64px, right: 0.5rem)

#### **2. Tipos de Toast:**

- **Success (✅):** Verde - Operação bem-sucedida
- **Error (❌):** Vermelho - Erros críticos (ex: vídeo não carrega)
- **Warning (⚠️):** Laranja - Avisos (ex: conexão lenta)
- **Info (ℹ️):** Azul - Informações gerais

#### **3. Implementação:**

✅ **Arquivo criado:** `backend/static/js/toast-notification.js`

**Características:**
- Auto-dismiss após 4 segundos (configurável)
- Botão de fechar manual
- Stacking (múltiplos toasts empilhados)
- Animação suave de entrada/saída
- Responsivo para mobile

#### **4. Uso em Erros de Vídeo:**

```javascript
// Em sidebar-content.js
function openVideoModal(video) {
    // ...
    
    // Se vídeo não carrega, mostra toast de erro
    iframe.addEventListener('error', () => {
        if (window.toast && typeof window.toast.error === 'function') {
            window.toast.error(
                'Erro ao carregar vídeo. Verifique sua conexão ou tente novamente.',
                5000 // 5 segundos
            );
        }
    });
    
    // Timeout: se vídeo demora muito, mostra aviso
    const loadTimeout = setTimeout(() => {
        if (iframe.contentDocument === null) {
            window.toast.warning(
                'Vídeo demorando para carregar. Verifique sua conexão.',
                4000
            );
        }
    }, 10000); // 10 segundos
}
```

#### **5. Casos de Uso:**

- ✅ **Erro ao carregar vídeo:** `toast.error('Erro ao carregar vídeo...')`
- ✅ **Conexão lenta detectada:** `toast.warning('Conexão lenta detectada...')`
- ✅ **Requisição cancelada:** `toast.info('Requisição cancelada')`
- ✅ **Vídeo pausado (economia de dados):** `toast.info('Vídeo pausado para economizar dados')`

---

## 📊 DASHBOARD DE MONITORAMENTO (Futuro)

### **Métricas a Coletar:**

1. **Performance:**
   - Tempo médio de resposta (ms)
   - Taxa de sucesso de requisições (%)
   - Tempo de streaming (ms)

2. **Rede:**
   - Tipo de conexão (2G, 3G, 4G, 5G)
   - Velocidade média (Mbps)
   - Taxa de erros (%)

3. **UX:**
   - Tarefas completadas (%)
   - Tempo médio por tarefa (s)
   - Taxa de abandono (%)

4. **Erros:**
   - Erros de vídeo (%)
   - Falhas de streaming (%)
   - Requisições canceladas (%)

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### **Monitoramento de Streaming:**
- [x] Sistema de logging de erros implementado
- [ ] Detecção de velocidade de conexão
- [ ] Ajuste adaptativo de velocidade de streaming
- [ ] Métricas salvadas em log estruturado

### **Cancelamento de Requisição:**
- [x] APIClient já implementa cancelamento
- [ ] Método `cancelAll()` adicionado
- [ ] Limpeza ao trocar de aba implementada
- [ ] Monitoramento de uso de memória

### **Toast Notification:**
- [x] Sistema de toast criado
- [x] Integrado com erros de vídeo
- [ ] Testes em dispositivos reais
- [ ] Feedback de usuários sobre avisos

---

## 📝 PRÓXIMOS PASSOS

1. **Implementar** detecção de velocidade de conexão
2. **Adicionar** método `cancelAll()` ao APIClient
3. **Testar** liberação de memória em dispositivos reais
4. **Coletar** métricas de performance durante testes
5. **Iterar** com base em resultados

---

**Versão:** 1.0  
**Status:** ✅ Aprovado  
**Próxima Revisão:** Após implementação
