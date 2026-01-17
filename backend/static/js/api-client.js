/**
 * APIClient - Cliente HTTP resiliente para requisições ao backend
 * 
 * Funcionalidades:
 * - Timeout automático (30 segundos padrão)
 * - Retry logic para erros 5xx e timeouts
 * - Request cancellation (cancela requisição anterior se nova for disparada)
 * - Suporte a credentials e headers personalizados
 * 
 * @version 1.0.0
 * @date 2025-01-08
 */

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.defaultTimeout = 30000; // 30 segundos
        this.maxRetries = 3;
        this.activeRequests = new Map(); // Mapa de requisições ativas por endpoint
        
        // Debug mode (mesmo padrão do chat.js)
        this.isDevelopment = window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1' ||
                           window.location.hostname.includes('.local') ||
                           window.DEBUG_MODE === true;
        
        this.log = (...args) => {
            if (this.isDevelopment) {
                console.log('[APIClient]', ...args);
            }
        };
        
        this.warn = (...args) => {
            if (this.isDevelopment) {
                console.warn('[APIClient]', ...args);
            }
        };
        
        this.error = (...args) => {
            if (this.isDevelopment) {
                console.error('[APIClient]', ...args);
            }
        };
    }
    
    /**
     * Cancela todas as requisições ativas
     * Útil para limpar requisições ao trocar de aba ou sair da página
     */
    cancelAll() {
        this.activeRequests.forEach((controller, endpoint) => {
            this.log(`🛑 Cancelando requisição para ${endpoint}`);
            controller.abort();
        });
        this.activeRequests.clear();
        this.log('✅ Todas as requisições canceladas');
    }
    
    /**
     * Faz uma requisição HTTP com todas as otimizações de resiliência
     * 
     * @param {string} endpoint - Endpoint da API (ex: '/api/chat')
     * @param {Object} options - Opções da requisição
     * @param {string} options.method - Método HTTP (GET, POST, etc.)
     * @param {Object} options.body - Corpo da requisição (será serializado como JSON)
     * @param {number} options.timeout - Timeout em ms (padrão: 30000)
     * @param {number} options.retries - Número de tentativas (padrão: 3)
     * @param {AbortSignal} options.signal - Sinal externo de cancelamento (opcional)
     * @param {string} options.priority - Prioridade da requisição (high, low, auto)
     * @param {Object} options.headers - Headers adicionais
     * @param {boolean} options.cancelPrevious - Se true, cancela requisições anteriores ao mesmo endpoint
     * @returns {Promise<Object>} Resposta parseada como JSON
     */
    async request(endpoint, options = {}) {
        const {
            method = 'GET',
            body,
            timeout = this.defaultTimeout,
            retries = this.maxRetries,
            signal: externalSignal,
            priority = 'auto',
            headers: customHeaders = {},
            cancelPrevious = true, // Por padrão, cancela requisições anteriores
            ...restOptions
        } = options;
        
        // Cancela requisição anterior ao mesmo endpoint se solicitado
        if (cancelPrevious && this.activeRequests.has(endpoint)) {
            const previousController = this.activeRequests.get(endpoint);
            this.log(`🛑 Cancelando requisição anterior para ${endpoint}`);
            previousController.abort();
            this.activeRequests.delete(endpoint);
        }
        
        // Cria AbortController para timeout e controle de cancelamento
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            this.log(`⏱️ Timeout atingido para ${endpoint} (${timeout}ms)`);
            controller.abort();
        }, timeout);
        
        // Armazena o controller para possível cancelamento futuro
        if (cancelPrevious) {
            this.activeRequests.set(endpoint, controller);
        }
        
        // Combina sinais se houver um externo
        const signal = externalSignal 
            ? this.combineSignals([controller.signal, externalSignal])
            : controller.signal;
        
        // Preparar headers
        const headers = {
            'Content-Type': 'application/json',
            ...customHeaders
        };
        
        // Preparar opções do fetch
        const fetchOptions = {
            method,
            headers,
            credentials: 'include', // Sempre inclui cookies
            signal,
            ...restOptions
        };
        
        // Adiciona body se fornecido
        if (body !== undefined) {
            fetchOptions.body = JSON.stringify(body);
        }
        
        // Adiciona priority se suportado (navegadores modernos)
        if (priority !== 'auto' && 'priority' in Request.prototype) {
            fetchOptions.priority = priority;
        }
        
        // Retry logic com backoff exponencial
        let lastError;
        let lastResponse;
        
        for (let attempt = 1; attempt <= retries; attempt++) {
            try {
                this.log(`📤 [Tentativa ${attempt}/${retries}] ${method} ${endpoint}`);
                
                const response = await fetch(`${this.baseURL}${endpoint}`, fetchOptions);
                
                clearTimeout(timeoutId);
                
                // Remove da lista de requisições ativas se for cancelada anteriormente
                if (cancelPrevious && this.activeRequests.has(endpoint)) {
                    this.activeRequests.delete(endpoint);
                }
                
                // Verifica se a requisição foi cancelada
                if (signal.aborted) {
                    throw new Error('Requisição cancelada');
                }
                
                // Para erros 4xx (client error), não retenta (exceto 408 - Request Timeout)
                if (!response.ok && response.status >= 400 && response.status < 500 && response.status !== 408) {
                    const errorText = await response.text().catch(() => 'Erro desconhecido');
                    throw new Error(`HTTP ${response.status}: ${errorText}`);
                }
                
                // Para erros 5xx (server error) ou timeout (408), retenta
                if (!response.ok && (response.status >= 500 || response.status === 408)) {
                    lastResponse = response;
                    
                    if (attempt < retries) {
                        const delay = this.getBackoffDelay(attempt);
                        this.warn(`⚠️ Erro ${response.status} na tentativa ${attempt}. Retentando em ${delay}ms...`);
                        await this.delay(delay);
                        
                        // Cria novo controller para nova tentativa (timeout resetado)
                        const newController = new AbortController();
                        const newTimeoutId = setTimeout(() => {
                            this.log(`⏱️ Timeout na tentativa ${attempt + 1} para ${endpoint}`);
                            newController.abort();
                        }, timeout);
                        
                        // Atualiza signal
                        if (externalSignal) {
                            fetchOptions.signal = this.combineSignals([newController.signal, externalSignal]);
                        } else {
                            fetchOptions.signal = newController.signal;
                        }
                        
                        // Atualiza controller ativo
                        if (cancelPrevious) {
                            this.activeRequests.set(endpoint, newController);
                        }
                        
                        clearTimeout(newTimeoutId);
                        continue;
                    } else {
                        const errorText = await response.text().catch(() => 'Erro desconhecido');
                        throw new Error(`HTTP ${response.status} após ${retries} tentativas: ${errorText}`);
                    }
                }
                
                // Sucesso - parseia JSON
                const data = await response.json();
                this.log(`✅ Sucesso em ${endpoint} (tentativa ${attempt}/${retries})`);
                
                return data;
                
            } catch (error) {
                clearTimeout(timeoutId);
                
                // Remove da lista de requisições ativas
                if (cancelPrevious && this.activeRequests.has(endpoint)) {
                    this.activeRequests.delete(endpoint);
                }
                
                // Se foi cancelado, não retenta
                if (error.name === 'AbortError' || error.message === 'Requisição cancelada') {
                    if (attempt === 1) {
                        // Se foi cancelado na primeira tentativa, é cancelamento manual
                        throw error;
                    }
                    // Se foi cancelado em tentativa subsequente, foi timeout - retenta
                    lastError = error;
                    if (attempt < retries) {
                        const delay = this.getBackoffDelay(attempt);
                        this.warn(`⏱️ Timeout na tentativa ${attempt}. Retentando em ${delay}ms...`);
                        await this.delay(delay);
                        continue;
                    }
                    throw new Error(`Timeout após ${retries} tentativas`);
                }
                
                // Para outros erros de rede, retenta
                if (error.name === 'TypeError' && error.message.includes('fetch')) {
                    lastError = error;
                    if (attempt < retries) {
                        const delay = this.getBackoffDelay(attempt);
                        this.warn(`🌐 Erro de rede na tentativa ${attempt}. Retentando em ${delay}ms...`);
                        await this.delay(delay);
                        continue;
                    }
                    throw new Error(`Erro de rede após ${retries} tentativas: ${error.message}`);
                }
                
                // Para outros erros, não retenta
                throw error;
            }
        }
        
        // Se chegou aqui, todas as tentativas falharam
        throw lastError || new Error(`Falha após ${retries} tentativas`);
    }
    
    /**
     * Calcula delay de backoff exponencial
     * @param {number} attempt - Número da tentativa (1-indexed)
     * @returns {number} Delay em milissegundos
     */
    getBackoffDelay(attempt) {
        // Backoff exponencial: 1s, 2s, 4s...
        return Math.min(1000 * Math.pow(2, attempt - 1), 10000); // Máximo 10s
    }
    
    /**
     * Delay/pausa assíncrona
     * @param {number} ms - Milissegundos para aguardar
     * @returns {Promise<void>}
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Combina múltiplos AbortSignals em um único signal
     * @param {AbortSignal[]} signals - Array de signals para combinar
     * @returns {AbortSignal} Signal combinado
     */
    combineSignals(signals) {
        const controller = new AbortController();
        
        signals.forEach(signal => {
            if (signal) {
                // Se já foi abortado, aborta imediatamente
                if (signal.aborted) {
                    controller.abort();
                    return;
                }
                
                // Adiciona listener para abortar quando qualquer signal for abortado
                signal.addEventListener('abort', () => {
                    controller.abort();
                });
            }
        });
        
        return controller.signal;
    }
    
    /**
     * Cancela todas as requisições ativas
     */
    cancelAll() {
        this.log(`🛑 Cancelando ${this.activeRequests.size} requisição(ões) ativa(s)`);
        this.activeRequests.forEach((controller, endpoint) => {
            controller.abort();
            this.log(`   - Cancelada: ${endpoint}`);
        });
        this.activeRequests.clear();
    }
    
    /**
     * Cancela requisições ativas para um endpoint específico
     * @param {string} endpoint - Endpoint a cancelar
     */
    cancel(endpoint) {
        if (this.activeRequests.has(endpoint)) {
            this.log(`🛑 Cancelando requisição para ${endpoint}`);
            this.activeRequests.get(endpoint).abort();
            this.activeRequests.delete(endpoint);
        }
    }
    
    /**
     * Métodos de conveniência para métodos HTTP comuns
     */
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }
    
    async post(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'POST', body });
    }
    
    async put(endpoint, body, options = {}) {
        return this.request(endpoint, { ...options, method: 'PUT', body });
    }
    
    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
}

// Exportar singleton global
if (typeof window !== 'undefined') {
    window.apiClient = new APIClient();
    
    // Expor para debug (apenas em desenvolvimento)
    if (window.apiClient.isDevelopment) {
        window.APIClient = APIClient; // Classe também disponível se precisar criar instâncias
        console.log('[APIClient] ✅ Cliente API inicializado e disponível em window.apiClient');
    }
}
