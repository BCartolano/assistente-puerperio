class ChatbotPuerperio {
    constructor() {
        this.userId = this.generateUserId();
        this.isTyping = false;
        this.categories = [];
        this.deviceType = this.detectDevice();
        
        this.initializeElements();
        this.bindEvents();
        this.loadCategories();
        this.loadChatHistory();
        this.requestNotificationPermission();
        this.optimizeForDevice();
    }
    
    generateUserId() {
        return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.welcomeMessage = document.getElementById('welcome-message');
        this.sidebar = document.getElementById('sidebar');
        this.menuToggle = document.getElementById('menu-toggle');
        this.closeSidebar = document.getElementById('close-sidebar');
        this.clearHistoryBtn = document.getElementById('clear-history');
        this.categoriesContainer = document.getElementById('categories');
        this.charCount = document.getElementById('char-count');
        this.alertModal = document.getElementById('alert-modal');
        this.closeAlert = document.getElementById('close-alert');
        this.emergencyCall = document.getElementById('emergency-call');
        this.findDoctor = document.getElementById('find-doctor');
        this.alertMessage = document.getElementById('alert-message');
        this.statusIndicator = document.getElementById('status-indicator');
        this.backToWelcome = document.getElementById('back-to-welcome');
        this.backBtn = document.getElementById('back-btn');
        
        // Auth elements
        this.authModal = document.getElementById('auth-modal');
        this.closeAuth = document.getElementById('close-auth');
        this.accountBtn = document.getElementById('account-btn');
        this.authTabs = document.querySelectorAll('.auth-tab');
        this.loginForm = document.getElementById('login-form');
        this.registerForm = document.getElementById('register-form');
        this.showLogin = document.getElementById('show-login');
        this.showRegister = document.getElementById('show-register');
        this.btnLogin = document.getElementById('btn-login');
        this.btnRegister = document.getElementById('btn-register');
    }
    
    bindEvents() {
        // Envio de mensagem
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Contador de caracteres
        this.messageInput.addEventListener('input', () => this.updateCharCount());
        
        // Menu sidebar
        this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        this.closeSidebar.addEventListener('click', () => this.closeSidebarMenu());
        
        // Limpar histórico
        this.clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        
        // Voltar ao início
        this.backBtn.addEventListener('click', () => this.backToWelcomeScreen());
        
        // Quick questions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-btn')) {
                const question = e.target.dataset.question;
                this.messageInput.value = question;
                this.sendMessage();
            }
        });
        
        // Modal de alerta
        this.closeAlert.addEventListener('click', () => this.hideAlert());
        this.emergencyCall.addEventListener('click', () => this.callEmergency());
        this.findDoctor.addEventListener('click', () => this.findDoctorNearby());
        
        // Fechar modal clicando fora
        this.alertModal.addEventListener('click', (e) => {
            if (e.target === this.alertModal) {
                this.hideAlert();
            }
        });
        
        // Fechar sidebar clicando fora
        document.addEventListener('click', (e) => {
            if (this.sidebar.classList.contains('open') && 
                !this.sidebar.contains(e.target) && 
                !this.menuToggle.contains(e.target)) {
                this.closeSidebarMenu();
            }
        });
        
        // Auth modal events
        this.accountBtn?.addEventListener('click', () => this.showAuthModal());
        this.closeAuth?.addEventListener('click', () => this.hideAuthModal());
        
        // Auth tabs
        this.authTabs.forEach(tab => {
            tab.addEventListener('click', () => this.switchAuthTab(tab.dataset.tab));
        });
        
        // Show login/register links
        this.showLogin?.addEventListener('click', (e) => {
            e.preventDefault();
            this.switchAuthTab('login');
        });
        this.showRegister?.addEventListener('click', (e) => {
            e.preventDefault();
            this.switchAuthTab('register');
        });
        
        // Submit buttons
        this.btnLogin?.addEventListener('click', () => this.handleLogin());
        this.btnRegister?.addEventListener('click', () => this.handleRegister());
        
        // Fechar auth modal clicando fora
        this.authModal?.addEventListener('click', (e) => {
            if (e.target === this.authModal) {
                this.hideAuthModal();
            }
        });
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = `${count}/500`;
        
        if (count > 450) {
            this.charCount.style.color = '#e74c3c';
        } else if (count > 400) {
            this.charCount.style.color = '#f39c12';
        } else {
            this.charCount.style.color = '#6c757d';
        }
    }
    
    async loadCategories() {
        try {
            const response = await fetch('/api/categorias');
            const categories = await response.json();
            this.categories = categories;
            this.renderCategories();
        } catch (error) {
            console.error('Erro ao carregar categorias:', error);
            this.categoriesContainer.innerHTML = `
                <div class="category-item">
                    <i class="fas fa-exclamation-triangle"></i>
                    Erro ao carregar categorias
                </div>
            `;
        }
    }
    
    renderCategories() {
        this.categoriesContainer.innerHTML = '';
        
        if (this.categories.length === 0) {
            this.categoriesContainer.innerHTML = `
                <div class="category-item">
                    <i class="fas fa-info-circle"></i>
                    Nenhuma categoria disponível
                </div>
            `;
            return;
        }
        
        this.categories.forEach(category => {
            const categoryElement = document.createElement('div');
            categoryElement.className = 'category-item';
            categoryElement.innerHTML = `
                <i class="fas fa-folder"></i>
                ${this.formatCategoryName(category)}
            `;
            
            categoryElement.addEventListener('click', () => {
                this.messageInput.value = `Fale sobre ${category}`;
                this.messageInput.focus();
                this.closeSidebarMenu();
            });
            
            this.categoriesContainer.appendChild(categoryElement);
        });
    }
    
    formatCategoryName(category) {
        return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Adiciona mensagem do usuário
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.updateCharCount();
        
        // Esconde welcome message e mostra chat
        this.welcomeMessage.style.display = 'none';
        this.chatMessages.classList.add('active');
        this.backToWelcome.style.display = 'block';
        
        // Mostra indicador de digitação
        this.showTyping();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pergunta: message,
                    user_id: this.userId
                })
            });
            
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }
            
            const data = await response.json();
            
            // Esconde indicador de digitação
            this.hideTyping();
            
            // Adiciona resposta do assistente
            this.addMessage(data.resposta, 'assistant', {
                categoria: data.categoria,
                alertas: data.alertas,
                fonte: data.fonte
            });
            
            // Mostra alerta se necessário
            if (data.alertas && data.alertas.length > 0) {
                this.showAlert(data.alertas);
            }
            
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.hideTyping();
            this.addMessage(
                'Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente em alguns instantes.',
                'assistant'
            );
        }
    }
    
    addMessage(content, sender, metadata = {}) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        
        const avatar = sender === 'user' ? '👩' : '🤱';
        const time = new Date().toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        // Adiciona som de notificação (se suportado)
        if (sender === 'assistant' && 'Notification' in window && Notification.permission === 'granted') {
            new Notification('Assistente Puerpério', {
                body: 'Nova mensagem recebida',
                icon: '/favicon.ico'
            });
        }
        
        let categoryBadge = '';
        if (metadata.categoria) {
            categoryBadge = `
                <div class="message-category">
                    📁 ${this.formatCategoryName(metadata.categoria)}
                </div>
            `;
        }
        
        let alertSection = '';
        if (metadata.alertas && metadata.alertas.length > 0) {
            alertSection = `
                <div class="message-alert">
                    ⚠️ <strong>Alerta:</strong> Detectamos palavras relacionadas a: ${metadata.alertas.join(', ')}
                </div>
            `;
        }
        
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
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Converte quebras de linha em HTML
        return content.replace(/\n/g, '<br>');
    }
    
    showTyping() {
        this.isTyping = true;
        this.typingIndicator.classList.add('show');
        this.scrollToBottom();
    }
    
    hideTyping() {
        this.isTyping = false;
        this.typingIndicator.classList.remove('show');
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    toggleSidebar() {
        this.sidebar.classList.toggle('open');
    }
    
    closeSidebarMenu() {
        this.sidebar.classList.remove('open');
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch(`/api/historico/${this.userId}`);
            const history = await response.json();
            
            if (history.length > 0) {
                this.welcomeMessage.style.display = 'none';
                this.chatMessages.classList.add('active');
                
                history.forEach(item => {
                    this.addMessage(item.pergunta, 'user');
                    this.addMessage(item.resposta, 'assistant', {
                        categoria: item.categoria,
                        alertas: item.alertas
                    });
                });
            }
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    }
    
    async clearHistory() {
        if (confirm('Tem certeza que deseja limpar todo o histórico de conversas?')) {
            try {
                // Aqui você implementaria a chamada para limpar o histórico no backend
                // Por enquanto, apenas limpa o frontend
                this.chatMessages.innerHTML = '';
                this.welcomeMessage.style.display = 'flex';
                this.chatMessages.classList.remove('active');
                
                // Gera novo ID de usuário
                this.userId = this.generateUserId();
                
                alert('Histórico limpo com sucesso!');
            } catch (error) {
                console.error('Erro ao limpar histórico:', error);
                alert('Erro ao limpar histórico. Tente novamente.');
            }
        }
    }
    
    showAlert(alertas) {
        this.alertMessage.textContent = 
            `Detectamos palavras relacionadas a: ${alertas.join(', ')}. ` +
            'Se você está enfrentando algum problema de saúde, procure atendimento médico.';
        this.alertModal.classList.add('show');
    }
    
    hideAlert() {
        this.alertModal.classList.remove('show');
    }
    
    callEmergency() {
        // Número de emergência do Brasil
        window.open('tel:192', '_self');
    }
    
    findDoctorNearby() {
        // Abre Google Maps para encontrar médicos próximos
        window.open('https://www.google.com/maps/search/médico+próximo', '_blank');
    }
    
    // Verifica status da conexão
    checkConnectionStatus() {
        if (navigator.onLine) {
            this.statusIndicator.className = 'status-online';
            this.statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Online';
        } else {
            this.statusIndicator.className = 'status-offline';
            this.statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Offline';
        }
    }
    
    backToWelcomeScreen() {
        // Limpa as mensagens do chat
        this.chatMessages.innerHTML = '';
        this.chatMessages.classList.remove('active');
        
        // Mostra a tela de boas-vindas
        this.welcomeMessage.style.display = 'flex';
        this.backToWelcome.style.display = 'none';
        
        // Foca no input
        this.messageInput.focus();
        
        // Gera novo ID de usuário para nova sessão
        this.userId = this.generateUserId();
    }
    
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('Permissão para notificações concedida');
                }
            });
        }
    }
    
    detectDevice() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        if (width <= 479) return 'mobile-portrait';
        if (width <= 575) return 'mobile-landscape';
        if (width <= 767) return 'tablet-portrait';
        if (width <= 991) return 'tablet-landscape';
        if (width <= 1199) return 'desktop-small';
        return 'desktop-large';
    }
    
    optimizeForDevice() {
        const deviceType = this.deviceType;
        
        // Adiciona classe CSS baseada no dispositivo
        document.body.classList.add(`device-${deviceType}`);
        
        // Otimizações específicas por dispositivo
        switch(deviceType) {
            case 'mobile-portrait':
                this.optimizeMobilePortrait();
                break;
            case 'mobile-landscape':
                this.optimizeMobileLandscape();
                break;
            case 'tablet-portrait':
                this.optimizeTabletPortrait();
                break;
            case 'tablet-landscape':
                this.optimizeTabletLandscape();
                break;
            default:
                this.optimizeDesktop();
        }
        
        // Adiciona listener para mudanças de orientação
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.deviceType = this.detectDevice();
                document.body.className = document.body.className.replace(/device-\w+/g, '');
                document.body.classList.add(`device-${this.deviceType}`);
                this.optimizeForDevice();
            }, 100);
        });
        
        // Adiciona listener para redimensionamento
        window.addEventListener('resize', () => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                const newDeviceType = this.detectDevice();
                if (newDeviceType !== this.deviceType) {
                    this.deviceType = newDeviceType;
                    document.body.className = document.body.className.replace(/device-\w+/g, '');
                    document.body.classList.add(`device-${this.deviceType}`);
                    this.optimizeForDevice();
                }
            }, 250);
        });
    }
    
    optimizeMobilePortrait() {
        // Fecha sidebar automaticamente em mobile
        this.closeSidebarMenu();
        
        // Ajusta tamanho do input para touch
        if (this.messageInput) {
            this.messageInput.style.fontSize = '16px'; // Previne zoom no iOS
        }
        
        // Otimiza scroll suave
        this.chatMessages.style.scrollBehavior = 'smooth';
    }
    
    optimizeMobileLandscape() {
        // Ajustes para landscape em mobile
        this.closeSidebarMenu();
    }
    
    optimizeTabletPortrait() {
        // Otimizações para tablet em portrait
        this.chatMessages.style.scrollBehavior = 'smooth';
    }
    
    optimizeTabletLandscape() {
        // Otimizações para tablet em landscape
        // Pode mostrar sidebar se necessário
    }
    
    optimizeDesktop() {
        // Otimizações para desktop
        this.chatMessages.style.scrollBehavior = 'auto';
    }
    
    // Auth functions
    showAuthModal() {
        this.authModal.classList.add('show');
        this.switchAuthTab('login');
    }
    
    hideAuthModal() {
        this.authModal.classList.remove('show');
        if (this.loginForm) {
            document.getElementById('login-email').value = '';
            document.getElementById('login-password').value = '';
        }
        if (this.registerForm) {
            document.getElementById('register-name').value = '';
            document.getElementById('register-email').value = '';
            document.getElementById('register-password').value = '';
            document.getElementById('register-baby').value = '';
        }
    }
    
    switchAuthTab(tab) {
        this.authTabs.forEach(t => t.classList.remove('active'));
        this.loginForm?.classList.remove('active');
        this.registerForm?.classList.remove('active');
        
        if (tab === 'login') {
            document.querySelector('[data-tab="login"]')?.classList.add('active');
            this.loginForm?.classList.add('active');
        } else if (tab === 'register') {
            document.querySelector('[data-tab="register"]')?.classList.add('active');
            this.registerForm?.classList.add('active');
        }
    }
    
    async handleLogin() {
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        
        if (!email || !password) {
            alert('Por favor, preencha todos os campos! 💕');
            return;
        }
        
        alert('Login funcionará em breve! Backend em desenvolvimento...');
        this.hideAuthModal();
    }
    
    async handleRegister() {
        const name = document.getElementById('register-name').value.trim();
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value;
        const babyName = document.getElementById('register-baby').value.trim();
        
        if (!name || !email || !password) {
            alert('Por favor, preencha os campos obrigatórios (Nome, Email e Senha)! 💕');
            return;
        }
        
        if (password.length < 6) {
            alert('A senha deve ter no mínimo 6 caracteres! 💕');
            return;
        }
        
        alert('Cadastro funcionará em breve! Backend em desenvolvimento...');
        this.hideAuthModal();
    }
}

// Inicializa o chatbot quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    const chatbot = new ChatbotPuerperio();
    
    // Verifica status da conexão periodicamente
    setInterval(() => chatbot.checkConnectionStatus(), 5000);
    chatbot.checkConnectionStatus();
    
    // Adiciona evento de online/offline
    window.addEventListener('online', () => chatbot.checkConnectionStatus());
    window.addEventListener('offline', () => chatbot.checkConnectionStatus());
    
    // Foca no input quando a página carrega
    document.getElementById('message-input').focus();
});

