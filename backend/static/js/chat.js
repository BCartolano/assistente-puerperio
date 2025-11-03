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
        
        // Sidebar new buttons
        this.sidebarBtnGuias = document.getElementById('sidebar-btn-guias');
        this.sidebarBtnGestacao = document.getElementById('sidebar-btn-gestacao');
        this.sidebarBtnPosparto = document.getElementById('sidebar-btn-posparto');
        this.sidebarBtnVacinas = document.getElementById('sidebar-btn-vacinas');
        this.sidebarBtnClear = document.getElementById('sidebar-btn-clear');
        this.sidebarBtnBack = document.getElementById('sidebar-btn-back');
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
        
        // Resources elements
        this.resourcesModal = document.getElementById('resources-modal');
        this.closeResources = document.getElementById('close-resources');
        this.resourcesTitle = document.getElementById('resources-title');
        this.resourcesContent = document.getElementById('resources-content');
        this.btnGuias = document.getElementById('btn-guias');
        this.btnGestacao = document.getElementById('btn-gestacao');
        this.btnPosparto = document.getElementById('btn-posparto');
        this.btnVacinas = document.getElementById('btn-vacinas');
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
        this.clearHistoryBtn?.addEventListener('click', () => this.clearHistory());
        
        // Voltar ao início
        this.backBtn.addEventListener('click', () => this.backToWelcomeScreen());
        
        // Sidebar buttons
        this.sidebarBtnGuias?.addEventListener('click', () => {
            this.closeSidebarMenu();
            this.showGuias();
        });
        this.sidebarBtnGestacao?.addEventListener('click', () => {
            this.closeSidebarMenu();
            this.showGestacao();
        });
        this.sidebarBtnPosparto?.addEventListener('click', () => {
            this.closeSidebarMenu();
            this.showPosparto();
        });
        this.sidebarBtnVacinas?.addEventListener('click', () => {
            this.closeSidebarMenu();
            this.showVacinas();
        });
        this.sidebarBtnClear?.addEventListener('click', () => {
            this.closeSidebarMenu();
            this.clearHistory();
        });
        this.sidebarBtnBack?.addEventListener('click', () => {
            this.closeSidebarMenu();
            this.backToWelcomeScreen();
        });
        
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
        
        // Resources buttons
        this.btnGuias?.addEventListener('click', () => this.showGuias());
        this.btnGestacao?.addEventListener('click', () => this.showGestacao());
        this.btnPosparto?.addEventListener('click', () => this.showPosparto());
        this.btnVacinas?.addEventListener('click', () => this.showVacinas());
        
        // Fechar resources modal
        this.closeResources?.addEventListener('click', () => this.hideResourcesModal());
        
        // Fechar resources modal clicando fora
        this.resourcesModal?.addEventListener('click', (e) => {
            if (e.target === this.resourcesModal) {
                this.hideResourcesModal();
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
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('🎉 ' + data.mensagem);
                this.hideAuthModal();
                window.location.reload();
            } else {
                alert('⚠️ ' + data.erro);
            }
        } catch (error) {
            alert('❌ Erro ao fazer login. Tente novamente.');
        }
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
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, email, password, baby_name: babyName})
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('🎉 ' + data.mensagem);
                this.hideAuthModal();
                // Auto switch para login
                setTimeout(() => {
                    this.showAuthModal();
                    this.switchAuthTab('login');
                }, 500);
            } else {
                alert('⚠️ ' + data.erro);
            }
        } catch (error) {
            alert('❌ Erro ao cadastrar. Tente novamente.');
        }
    }
    
    // Resources functions
    hideResourcesModal() {
        this.resourcesModal.classList.remove('show');
        this.resourcesContent.innerHTML = '';
    }
    
    async showGuias() {
        try {
            const response = await fetch('/api/guias');
            const guias = await response.json();
            
            this.resourcesTitle.textContent = '📚 Guias Práticos';
            let html = '<div class="guia-grid">';
            
            for (const [key, guia] of Object.entries(guias)) {
                html += `
                    <div class="guia-card" data-guia="${key}">
                        <div class="guia-card-title">${guia.titulo}</div>
                        <div class="guia-card-desc">${guia.descricao}</div>
                    </div>
                `;
            }
            
            html += '</div>';
            this.resourcesContent.innerHTML = html;
            this.resourcesModal.classList.add('show');
            
            // Add click listeners to guia cards
            document.querySelectorAll('.guia-card').forEach(card => {
                card.addEventListener('click', () => this.showGuiaDetalhes(card.dataset.guia, guias[card.dataset.guia]));
            });
        } catch (error) {
            alert('❌ Erro ao carregar guias');
        }
    }
    
    showGuiaDetalhes(key, guia) {
        this.resourcesTitle.textContent = guia.titulo;
        let html = `<p style="color: #666; margin-bottom: 1.5rem;">${guia.descricao}</p>`;
        
        if (guia.causas) {
            html += `<div class="alerta-importante"><strong>Causas:</strong> ${guia.causas}</div>`;
        }
        
        if (guia.importante) {
            html += `<div class="alerta-importante"><strong>⚠️ IMPORTANTE:</strong> ${guia.importante}</div>`;
        }
        
        guia.passos.forEach(passo => {
            html += `
                <div class="passo-card">
                    <span class="passo-numero">${passo.numero}</span>
                    <span class="passo-titulo">${passo.titulo}</span>
                    <p class="passo-descricao">${passo.descricao}</p>
                    ${passo.imagem ? `<img src="${passo.imagem}" alt="${passo.titulo}" class="passo-imagem">` : ''}
                    <div class="passo-dica">💡 ${passo.dica}</div>
                </div>
            `;
        });
        
        if (guia.depois) {
            html += `<div class="alerta-importante"><strong>Depois:</strong> ${guia.depois}</div>`;
        }
        
        if (guia.emergencia) {
            html += `<div class="alerta-importante" style="background: #fff3cd; border-color: #ffc107;">${guia.emergencia}</div>`;
        }
        
        if (guia.sinais_medico) {
            html += `<div class="alerta-importante"><strong>⚠️ Procure o médico se:</strong> ${guia.sinais_medico}</div>`;
        }
        
        if (guia.telefones_uteis) {
            html += `<div class="alerta-importante" style="background: #f8f9fa;">📞 ${guia.telefones_uteis}</div>`;
        }
        
        this.resourcesContent.innerHTML = html;
    }
    
    async showGestacao() {
        try {
            const response = await fetch('/api/cuidados/gestacao');
            const gestacao = await response.json();
            
            this.resourcesTitle.textContent = '🤰 Cuidados na Gestação';
            let html = '';
            
            for (const [key, trimestre] of Object.entries(gestacao)) {
                html += `
                    <div class="trimestre-card">
                        <h4>${trimestre.nome}</h4>
                        <p style="margin-bottom: 0.5rem; color: #666;"><strong>${trimestre.semanas}</strong> - ${trimestre.descricao}</p>
                        ${trimestre.cuidados ? trimestre.cuidados.map(cuidado => `
                            <div class="semana-item">✅ ${cuidado}</div>
                        `).join('') : ''}
                        ${trimestre.desenvolvimento_bebe ? `<div style="margin-top: 1rem; padding: 0.8rem; background: #e8f5e9; border-radius: 8px;"><strong>👶 Desenvolvimento do bebê:</strong><br>${trimestre.desenvolvimento_bebe}</div>` : ''}
                        ${trimestre.exames ? `<div style="margin-top: 1rem;"><strong>🔬 Exames recomendados:</strong><ul style="margin: 0.5rem 0; padding-left: 1.5rem;">${trimestre.exames.map(ex => `<li>${ex}</li>`).join('')}</ul></div>` : ''}
                        ${trimestre.alerta ? `<div class="alerta-importante"><strong>⚠️ Atenção:</strong> ${trimestre.alerta}</div>` : ''}
                    </div>
                `;
            }
            
            this.resourcesContent.innerHTML = html;
            this.resourcesModal.classList.add('show');
        } catch (error) {
            alert('❌ Erro ao carregar cuidados de gestação');
        }
    }
    
    async showPosparto() {
        try {
            const response = await fetch('/api/cuidados/puerperio');
            const posparto = await response.json();
            
            this.resourcesTitle.textContent = '👶 Cuidados Pós-Parto';
            let html = '';
            
            for (const [key, periodo] of Object.entries(posparto)) {
                html += `
                    <div class="periodo-card">
                        <h4>${periodo.nome}</h4>
                        <p style="margin-bottom: 0.5rem; color: #666;"><strong>${periodo.semanas}</strong> - ${periodo.descricao}</p>
                        ${periodo.cuidados_fisicos ? `
                            <div style="margin-bottom: 1rem;">
                                <strong>💪 Cuidados Físicos:</strong>
                                ${periodo.cuidados_fisicos.map(c => `<div class="semana-item">✅ ${c}</div>`).join('')}
                            </div>
                        ` : ''}
                        ${periodo.cuidados_emocionais ? `
                            <div style="margin-bottom: 1rem;">
                                <strong>💕 Cuidados Emocionais:</strong>
                                ${periodo.cuidados_emocionais.map(c => `<div class="semana-item">❤️ ${c}</div>`).join('')}
                            </div>
                        ` : ''}
                        ${periodo.amamentacao ? `
                            <div style="margin-bottom: 1rem;">
                                <strong>🍼 Amamentação:</strong>
                                ${periodo.amamentacao.map(c => `<div class="semana-item">🤱 ${c}</div>`).join('')}
                            </div>
                        ` : ''}
                        ${periodo.desenvolvimento_bebe ? `<div style="margin-top: 1rem; padding: 0.8rem; background: #e8f5e9; border-radius: 8px;"><strong>👶 Desenvolvimento do bebê:</strong><br>${periodo.desenvolvimento_bebe}</div>` : ''}
                        ${periodo.alertas ? `<div class="alerta-importante"><strong>⚠️ Atenção:</strong> ${periodo.alertas}</div>` : ''}
                        ${periodo.telefones_uteis ? `<div style="margin-top: 0.5rem; padding: 0.8rem; background: #f8f9fa; border-radius: 8px;">📞 ${periodo.telefones_uteis}</div>` : ''}
                    </div>
                `;
            }
            
            this.resourcesContent.innerHTML = html;
            this.resourcesModal.classList.add('show');
        } catch (error) {
            alert('❌ Erro ao carregar cuidados pós-parto');
        }
    }
    
    async showVacinas() {
        try {
            const [maeData, bebeData, vacinasStatus] = await Promise.all([
                fetch('/api/vacinas/mae').then(r => r.json()),
                fetch('/api/vacinas/bebe').then(r => r.json()),
                this.fetchVacinasStatus()
            ]);
            
            this.resourcesTitle.textContent = '💉 Carteira de Vacinação';
            
            // Criar tabs para Mãe e Bebê
            let html = `
                <div class="vacinas-tabs">
                    <button class="vacina-tab active" data-tab="mae">👩 Vacinas da Mamãe</button>
                    <button class="vacina-tab" data-tab="bebe">👶 Vacinas do Bebê</button>
                </div>
                <div class="vacinas-content">
                    <div class="vacina-tab-content active" id="vacinas-mae">
                        ${this.renderVacinasMae(maeData, vacinasStatus)}
                    </div>
                    <div class="vacina-tab-content" id="vacinas-bebe">
                        ${this.renderVacinasBebe(bebeData, vacinasStatus)}
                    </div>
                </div>
            `;
            
            this.resourcesContent.innerHTML = html;
            this.resourcesModal.classList.add('show');
            
            // Bind tabs
            document.querySelectorAll('.vacina-tab').forEach(tab => {
                tab.addEventListener('click', () => this.switchVacinaTab(tab.dataset.tab));
            });
            
            // Bind checkboxes
            this.bindVacinaCheckboxes();
        } catch (error) {
            alert('❌ Erro ao carregar vacinas');
        }
    }
    
    async fetchVacinasStatus() {
        try {
            const response = await fetch('/api/vacinas/status');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Erro ao buscar status:', error);
        }
        return {};
    }
    
    renderVacinasMae(maeData, status) {
        const vacinasTomadas = status.mae || [];
        const nomesTomadas = new Set(vacinasTomadas.map(v => v.nome));
        let html = '';
        
        for (const [key, periodo] of Object.entries(maeData)) {
            if (key !== 'calendario' && key !== 'importante' && 'vacinas' in periodo) {
                html += `
                    <div class="vacina-card">
                        <h4>${periodo.nome || key}</h4>
                        ${periodo.descricao ? `<p style="margin-bottom: 1rem; color: #666;">${periodo.descricao}</p>` : ''}
                        ${periodo.vacinas ? periodo.vacinas.map(v => {
                            const isChecked = nomesTomadas.has(v.nome);
                            return `
                                <div class="vacina-item ${isChecked ? 'checked' : ''}" data-tipo="mae" data-nome="${this.escapeHtml(v.nome)}">
                                    <label class="vacina-checkbox-label">
                                        <input type="checkbox" ${isChecked ? 'checked' : ''}>
                                        <span class="checkmark"></span>
                                        <div class="vacina-info">
                                            <strong>💉 ${v.nome}</strong>
                                            ${v.quando ? `<div class="vacina-detail">⏰ ${v.quando}</div>` : ''}
                                            ${v.dose ? `<div class="vacina-detail">📅 ${v.dose}</div>` : ''}
                                            ${v.onde ? `<div class="vacina-detail">🏥 ${v.onde}</div>` : ''}
                                            ${v.documentos ? `<div class="vacina-detail">📋 ${v.documentos}</div>` : ''}
                                            ${v.protege ? `<div class="vacina-detail">🛡️ ${v.protege}</div>` : ''}
                                            ${v.observacao ? `<em style="color: #8b5a5a; font-size: 0.9em;">${v.observacao}</em>` : ''}
                                        </div>
                                    </label>
                                </div>
                            `;
                        }).join('') : ''}
                    </div>
                `;
            }
        }
        
        if (maeData.importante) {
            html += `<div class="alerta-importante">⚠️ ${maeData.importante}</div>`;
        }
        
        return html;
    }
    
    renderVacinasBebe(bebeData, status) {
        const vacinasTomadas = status.bebe || [];
        const nomesTomadas = new Set(vacinasTomadas.map(v => v.nome));
        let html = '';
        
        for (const [key, periodo] of Object.entries(bebeData)) {
            if (key !== 'calendario' && key !== 'recomendacoes' && key !== 'carteira_vacinacao' && 'vacinas' in periodo) {
                html += `
                    <div class="vacina-card">
                        <h4>${periodo.idade || key}</h4>
                        ${periodo.vacinas ? periodo.vacinas.map(v => {
                            const isChecked = nomesTomadas.has(v.nome);
                            return `
                                <div class="vacina-item ${isChecked ? 'checked' : ''}" data-tipo="bebe" data-nome="${this.escapeHtml(v.nome)}">
                                    <label class="vacina-checkbox-label">
                                        <input type="checkbox" ${isChecked ? 'checked' : ''}>
                                        <span class="checkmark"></span>
                                        <div class="vacina-info">
                                            <strong>💉 ${v.nome}</strong>
                                            ${v.doenca ? `<div class="vacina-detail">🦠 ${v.doenca}</div>` : ''}
                                            ${v.local ? `<div class="vacina-detail">🏥 ${v.local}</div>` : ''}
                                            ${v.onde ? `<div class="vacina-detail">🏥 ${v.onde}</div>` : ''}
                                            ${v.documentos ? `<div class="vacina-detail">📋 ${v.documentos}</div>` : ''}
                                            ${v.observacao ? `<em style="color: #8b5a5a; font-size: 0.9em;">${v.observacao}</em>` : ''}
                                        </div>
                                    </label>
                                </div>
                            `;
                        }).join('') : ''}
                    </div>
                `;
            }
        }
        
        return html;
    }
    
    switchVacinaTab(tab) {
        document.querySelectorAll('.vacina-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.vacina-tab-content').forEach(c => c.classList.remove('active'));
        
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
        document.getElementById(`vacinas-${tab}`).classList.add('active');
    }
    
    bindVacinaCheckboxes() {
        document.querySelectorAll('.vacina-item input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', async (e) => {
                const item = e.target.closest('.vacina-item');
                const tipo = item.dataset.tipo;
                const nome = item.dataset.nome;
                const isChecked = e.target.checked;
                
                if (isChecked) {
                    await this.marcarVacina(tipo, nome, item);
                } else {
                    await this.desmarcarVacina(tipo, nome, item);
                }
            });
        });
    }
    
    async marcarVacina(tipo, nome, itemElement) {
        try {
            const response = await fetch('/api/vacinas/marcar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tipo, vacina_nome: nome})
            });
            
            const data = await response.json();
            
            if (response.ok) {
                itemElement.classList.add('checked');
                this.showCelebration();
            } else {
                alert('⚠️ ' + data.erro);
                itemElement.querySelector('input').checked = false;
            }
        } catch (error) {
            alert('❌ Erro ao marcar vacina');
            itemElement.querySelector('input').checked = false;
        }
    }
    
    async desmarcarVacina(tipo, nome, itemElement) {
        try {
            const response = await fetch('/api/vacinas/desmarcar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tipo, vacina_nome: nome})
            });
            
            if (response.ok) {
                itemElement.classList.remove('checked');
            }
        } catch (error) {
            alert('❌ Erro ao desmarcar vacina');
        }
    }
    
    showCelebration() {
        const celebration = document.createElement('div');
        celebration.className = 'celebration-overlay';
        celebration.innerHTML = `
            <div class="celebration-content">
                <div class="celebration-emoji">🎉</div>
                <h2>Parabéns, Mamãe! 🎉</h2>
                <p>Você cuidou da saúde!</p>
                <p style="font-size: 0.9em; margin-top: 1rem;">Obrigada por se proteger 💕</p>
            </div>
        `;
        document.body.appendChild(celebration);
        
        setTimeout(() => {
            celebration.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            celebration.classList.remove('show');
            setTimeout(() => celebration.remove(), 500);
        }, 3000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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

