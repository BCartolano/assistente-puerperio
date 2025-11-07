class ChatbotPuerperio {
    constructor() {
        this.userId = this.generateUserId();
        
        // Função auxiliar para remover elementos de forma segura
        this.safeRemoveElement = (element) => {
            if (!element) return false;
            
            // Verifica se o elemento ainda está no DOM
            if (!element.parentNode) {
                console.warn('⚠️ [DOM] Elemento já foi removido do DOM');
                return false;
            }
            
            try {
                // Tenta usar o método moderno remove()
                if (typeof element.remove === 'function') {
                    element.remove();
                    return true;
                }
                // Fallback para removeChild se remove() não estiver disponível
                else if (element.parentNode) {
                    element.parentNode.removeChild(element);
                    return true;
                }
            } catch (e) {
                console.warn('⚠️ [DOM] Erro ao remover elemento:', e);
                // Última tentativa: verifica se ainda existe parentNode e tenta remover
                if (element.parentNode) {
                    try {
                        element.parentNode.removeChild(element);
                        return true;
                    } catch (e2) {
                        console.error('❌ [DOM] Erro crítico ao remover elemento:', e2);
                        return false;
                    }
                }
            }
            return false;
        };
        this.isTyping = false;
        this.categories = [];
        this.deviceType = this.detectDevice();
        this.userLoggedIn = false;
        this.currentUserName = null;
        
        this.initializeLoginElements();
        this.bindInitialLoginEvents();
        this.checkIfLoggedIn();
    }
    
    checkIfLoggedIn() {
        // Check if user is already logged in
        fetch('/api/user', {
            credentials: 'include'
        })
            .then(res => {
                if (res.ok) {
                    return res.json().then(user => {
                        console.log('✅ [AUTH] Usuário já está logado:', user.name);
                        this.userLoggedIn = true;
                        this.currentUserName = user.name;
                        
                        // IMPORTANTE: Atualiza userId com o ID real do backend
                        if (user.id) {
                            this.userId = user.id;
                            console.log(`✅ [AUTH] userId atualizado para: ${this.userId}`);
                        }
                        
                        this.updateWelcomeMessage(this.currentUserName);
                        this.initMainApp();
                        // Garante que o Menu Inicial está visível ao recarregar
                        this.backToWelcomeScreen();
                    });
                } else {
                    // User not logged in, show login screen
                    // 401 é esperado quando não está logado - não é um erro
                    this.userLoggedIn = false;
                    this.currentUserName = null;
                    this.showLoginScreen();
                    
                    // Carrega histórico mesmo sem estar logado (para usuários anônimos)
                    // O userId já foi gerado no constructor e está salvo no localStorage
                    this.loadChatHistory();
                }
            })
            .catch((error) => {
                // Erro na requisição - assume que não está logado
                this.userLoggedIn = false;
                this.currentUserName = null;
                this.showLoginScreen();
                
                // Carrega histórico mesmo sem estar logado (para usuários anônimos)
                // O userId já foi gerado no constructor e está salvo no localStorage
                this.loadChatHistory();
            });
    }
    
    updateWelcomeMessage(userName) {
        // Remove qualquer botão antigo que possa existir (cache do navegador)
        const oldAccountBtn = document.getElementById('account-btn');
        if (oldAccountBtn) {
            oldAccountBtn.style.display = 'none';
            if (this.safeRemoveElement(oldAccountBtn)) {
                console.log('✅ [WELCOME] Botão antigo removido');
            }
        }
        
        // Garante que o elemento existe
        if (!this.userGreeting) {
            this.userGreeting = document.getElementById('user-greeting');
        }
        
        // Atualiza mensagem de boas-vindas com saudação variável conforme hora do dia
        if (this.userGreeting && userName) {
            // Pega apenas o primeiro nome
            const firstName = userName.split(' ')[0];
            
            // Determina saudação conforme hora do dia
            const now = new Date();
            const hour = now.getHours();
            let greeting;
            
            if (hour >= 5 && hour < 12) {
                greeting = `Bom dia, ${firstName} 🌅`;
            } else if (hour >= 12 && hour < 18) {
                greeting = `Boa tarde, ${firstName} ☀️`;
            } else if (hour >= 18 && hour < 22) {
                greeting = `Boa noite, ${firstName} 🌆`;
            } else {
                greeting = `Boa madrugada, ${firstName} 🌙`;
            }
            
            this.userGreeting.textContent = greeting;
            console.log(`✅ [WELCOME] Mensagem atualizada: ${greeting}`);
        }
    }
    
    initMainApp() {
        console.log('🚀 [INIT] initMainApp chamado');
        const loginScreen = document.getElementById('login-screen');
        const mainContainer = document.getElementById('main-container');
        
        if (loginScreen) {
            loginScreen.classList.add('hidden');
            loginScreen.style.display = 'none';
            console.log('✅ [INIT] Tela de login ocultada');
        } else {
            console.error('❌ [INIT] Elemento login-screen não encontrado!');
        }
        
        if (mainContainer) {
            mainContainer.style.display = 'flex';
            mainContainer.classList.remove('hidden');
            console.log('✅ [INIT] Container principal exibido');
        } else {
            console.error('❌ [INIT] Elemento main-container não encontrado!');
        }
        
        // Mostra o footer quando o app é inicializado
        const footer = document.getElementById('app-footer');
        if (footer) {
            footer.style.display = 'block';
            console.log('✅ [INIT] Footer exibido');
        }
        
                  // Verifica se os elementos existem antes de inicializar
          try {
              this.initializeElements();
              this.bindEvents();

              // Só carrega categorias se o container existir
              // Nota: O container de categorias pode não existir mais no HTML atual
              // Isso é normal e não impede o funcionamento do app
              if (this.categoriesContainer) {
                  this.loadCategories();
              }
              // Não exibe aviso se não encontrado - é opcional

              this.loadChatHistory();
              this.requestNotificationPermission();
              this.optimizeForDevice();

                              // Inicializa o status de conexão após os elementos serem carregados
                // Pequeno delay para garantir que o DOM está totalmente renderizado
                setTimeout(() => {
                    this.checkConnectionStatus();
                }, 100);

                // Inicializa o carrossel de features após os elementos serem renderizados
                setTimeout(() => {
                    if (typeof initFeatureCarousel === 'function') {
                        initFeatureCarousel();
                    }
                }, 200);

                // Inicializa mensagem rotativa
                this.initRotatingMessage();
                
                // Inicializa botões de sentimento
                this.initFeelingButtons();
                
                // Inicializa links de apoio rápido
                this.initSupportLinks();

                // Foca no input de mensagem se existir
                if (this.messageInput) {
                    setTimeout(() => {
                        this.messageInput.focus();
                    }, 300);
                }

                console.log('✅ [INIT] App inicializado com sucesso');
          } catch (error) {
              console.error('❌ [INIT] Erro ao inicializar app:', error);
          }
    }
    
    showLoginScreen() {
        // Garante que a tela de login está visível e o menu oculto
        const loginScreen = document.getElementById('login-screen');
        const mainContainer = document.getElementById('main-container');
        
        if (loginScreen) {
            loginScreen.style.display = 'flex';
            loginScreen.classList.remove('hidden');
        }
        
        if (mainContainer) {
            mainContainer.style.display = 'none';
            mainContainer.classList.add('hidden');
        }
        
        // Reset do estado de login
        this.userLoggedIn = false;
        this.currentUserName = null;
        
        console.log('✅ [LOGIN] Tela de login exibida');
    }
    
    initializeLoginElements() {
        this.loginScreen = document.getElementById('login-screen');
        this.initialLoginForm = document.getElementById('initial-login-form');
        this.initialRegisterForm = document.getElementById('initial-register-form');
        this.loginTabs = document.querySelectorAll('.login-tab');
        
        // Move ícones dos labels para dentro dos inputs (apenas se os formulários existirem)
        if (this.initialLoginForm || this.initialRegisterForm) {
            this.moveIconsIntoInputs();
        }
    }
    
    moveIconsIntoInputs() {
        // Mapeamento de ícones por tipo de input
        const iconMap = {
            'email': 'fa-envelope',
            'password': 'fa-lock',
            'text': 'fa-user', // padrão para text
            'name': 'fa-user',
            'baby_name': 'fa-baby'
        };
        
        // Função para criar ícone dentro do input
        const createInputIcon = (input, iconClass) => {
            // Remove ícone anterior se existir
            const existingIcon = input.parentElement.querySelector('.input-icon');
            if (existingIcon) {
                existingIcon.remove();
            }
            
            // Cria um wrapper ao redor do input se não existir
            let inputWrapper = input.parentElement.querySelector('.input-wrapper');
            if (!inputWrapper) {
                inputWrapper = document.createElement('div');
                inputWrapper.className = 'input-wrapper';
                inputWrapper.style.cssText = 'position: relative; width: 100%;';
                input.parentNode.insertBefore(inputWrapper, input);
                inputWrapper.appendChild(input);
            }
            
            // Cria novo ícone
            const icon = document.createElement('i');
            icon.className = `fas ${iconClass} input-icon`;
            icon.style.cssText = `
                position: absolute !important;
                left: 1rem !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                z-index: 10 !important;
                pointer-events: none;
                color: #f4a6a6 !important;
                font-size: 1.1rem !important;
                transition: none !important;
                margin: 0 !important;
                padding: 0 !important;
                line-height: 1 !important;
            `;
            // Insere o ícone no wrapper (que contém o input)
            inputWrapper.appendChild(icon);
            
            // Função simples para manter o ícone centralizado (agora que está no wrapper)
            const updateIconPosition = () => {
                // Com o wrapper, o ícone já está posicionado corretamente usando top: 50%
                // Apenas garante que o transform está correto
                icon.style.top = '50%';
                icon.style.transform = 'translateY(-50%)';
                icon.style.left = '1rem';
            };
            
            // Atualiza a posição quando necessário
            const resizeHandler = () => setTimeout(updateIconPosition, 10);
            window.addEventListener('resize', resizeHandler);
            
            // Garante que o ícone não se mova quando o input recebe foco
            input.addEventListener('focus', () => {
                setTimeout(updateIconPosition, 50);
            });
            
            input.addEventListener('blur', () => {
                setTimeout(updateIconPosition, 50);
            });
            
            // Observa mudanças no layout do input
            if (window.ResizeObserver) {
                const resizeObserver = new ResizeObserver(() => {
                    updateIconPosition();
                });
                resizeObserver.observe(input);
            }
            
            // Atualiza após um delay para garantir que o layout está completo
            setTimeout(updateIconPosition, 100);
            setTimeout(updateIconPosition, 500);
        };
        
        // Processa todos os inputs dos formulários de login
        const inputs = document.querySelectorAll('.login-form .form-group input');
        inputs.forEach(input => {
            const type = input.type;
            const name = input.name;
            const id = input.id;
            
            let iconClass = iconMap[type] || 'fa-user';
            
            // Ícones específicos por ID
            if (id === 'initial-login-email' || id === 'initial-register-email') {
                iconClass = 'fa-envelope';
            } else if (id === 'initial-login-password' || id === 'initial-register-password') {
                iconClass = 'fa-lock';
            } else if (id === 'initial-register-name') {
                iconClass = 'fa-user';
            } else if (id === 'initial-register-baby') {
                iconClass = 'fa-baby';
            } else if (name === 'name') {
                iconClass = 'fa-user';
            } else if (name === 'baby_name') {
                iconClass = 'fa-baby';
            }
            
            createInputIcon(input, iconClass);
        });
    }
    
    bindInitialLoginEvents() {
        // Verifica se os elementos existem antes de adicionar event listeners
        if (!this.initialLoginForm && !this.initialRegisterForm) {
            // Se não existirem, provavelmente estamos em uma página diferente (ex: forgot-password)
            return;
        }
        
        // Tab switching (apenas se existirem tabs)
        if (this.loginTabs && this.loginTabs.length > 0) {
            this.loginTabs.forEach(tab => {
                tab.addEventListener('click', () => this.switchInitialTab(tab.dataset.tab));
            });
        }
        
        // Preenche email automaticamente se estiver salvo
        this.loadRememberedEmail();
        
        // Login form submission
        if (this.initialLoginForm) {
            this.initialLoginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleInitialLogin();
            });
        }
        
        // Register form submission
        if (this.initialRegisterForm) {
            this.initialRegisterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleInitialRegister();
            });
        }
        
        // Forgot password link
        const forgotPasswordLink = document.getElementById('forgot-password-link');
        if (forgotPasswordLink) {
            forgotPasswordLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleForgotPassword();
            });
        }
    }
    
    loadRememberedEmail() {
        // Carrega email salvo do localStorage e preenche o campo
        // Verifica se o campo de email existe antes de tentar preencher
        const emailInput = document.getElementById('initial-login-email');
        if (!emailInput) {
            return;
        }
        
        const rememberedEmail = localStorage.getItem('remembered_email');
        if (rememberedEmail) {
            emailInput.value = rememberedEmail;
            // Marca o checkbox como checked
            const rememberMeCheckbox = document.getElementById('initial-remember-me');
            if (rememberMeCheckbox) {
                rememberMeCheckbox.checked = true;
            }
            console.log('💾 [LOGIN] Email lembrado carregado:', rememberedEmail);
        }
    }
    
    switchInitialTab(tab) {
        if (!this.loginTabs || !this.initialLoginForm || !this.initialRegisterForm) {
            return;
        }
        
        this.loginTabs.forEach(t => t.classList.remove('active'));
        this.initialLoginForm.classList.remove('active');
        this.initialRegisterForm.classList.remove('active');
        
        if (tab === 'login') {
            document.querySelector('[data-tab="login"]').classList.add('active');
            this.initialLoginForm.classList.add('active');
        } else if (tab === 'register') {
            document.querySelector('[data-tab="register"]').classList.add('active');
            this.initialRegisterForm.classList.add('active');
        }
    }
    
    async handleInitialLogin() {
        const email = document.getElementById('initial-login-email').value.trim().toLowerCase();
        const password = document.getElementById('initial-login-password').value.trim(); // Remove espaços
        const rememberMe = document.getElementById('initial-remember-me').checked;
        
        if (!email || !password) {
            alert('Por favor, preencha todos os campos! 💕');
            return;
        }
        
        console.log(`🔍 [LOGIN] Tentando login com email: ${email}, password length: ${password.length}, remember_me: ${rememberMe}`);
        
        // Salva email no localStorage se "Lembre-se de mim" estiver marcado
        if (rememberMe) {
            localStorage.setItem('remembered_email', email);
            console.log('💾 [LOGIN] Email salvo no localStorage');
        } else {
            localStorage.removeItem('remembered_email');
            console.log('🗑️ [LOGIN] Email removido do localStorage');
        }
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include',  // Importante para cookies de sessão
                body: JSON.stringify({email, password, remember_me: rememberMe})
            });
            
            const data = await response.json();
            console.log('🔍 [LOGIN] Resposta completa:', data);
            console.log('🔍 [LOGIN] Status HTTP:', response.status);
            console.log('🔍 [LOGIN] response.ok:', response.ok);
            console.log('🔍 [LOGIN] data.sucesso:', data.sucesso);
            console.log('🔍 [LOGIN] data.user:', data.user);
            
            // Se houver erro específico de email não verificado, mostra mensagem mais clara
            if (data.erro && data.mensagem && data.pode_login === false) {
                const userEmail = data.email || email;
                const resend = confirm(`⚠️ ${data.mensagem}\n\nDeseja que eu reenvie o email de verificação agora?`);
                if (resend) {
                    this.resendVerificationEmail(userEmail);
                }
                return;
            }
            
            if (response.ok && (data.sucesso === true || data.user)) {
                console.log('✅ [LOGIN] Login bem-sucedido, inicializando app...');
                this.userLoggedIn = true;
                this.currentUserName = data.user ? data.user.name : email;
                
                // IMPORTANTE: Atualiza userId com o ID real do backend
                if (data.user && data.user.id) {
                    this.userId = data.user.id;
                    console.log(`✅ [LOGIN] userId atualizado para: ${this.userId}`);
                }
                
                // Atualiza mensagem de boas-vindas
                this.updateWelcomeMessage(this.currentUserName);
                
                // Mostra mensagem de boas-vindas se disponível
                if (data.mensagem) {
                    console.log('💕 Mensagem:', data.mensagem);
                }
                
                // Pequeno delay para garantir que a sessão está criada
                setTimeout(() => {
                    console.log('🚀 [LOGIN] Chamando initMainApp...');
                    this.initMainApp();
                }, 200);
            } else {
                console.log('❌ [LOGIN] Login falhou ou resposta inválida');
                if (data.pode_login === false && data.mensagem) {
                    // Email não verificado
                    if (confirm(data.mensagem + '\n\nDeseja reenviar o email de verificação?')) {
                        await this.resendVerificationEmail(email);
                    }
                } else {
                    alert('⚠️ ' + (data.erro || data.mensagem || 'Erro ao fazer login'));
                    console.error('❌ [LOGIN] Erro detalhado:', data);
                }
            }
        } catch (error) {
            console.error('Erro ao fazer login:', error);
            alert('❌ Erro ao fazer login. Tente novamente.');
        }
    }
    
    handleForgotPassword() {
        // Redireciona para a página dedicada de recuperação de senha
        window.location.href = '/forgot-password';
    }
    
    async resendVerificationEmail(email) {
        if (!email) {
            email = document.getElementById('initial-login-email')?.value.trim().toLowerCase();
            if (!email) {
                this.showNotification(
                    'Email necessário',
                    'Por favor, digite seu email para reenviar a verificação.',
                    'error'
                );
                return;
            }
        }
        
        try {
            this.showNotification(
                'Enviando email...',
                'Aguarde enquanto reenviamos o email de verificação.',
                'success'
            );
            
            const response = await fetch('/api/resend-verification', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: email.toLowerCase()})
            });
            
            const data = await response.json();
            
            if (data.sucesso) {
                this.showNotification(
                    'Email reenviado! 📧',
                    data.mensagem + ' Verifique, também, a pasta de spam.',
                    'success'
                );
            } else {
                this.showNotification(
                    'Erro ao reenviar ⚠️',
                    data.erro || 'Não foi possível reenviar o email. Tente novamente mais tarde.',
                    'error'
                );
            }
        } catch (error) {
            console.error('Erro ao reenviar email:', error);
            this.showNotification(
                'Erro ao reenviar ❌',
                'Erro ao reenviar email. Tente novamente ou verifique se o email está configurado no servidor.',
                'error'
            );
        }
    }
    
    async handleLogout() {
        // Mostra modal de confirmação customizado
        const confirmModal = document.getElementById('logout-confirm-modal');
        if (!confirmModal) {
            // Fallback se o modal não existir (não deveria acontecer)
            if (!confirm('Tem certeza de que deseja sair da sua conta? 💕')) {
                return;
            }
        } else {
            // Mostra o modal
            confirmModal.style.display = 'flex';
            
            // Busca os botões
            const confirmBtn = document.getElementById('logout-confirm-btn');
            const cancelBtn = document.getElementById('logout-cancel-btn');
            const closeBtn = document.getElementById('close-logout-confirm');
            
            // Função para fechar o modal
            const closeModal = () => {
                confirmModal.style.display = 'none';
            };
            
            // Função para fazer logout
            const proceedLogout = () => {
                closeModal();
                this.performLogout();
            };
            
            // Remove listeners antigos e adiciona novos (usando once: true para evitar duplicação)
            const handleConfirm = () => {
                proceedLogout();
            };
            
            const handleCancel = () => {
                closeModal();
            };
            
            const handleOutsideClick = (e) => {
                if (e.target === confirmModal) {
                    closeModal();
                }
            };
            
            // Remove listeners anteriores se existirem
            if (confirmBtn) {
                confirmBtn.replaceWith(confirmBtn.cloneNode(true));
            }
            if (cancelBtn) {
                cancelBtn.replaceWith(cancelBtn.cloneNode(true));
            }
            if (closeBtn) {
                closeBtn.replaceWith(closeBtn.cloneNode(true));
            }
            
            // Adiciona novos listeners
            document.getElementById('logout-confirm-btn')?.addEventListener('click', handleConfirm);
            document.getElementById('logout-cancel-btn')?.addEventListener('click', handleCancel);
            document.getElementById('close-logout-confirm')?.addEventListener('click', handleCancel);
            
            // Remove listener anterior se existir e adiciona novo para clicar fora do modal
            confirmModal.removeEventListener('click', handleOutsideClick);
            confirmModal.addEventListener('click', handleOutsideClick);
        }
    }
    
    async performLogout() {
        try {
            const response = await fetch('/api/logout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include'
            });
            
            // Mesmo se der erro, força logout local
            this.userLoggedIn = false;
            this.currentUserName = null;
            
            // Limpa histórico local
            if (this.chatMessages) {
                this.chatMessages.innerHTML = '';
            }
            
            // Se o usuário estava logado, limpa o userId do localStorage
            // Para usuários não logados, mantém o userId para preservar histórico
            // Mas se estava logado, gera novo userId para próxima sessão
            localStorage.removeItem('chatbot_user_id');
            this.userId = this.generateUserId();
            
            // Volta para tela de login
            this.showLoginScreen();
            
            // Mostra notificação de despedida
            setTimeout(() => {
                this.showNotification(
                    'Até logo! 👋',
                    'Você saiu da sua conta. Volte sempre! 💕',
                    'success'
                );
            }, 300); // Pequeno delay para garantir que a tela de login já foi exibida
            
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
            // Força logout local mesmo com erro
            this.userLoggedIn = false;
            this.currentUserName = null;
            this.showLoginScreen();
            
            // Mostra notificação de despedida mesmo com erro
            setTimeout(() => {
                this.showNotification(
                    'Até logo! 👋',
                    'Você saiu da sua conta. Volte sempre! 💕',
                    'success'
                );
            }, 300);
        }
    }
    
    async handleInitialRegister() {
        const name = document.getElementById('initial-register-name').value.trim();
        const email = document.getElementById('initial-register-email').value.trim();
        const password = document.getElementById('initial-register-password').value;
        const babyName = document.getElementById('initial-register-baby').value.trim();
        
        if (!name || !email || !password) {
            alert('Por favor, preencha os campos obrigatórios! 💕');
            return;
        }
        
        if (password.length < 6) {
            alert('A senha deve ter no mínimo 6 caracteres! 💕');
            return;
        }
        
        try {
            const requestData = {
                name: name,
                email: email,
                password: password,
                baby_name: babyName || ''
            };
            
            console.log('[REGISTER] Enviando dados:', {
                name: name,
                email: email,
                password: '***',
                baby_name: babyName || ''
            });
            
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(requestData)
            });
            
            console.log('[REGISTER] Status da resposta:', response.status);
            
            const data = await response.json();
            console.log('[REGISTER] Resposta do servidor:', data);
            
            if (response.ok) {
                // Mostra notificação de sucesso
                this.showNotification(
                    'Cadastro realizado! 🎉',
                    data.verification_sent ? 
                        'O link de verificação de email foi enviado para ' + email + '. Verifique sua caixa de entrada! 💕' :
                        data.mensagem,
                    'success'
                );
                // Auto switch to login after successful registration
                this.switchInitialTab('login');
                document.getElementById('initial-login-email').value = email;
            } else {
                // Mostra mensagem de erro específica do servidor
                const errorMessage = data.erro || data.mensagem || 'Erro ao cadastrar. Tente novamente.';
                console.error('[REGISTER] Erro:', errorMessage);
                this.showNotification(
                    'Erro no cadastro ⚠️',
                    errorMessage,
                    'error'
                );
            }
        } catch (error) {
            console.error('[REGISTER] Erro na requisição:', error);
            this.showNotification(
                'Erro ao cadastrar ❌',
                'Erro ao cadastrar. Verifique sua conexão e tente novamente.',
                'error'
            );
        }
    }
    
    generateUserId() {
        // Tenta recuperar userId do localStorage primeiro
        let userId = localStorage.getItem('chatbot_user_id');
        
        // Se não existe, gera um novo e salva no localStorage
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('chatbot_user_id', userId);
            console.log('🆕 [USER_ID] Novo userId gerado e salvo:', userId);
        } else {
            console.log('✅ [USER_ID] userId recuperado do localStorage:', userId);
        }
        
        return userId;
    }
    
    showNotification(title, message, type = 'success') {
        // Remove notificação anterior se existir
        const existingNotification = document.querySelector('.notification-toast');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Cria elemento da notificação
        const notification = document.createElement('div');
        notification.className = `notification-toast ${type}`;
        
        // Ícone baseado no tipo
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        notification.innerHTML = `
            <i class="fas ${icon} notification-icon"></i>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" aria-label="Fechar">&times;</button>
        `;
        
        // Adiciona ao body
        document.body.appendChild(notification);
        
        // Fecha ao clicar no botão X
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.hideNotification(notification);
        });
        
        // Auto-fecha após 3 segundos
        setTimeout(() => {
            this.hideNotification(notification);
        }, 3000);
    }
    
    hideNotification(notification) {
        if (notification && notification.parentNode) {
            notification.classList.add('hiding');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }
    
    initializeElements() {
        this.messageInput = document.getElementById('message-input');
        // Desabilita autocomplete do Chrome para evitar sugestões de email/senha
        if (this.messageInput) {
            this.messageInput.setAttribute('autocomplete', 'off');
            this.messageInput.setAttribute('data-lpignore', 'true');
            this.messageInput.setAttribute('data-form-type', 'other');
            // Força desabilitar autocomplete via JavaScript
            this.messageInput.autocomplete = 'off';
        }
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.welcomeMessage = document.getElementById('welcome-message');
        this.sidebar = document.getElementById('sidebar');
        this.menuToggle = document.getElementById('menu-toggle');
        this.menuToggleHeader = document.getElementById('menu-toggle-header');
        this.closeSidebar = document.getElementById('close-sidebar');
        
        // Log para debug
        console.log('🔍 [INIT] Elementos do sidebar:');
        console.log('🔍 [INIT] sidebar:', !!this.sidebar);
        console.log('🔍 [INIT] menuToggle:', !!this.menuToggle);
        console.log('🔍 [INIT] closeSidebar:', !!this.closeSidebar);
        this.clearHistoryBtn = document.getElementById('clear-history');
        this.categoriesContainer = document.getElementById('categories'); // Pode ser null se não existir no HTML
        
        // Sidebar new buttons
        this.sidebarBtnGuias = document.getElementById('sidebar-btn-guias');
        this.sidebarBtnGestacao = document.getElementById('sidebar-btn-gestacao');
        this.sidebarBtnPosparto = document.getElementById('sidebar-btn-posparto');
        this.sidebarBtnVacinas = document.getElementById('sidebar-btn-vacinas');
        this.sidebarBtnClear = document.getElementById('sidebar-btn-clear');
        this.sidebarBtnBack = document.getElementById('sidebar-btn-back');
        this.sidebarBtnLogout = document.getElementById('sidebar-btn-logout');
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
        this.userGreeting = document.getElementById('user-greeting');
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
        
        // Botão de iniciar conversa
        this.startChatBtn = document.getElementById('start-chat-btn');
    }
    
        bindEvents() {
        // Envio de mensagem
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Contador de caracteres
            this.messageInput.addEventListener('input', () => this.updateCharCount());
        }

        // Menu sidebar - ambos os botões (header e input-area)
        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        }
        if (this.menuToggleHeader) {
            this.menuToggleHeader.addEventListener('click', () => this.toggleSidebar());
        }
        
        if (this.closeSidebar) {
            this.closeSidebar.addEventListener('click', () => this.closeSidebarMenu());
        }

        // Limpar histórico
        if (this.clearHistoryBtn) {
            this.clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        }

        // Voltar ao início
        if (this.backBtn) {
            this.backBtn.addEventListener('click', () => this.backToWelcomeScreen());
        }
        
        // Botão de iniciar conversa
        if (this.startChatBtn) {
            this.startChatBtn.addEventListener('click', () => this.startChat());
        }
        
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
        this.sidebarBtnLogout?.addEventListener('click', () => {
            this.closeSidebarMenu();
            this.handleLogout();
        });
        
        // Quick questions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-btn')) {
                const question = e.target.dataset.question;
                if (this.messageInput && question) {
                    this.messageInput.value = question;
                    this.sendMessage();
                }
            }
        });
        
                // Modal de alerta
        if (this.closeAlert) {
            this.closeAlert.addEventListener('click', () => this.hideAlert());
        }
        if (this.emergencyCall) {
            this.emergencyCall.addEventListener('click', () => this.callEmergency());
        }
        if (this.findDoctor) {
            this.findDoctor.addEventListener('click', () => this.findDoctorNearby());
        }

        // Fechar modal clicando fora
        if (this.alertModal) {
            this.alertModal.addEventListener('click', (e) => {
                if (e.target === this.alertModal) {
                    this.hideAlert();
                }
            });
        }

        // Fechar sidebar clicando fora
        document.addEventListener('click', (e) => {
            if (this.sidebar && 
                this.sidebar.classList && 
                this.sidebar.classList.contains('open') && 
                (this.menuToggle || this.menuToggleHeader) &&
                !this.sidebar.contains(e.target) && 
                !(this.menuToggle && this.menuToggle.contains(e.target)) &&
                !(this.menuToggleHeader && this.menuToggleHeader.contains(e.target))) {
                this.closeSidebarMenu();
            }
        });
        
        // Auth modal events
        // Botão de conta removido - substituído por mensagem de boas-vindas
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
        // Verifica se os elementos existem antes de usar
        if (!this.messageInput || !this.charCount) {
            return;
        }

        const count = this.messageInput.value ? this.messageInput.value.length : 0;
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
            if (this.categoriesContainer) {
                this.categoriesContainer.innerHTML = `
                    <div class="category-item">
                        <i class="fas fa-exclamation-triangle"></i>
                        Erro ao carregar categorias
                    </div>
                `;
            }
        }
    }
    
    renderCategories() {
        if (!this.categoriesContainer) {
            console.warn('categoriesContainer não encontrado');
            return;
        }
        
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
                if (this.messageInput) {
                    this.messageInput.value = `Fale sobre ${category}`;
                    if (typeof this.messageInput.focus === 'function') {
                        this.messageInput.focus();
                    }
                }
                this.closeSidebarMenu();
            });
            
            this.categoriesContainer.appendChild(categoryElement);
        });
    }
    
    formatCategoryName(category) {
        return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
        async sendMessage() {
        // Verifica se messageInput existe antes de usar
        if (!this.messageInput || !this.messageInput.value) {
            console.warn('messageInput não está disponível');
            return;
        }

        const message = this.messageInput.value.trim();
        if (!message) return;

        // Marca que o usuário já interagiu (para mostrar mensagem de boas-vindas nas próximas vezes)
        localStorage.setItem(`sophia_has_interacted_${this.userId}`, 'true');

        // Adiciona mensagem do usuário
        this.addMessage(message, 'user');
        
        if (this.messageInput) {
            this.messageInput.value = '';
        }
        this.updateCharCount();

        // Desabilita o botão de enviar para evitar múltiplos envios
        if (this.sendButton) {
            this.sendButton.disabled = true;
        }
        if (this.messageInput) {
            this.messageInput.disabled = true;
        }

        // Esconde welcome message e mostra chat
        if (this.welcomeMessage) {
            this.welcomeMessage.style.display = 'none';
        }
        if (this.chatMessages) {
            this.chatMessages.classList.add('active');
        }
        // Mostra o input do chat (usa .input-area diretamente)
        const inputArea = document.querySelector('.input-area');
        if (inputArea && inputArea.style) {
            inputArea.style.display = 'flex';
        }
        // Botão "Voltar ao Menu" removido - usuário pode usar o menu lateral

        // Mostra indicador de digitação
        this.showTyping();

        try {
            console.log('📤 Enviando mensagem:', message);
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Importante para cookies de sessão
                body: JSON.stringify({
                    pergunta: message,
                    user_id: this.userId
                })
            });

            console.log('📥 Resposta recebida, status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Erro na resposta:', response.status, errorText);
                throw new Error(`Erro na resposta do servidor: ${response.status}`);
            }

            const data = await response.json();
            console.log('✅ Dados recebidos:', data);

            // Esconde indicador de digitação
            this.hideTyping();

            // Verifica se há uma resposta válida
            if (data.resposta) {
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
            } else {
                console.warn('⚠️ Resposta vazia recebida:', data);
                this.addMessage(
                    'Desculpe, não consegui processar sua pergunta. Tente reformulá-la ou tente novamente mais tarde.',
                    'assistant'
                );
            }

        } catch (error) {
            console.error('❌ Erro ao enviar mensagem:', error);
            this.hideTyping();
            this.addMessage(
                'Desculpe, ocorreu um erro ao processar sua pergunta. Verifique sua conexão e tente novamente.',
                'assistant'
            );
        } finally {
            // Reabilita o botão e input
            if (this.sendButton) {
                this.sendButton.disabled = false;
            }
            if (this.messageInput) {
                this.messageInput.disabled = false;
                // Foca no input para permitir nova mensagem
                if (typeof this.messageInput.focus === 'function') {
                    this.messageInput.focus();
                }
            }
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

        // Verifica se chatMessages existe antes de adicionar mensagem
        if (!this.chatMessages) {
            console.warn('chatMessages não está disponível');
            return;
        }

        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Converte quebras de linha em HTML
        return content.replace(/\n/g, '<br>');
    }
    
        showTyping() {
        this.isTyping = true;
        if (this.typingIndicator && this.typingIndicator.classList) {
            this.typingIndicator.classList.add('show');
        }
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        if (this.typingIndicator && this.typingIndicator.classList) {
            this.typingIndicator.classList.remove('show');
        }
    }
    
    scrollToBottom() {
        if (!this.chatMessages) {
            return;
        }
        setTimeout(() => {
            if (this.chatMessages && typeof this.chatMessages.scrollTop !== 'undefined') {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }
        }, 100);
    }
    
        playSound(frequency = 400, duration = 100, type = 'sine') {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = type;
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration / 1000);
        } catch (e) {
            // Silenciosamente falha se áudio não estiver disponível
            console.log('Áudio não disponível');
        }
    }

    toggleSidebar() {
        console.log('🔍 [SIDEBAR] toggleSidebar chamado');
        console.log('🔍 [SIDEBAR] sidebar existe:', !!this.sidebar);
        console.log('🔍 [SIDEBAR] userId atual:', this.userId);
        
        if (!this.sidebar || !this.sidebar.classList) {
            console.error('❌ [SIDEBAR] Sidebar não encontrado ou sem classList');
            return;
        }
        
        // Verifica estado atual pela posição real, não apenas pela classe
        const rect = this.sidebar.getBoundingClientRect();
        const isActuallyOpen = rect.x >= 0;
        
        console.log('🔍 [SIDEBAR] Estado pela classe:', this.sidebar.classList.contains('open') ? 'ABERTO' : 'FECHADO');
        console.log('🔍 [SIDEBAR] Estado pela posição (x):', isActuallyOpen ? 'ABERTO' : 'FECHADO', `(x=${rect.x})`);
        
        // Se está fechado (x < 0), abre; se está aberto, fecha
        const isOpening = !isActuallyOpen;
        
        if (isOpening) {
            // FORÇA ABERTURA
            this.sidebar.classList.add('open');
            this.sidebar.style.transform = 'translateX(0)';
            setTimeout(() => {
                this.sidebar.style.removeProperty('transform'); // Remove inline style para usar CSS
            }, 10);
            console.log('✅ [SIDEBAR] ABRINDO - Classe "open" adicionada');
        } else {
            // FORÇA FECHAMENTO
            this.sidebar.classList.remove('open');
            this.sidebar.style.transform = 'translateX(-100%)';
            setTimeout(() => {
                this.sidebar.style.removeProperty('transform'); // Remove inline style para usar CSS
            }, 10);
            console.log('✅ [SIDEBAR] FECHANDO - Classe "open" removida');
        }
        
        // Adiciona/remove classe no body para controlar overlay no mobile
        if (document.body && document.body.classList) {
            if (isOpening) {
                document.body.classList.add('sidebar-open');
                console.log('✅ [SIDEBAR] Classe sidebar-open adicionada ao body');
                this.playSound(500, 150, 'sine'); // Som suave ao abrir
            } else {
                document.body.classList.remove('sidebar-open');
                console.log('✅ [SIDEBAR] Classe sidebar-open removida do body');
                this.playSound(300, 100, 'sine'); // Som mais baixo ao fechar
            }
        }
        
        // Verifica estado final
        setTimeout(() => {
            const finalRect = this.sidebar.getBoundingClientRect();
            const finalIsOpen = finalRect.x >= 0;
            console.log('🔍 [SIDEBAR] Estado final:', finalIsOpen ? 'ABERTO' : 'FECHADO', `(x=${finalRect.x})`);
            console.log('🔍 [SIDEBAR] Classe "open" presente:', this.sidebar.classList.contains('open'));
            console.log('🔍 [SIDEBAR] Computed transform:', window.getComputedStyle(this.sidebar).transform);
        }, 100);
    }

    closeSidebarMenu() {
        if (!this.sidebar || !this.sidebar.classList) {
            return;
        }
        
        if (this.sidebar.classList.contains('open')) {
            this.sidebar.classList.remove('open');
            if (document.body && document.body.classList) {
                document.body.classList.remove('sidebar-open'); // Remove classe do body
            }
            this.playSound(300, 100, 'sine'); // Som ao fechar
        }
    }

        initRotatingMessage() {
        const rotatingText = document.getElementById('rotating-text');
        if (!rotatingText) return;

        const messages = [
            'Você não está sozinha. 💛',
            'Cada dia é um passo no seu recomeço. 🌱',
            'Você está fazendo um trabalho incrível. ✨',
            'É normal ter dúvidas. Você é humana. 💕',
            'Cada momento difícil é também um momento de crescimento. 🌸',
            'Você merece todo o carinho e cuidado. 🤱',
            'Não existe mãe perfeita, apenas mães que amam. 💝'
        ];

        let currentIndex = 0;

        setInterval(() => {
            // Verifica se o elemento ainda existe no DOM antes de acessar
            const currentElement = document.getElementById('rotating-text');
            if (!currentElement || !document.body.contains(currentElement)) {
                return; // Elemento foi removido, para o intervalo
            }

            try {
                currentElement.style.opacity = '0';
                setTimeout(() => {
                    // Verifica novamente dentro do timeout
                    const checkElement = document.getElementById('rotating-text');
                    if (!checkElement || !document.body.contains(checkElement)) {
                        return;
                    }
                    currentIndex = (currentIndex + 1) % messages.length;
                    checkElement.textContent = messages[currentIndex];
                    checkElement.style.opacity = '1';
                }, 500);
            } catch (error) {
                console.warn('Erro ao atualizar mensagem rotativa:', error);
            }
        }, 5000); // Muda a cada 5 segundos
    }

    initFeelingButtons() {
        const feelingButtons = document.querySelectorAll('.feeling-btn');
        const feelingResponses = {
            'cansada': 'Entendo que você está cansada. O puerpério é realmente exaustivo. Lembre-se de descansar quando possível e aceitar ajuda quando oferecida. Você está fazendo muito mais do que imagina! 💤',
            'feliz': 'Que alegria saber que você está se sentindo feliz! Aproveite esses momentos de alegria e celebre cada pequena vitória. Você merece sentir-se bem! 😊',
            'ansiosa': 'A ansiedade no puerpério é muito comum. Você não está sozinha nisso. Respirar fundo e focar no momento presente pode ajudar. Se a ansiedade persistir ou piorar, não hesite em buscar ajuda profissional. 🤗',
            'confusa': 'É totalmente normal se sentir confusa nessa fase. Há muitas mudanças acontecendo ao mesmo tempo. Tome um dia de cada vez e lembre-se: não há perguntas bobas. Estou aqui para ajudar! 💭',
            'triste': 'Sinto muito que você esteja se sentindo triste. Seus sentimentos são válidos e importantes. Se essa tristeza persistir ou interferir no seu dia a dia, considere buscar ajuda profissional. Você merece apoio. 💙',
            'gratidao': 'Que lindo sentir gratidão! Apreciar os momentos bons é muito importante. Guarde esses sentimentos para quando os dias estiverem mais difíceis. Você está criando memórias preciosas. 🙏'
        };

        feelingButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const feeling = btn.dataset.feeling;
                const response = feelingResponses[feeling];
                if (response) {
                    // Esconde welcome message e mostra chat
                    if (this.welcomeMessage) {
                        this.welcomeMessage.style.display = 'none';
                    }
                    if (this.chatMessages) {
                        this.chatMessages.classList.add('active');
                    }
                    // Mostra o input do chat (usa .input-area diretamente)
                    const inputArea = document.querySelector('.input-area');
                    if (inputArea && inputArea.style) {
                        inputArea.style.display = 'flex';
                    }
                    // Foca no input
                    if (this.messageInput) {
                        setTimeout(() => {
                            this.messageInput.focus();
                        }, 100);
                    }
                    // Botão "Voltar ao Menu" removido - usuário pode usar o menu lateral

                    // Adiciona mensagem do usuário
                    this.addMessage(`Estou me sentindo ${btn.textContent.trim()}`, 'user');
                    
                    // Adiciona resposta empática
                    setTimeout(() => {
                        this.addMessage(response, 'assistant');
                    }, 500);
                }
            });
        });
    }

    initSupportLinks() {
        const supportLinks = document.querySelectorAll('.support-link');
        
        supportLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const topic = link.dataset.topic;
                let message = '';

                switch(topic) {
                    case 'baby-blues-depressao':
                        message = 'O baby blues geralmente começa 2-3 dias após o parto e dura até 2 semanas. Quando os sintomas persistem por mais de 2 semanas, são muito intensos, ou incluem pensamentos de machucar a si mesma ou ao bebê, pode ser depressão pós-parto e é essencial buscar ajuda profissional imediatamente. Você não está sozinha e há tratamento eficaz. 💙';
                        break;
                    case 'pedir-ajuda':
                        message = 'Pedir ajuda não é sinal de fraqueza, é sinal de sabedoria e autocuidado. Você pode começar dizendo: "Preciso de ajuda" para alguém de confiança, buscar grupos de apoio, ou procurar um profissional de saúde mental. Lembre-se: cuidar de você também é cuidar do seu bebê. Existe ajuda e esperança. 🤗';
                        break;
                    case 'redes-apoio':
                        message = 'Redes de apoio podem incluir: família, amigos, grupos de mães, profissionais de saúde, psicólogos, psiquiatras, grupos online de puerpério, e linhas de ajuda. Você pode buscar no SUS, CAPS, ou ONGs focadas em saúde materna. Não hesite em pedir ajuda - você merece suporte! 💕';
                        break;
                }

                if (message) {
                    // Esconde welcome message e mostra chat
                    if (this.welcomeMessage) {
                        this.welcomeMessage.style.display = 'none';
                    }
                    if (this.chatMessages) {
                        this.chatMessages.classList.add('active');
                    }
                    // Mostra o input do chat (usa .input-area diretamente)
                    const inputArea = document.querySelector('.input-area');
                    if (inputArea && inputArea.style) {
                        inputArea.style.display = 'flex';
                    }
                    // Foca no input
                    if (this.messageInput) {
                        setTimeout(() => {
                            this.messageInput.focus();
                        }, 100);
                    }
                    // Botão "Voltar ao Menu" removido - usuário pode usar o menu lateral

                    // Adiciona mensagem do usuário
                    this.addMessage(link.textContent.trim(), 'user');
                    
                    // Adiciona resposta
                    setTimeout(() => {
                        this.addMessage(message, 'assistant');
                    }, 500);
                }
            });
        });
    }
    
    async loadChatHistory() {
        try {
            console.log(`🔍 [HISTORY] Carregando histórico para userId: ${this.userId}`);
            const response = await fetch(`/api/historico/${this.userId}`);
            const history = await response.json();
            
            console.log(`📋 [HISTORY] Histórico recebido: ${history.length} mensagens`);
            
            // IMPORTANTE: NÃO exibe o histórico na tela
            // O histórico é carregado apenas para que o backend possa usá-lo como contexto
            // A Sophia lembrará das conversas anteriores, mas a tela começa limpa
            
            // Limpa qualquer histórico visual que possa ter ficado
            if (this.chatMessages) {
                this.chatMessages.innerHTML = '';
                if (this.chatMessages.classList) {
                    this.chatMessages.classList.remove('active');
                }
            }
            if (this.welcomeMessage && this.welcomeMessage.style) {
                this.welcomeMessage.style.display = 'flex';
            }
            
            if (history.length > 0) {
                console.log(`✅ [HISTORY] Histórico carregado no backend (${history.length} mensagens) - NÃO exibido na tela para manter interface limpa`);
                // NÃO mostra mensagem automática - o usuário deve clicar no Menu Inicial para começar
                // A Sophia lembrará do histórico quando o usuário iniciar uma nova conversa
            } else {
                console.log(`ℹ️ [HISTORY] Nenhuma mensagem encontrada no histórico para userId: ${this.userId}`);
            }
            
            // SEMPRE garante que o Menu Inicial está visível ao recarregar
            // O usuário deve clicar para iniciar uma nova conversa
            this.backToWelcomeScreen();
        } catch (error) {
            console.error('❌ [HISTORY] Erro ao carregar histórico:', error);
            console.error('❌ [HISTORY] userId usado:', this.userId);
        }
    }
    
    async clearHistory() {
        if (confirm('Tem certeza de que deseja limpar todo o histórico de conversas?')) {
            try {
                // Limpa o histórico no backend
                const response = await fetch(`/api/historico/${this.userId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    console.log('✅ [HISTORY] Histórico limpo no backend');
                } else {
                    console.warn('⚠️ [HISTORY] Erro ao limpar histórico no backend');
                }
                
                // Limpa o frontend
                if (this.chatMessages) {
                    this.chatMessages.innerHTML = '';
                    if (this.chatMessages.classList) {
                        this.chatMessages.classList.remove('active');
                    }
                }
                if (this.welcomeMessage && this.welcomeMessage.style) {
                    this.welcomeMessage.style.display = 'flex';
                }
                
                // NÃO gera novo userId - mantém o mesmo para manter consistência
                // O histórico foi limpo, mas o userId permanece o mesmo
                
                alert('Histórico limpo com sucesso!');
            } catch (error) {
                console.error('Erro ao limpar histórico:', error);
                alert('Erro ao limpar histórico. Tente novamente.');
            }
        }
    }
    
    showAlert(alertas) {
        if (!this.alertMessage || !this.alertModal) {
            console.warn('Elementos de alerta não estão disponíveis');
            return;
        }
        
        if ('textContent' in this.alertMessage) {
            this.alertMessage.textContent = 
                `Detectamos palavras relacionadas a: ${alertas.join(', ')}. ` +
                'Se você está enfrentando algum problema de saúde, procure atendimento médico.';
        }
        
        if (this.alertModal.classList) {
            this.alertModal.classList.add('show');
        }
    }
    
    hideAlert() {
        if (!this.alertModal || !this.alertModal.classList) {
            return;
        }
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
        try {
            // Tenta encontrar o elemento se não foi inicializado
            if (!this.statusIndicator) {
                this.statusIndicator = document.getElementById('status-indicator');
            }

            // Se o elemento ainda não existe, não faz nada (usuário não está logado)
            if (!this.statusIndicator) {
                return; // Elemento não existe ainda (usuário não está logado)
            }

            // Verifica se document.body existe
            if (!document.body) {
                return;
            }

            // Verifica se o elemento ainda está no DOM (pode ter sido removido)
            try {
                if (!document.body.contains(this.statusIndicator)) {
                    this.statusIndicator = null;
                    return;
                }
            } catch (e) {
                // Se houver erro ao verificar, assume que o elemento não está mais no DOM
                this.statusIndicator = null;
                return;
            }

            // Verificação final antes de acessar propriedades
            // Verifica se statusIndicator ainda existe e é um elemento válido
            if (!this.statusIndicator ||
                !this.statusIndicator.nodeType ||
                this.statusIndicator.nodeType !== 1) {
                this.statusIndicator = null;
                return;
            }

            // Verifica se className existe antes de acessar
            if (!('className' in this.statusIndicator)) {
                console.warn('Status indicator não tem propriedade className');
                this.statusIndicator = null;
                return;
            }

            // Verifica novamente se o elemento ainda está no DOM antes de modificar
            try {
                if (!document.body.contains(this.statusIndicator)) {
                    this.statusIndicator = null;
                    return;
                }
            } catch (e) {
                this.statusIndicator = null;
                return;
            }

            // Atribuições individuais com try-catch separado para cada uma
            if (navigator.onLine) {
                try {
                    if (this.statusIndicator && this.statusIndicator.nodeType === 1 && 'className' in this.statusIndicator) {
                        this.statusIndicator.className = 'status-online';
                    }
                } catch (e) {
                    console.warn('Erro ao definir className online:', e);
                    this.statusIndicator = null;
                    return;
                }
                try {
                    if (this.statusIndicator && this.statusIndicator.nodeType === 1 && 'innerHTML' in this.statusIndicator) {
                        this.statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Online';
                    }
                } catch (e) {
                    console.warn('Erro ao definir innerHTML online:', e);
                    // Não retorna aqui, apenas loga o erro
                }
            } else {
                try {
                    if (this.statusIndicator && this.statusIndicator.nodeType === 1 && 'className' in this.statusIndicator) {
                        this.statusIndicator.className = 'status-offline';
                    }
                } catch (e) {
                    console.warn('Erro ao definir className offline:', e);
                    this.statusIndicator = null;
                    return;
                }
                try {
                    if (this.statusIndicator && this.statusIndicator.nodeType === 1 && 'innerHTML' in this.statusIndicator) {
                        this.statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Offline';
                    }
                } catch (e) {
                    console.warn('Erro ao definir innerHTML offline:', e);
                    // Não retorna aqui, apenas loga o erro
                }
            }
        } catch (error) {
            // Se houver erro geral, reseta a referência
            console.warn('Erro ao atualizar status de conexão:', error);
            this.statusIndicator = null;
        }
    }
    
    startChat() {
        // Esconde welcome message e mostra chat
        if (this.welcomeMessage) {
            this.welcomeMessage.style.display = 'none';
        }
        if (this.chatMessages) {
            this.chatMessages.classList.add('active');
        }
        // Mostra o input do chat
        const inputArea = document.querySelector('.input-area');
        if (inputArea && inputArea.style) {
            inputArea.style.display = 'flex';
        }
        // Foca no input
        if (this.messageInput) {
            setTimeout(() => {
                this.messageInput.focus();
            }, 100);
        }
        // Adiciona mensagem de boas-vindas da Sophia
        const welcomeMsg = "Oi! 🌸 Sou a Sophia! Estou aqui para te ajudar com qualquer dúvida sobre puerpério, gestação ou cuidados com o bebê. Como posso te ajudar hoje?";
        this.addMessage(welcomeMsg, 'assistant');
    }
    
        backToWelcomeScreen() {
        // Limpa as mensagens do chat
        if (this.chatMessages) {
            this.chatMessages.innerHTML = '';
            if (this.chatMessages.classList) {
                this.chatMessages.classList.remove('active');
            }
        }

        // Mostra a tela de boas-vindas
        if (this.welcomeMessage && this.welcomeMessage.style) {
            this.welcomeMessage.style.display = 'flex';
        }

        if (this.backToWelcome && this.backToWelcome.style) {
            this.backToWelcome.style.display = 'none';
        }

        // Oculta o input do chat quando volta ao menu inicial
        const inputArea = document.querySelector('.input-area');
        if (inputArea && inputArea.style) {
            inputArea.style.display = 'none';
        }
        
        // NÃO gera novo userId - mantém o mesmo para preservar histórico
        // O userId é persistente e mantém a memória da Sophia
        // this.userId = this.generateUserId(); // REMOVIDO - mantém userId persistente
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
        if (document.body && document.body.classList) {
            document.body.classList.add(`device-${deviceType}`);
        }
        
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
                if (document.body && document.body.className && document.body.classList) {
                    document.body.className = document.body.className.replace(/device-\w+/g, '');
                    document.body.classList.add(`device-${this.deviceType}`);
                }
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
                    if (document.body && document.body.className && document.body.classList) {
                        document.body.className = document.body.className.replace(/device-\w+/g, '');
                        document.body.classList.add(`device-${this.deviceType}`);
                    }
                    this.optimizeForDevice();
                }
            }, 250);
        });
    }
    
    optimizeMobilePortrait() {
        // Fecha sidebar automaticamente em mobile
        this.closeSidebarMenu();
        
        // Ajusta tamanho do input para touch
        if (this.messageInput && this.messageInput.style) {
            this.messageInput.style.fontSize = '16px'; // Previne zoom no iOS
        }
        
        // Otimiza scroll suave
        if (this.chatMessages && this.chatMessages.style) {
            this.chatMessages.style.scrollBehavior = 'smooth';
        }
    }
    
    optimizeMobileLandscape() {
        // Ajustes para landscape em mobile
        this.closeSidebarMenu();
    }
    
    optimizeTabletPortrait() {
        // Otimizações para tablet em portrait
        if (this.chatMessages && this.chatMessages.style) {
            this.chatMessages.style.scrollBehavior = 'smooth';
        }
    }
    
    optimizeTabletLandscape() {
        // Otimizações para tablet em landscape
        // Pode mostrar sidebar se necessário
    }
    
    optimizeDesktop() {
        // Otimizações para desktop
        if (this.chatMessages && this.chatMessages.style) {
            this.chatMessages.style.scrollBehavior = 'auto';
        }
    }
    
    // Auth functions
    showAuthModal() {
        this.authModal.classList.add('show');
        this.switchAuthTab('login');
        // Carrega email lembrado quando o modal é aberto
        const rememberedEmail = localStorage.getItem('remembered_email');
        if (rememberedEmail) {
            const emailInput = document.getElementById('login-email');
            if (emailInput) {
                emailInput.value = rememberedEmail;
                // Marca o checkbox como checked
                const rememberMeCheckbox = document.getElementById('remember-me');
                if (rememberMeCheckbox) {
                    rememberMeCheckbox.checked = true;
                }
                console.log('💾 [LOGIN MODAL] Email lembrado carregado:', rememberedEmail);
            }
        }
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
        const email = document.getElementById('login-email').value.trim().toLowerCase();
        const password = document.getElementById('login-password').value.trim(); // Remove espaços
        const rememberMe = document.getElementById('remember-me').checked;
        
        if (!email || !password) {
            alert('Por favor, preencha todos os campos! 💕');
            return;
        }
        
        console.log(`🔍 [LOGIN MODAL] Tentando login com email: ${email}, password length: ${password.length}, remember_me: ${rememberMe}`);
        
        // Salva email no localStorage se "Lembre-se de mim" estiver marcado
        if (rememberMe) {
            localStorage.setItem('remembered_email', email);
            console.log('💾 [LOGIN MODAL] Email salvo no localStorage');
        } else {
            localStorage.removeItem('remembered_email');
            console.log('🗑️ [LOGIN MODAL] Email removido do localStorage');
        }
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include',  // Importante para cookies de sessão (especialmente em mobile)
                body: JSON.stringify({email, password, remember_me: rememberMe})
            });
            
            const data = await response.json();
            console.log('🔍 [LOGIN MODAL] Resposta completa:', data);
            console.log('🔍 [LOGIN MODAL] Status HTTP:', response.status);
            console.log('🔍 [LOGIN MODAL] response.ok:', response.ok);
            
            // Se houver erro específico de email não verificado, mostra mensagem mais clara
            if (data.erro && data.mensagem && data.pode_login === false) {
                const userEmail = data.email || email;
                const resend = confirm(`⚠️ ${data.mensagem}\n\nDeseja que eu reenvie o email de verificação agora?`);
                if (resend) {
                    this.resendVerificationEmail(userEmail);
                }
                return;
            }
            
            if (response.ok && (data.sucesso === true || data.user)) {
                console.log('✅ [LOGIN MODAL] Login bem-sucedido');
                this.userLoggedIn = true;
                this.currentUserName = data.user ? data.user.name : email;
                
                // Atualiza mensagem de boas-vindas
                this.updateWelcomeMessage(this.currentUserName);
                
                alert('🎉 ' + (data.mensagem || 'Login realizado com sucesso!'));
                this.hideAuthModal();
                
                // Pequeno delay para garantir que a sessão está criada antes de recarregar
                setTimeout(() => {
                    window.location.reload();
                }, 100);
            } else {
                console.error('❌ [LOGIN MODAL] Erro no login:', data.erro);
                alert('⚠️ ' + (data.erro || 'Email ou senha incorretos'));
            }
        } catch (error) {
            console.error('❌ [LOGIN MODAL] Erro na requisição:', error);
            alert('❌ Erro ao fazer login. Verifique sua conexão e tente novamente.');
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
        
        // Adiciona aviso médico no TOPO (antes de tudo)
        let html = `<div class="alerta-medico-guia" style="background: #fff3cd; border: 2px solid #ffc107; padding: 1.2rem; margin-bottom: 1.5rem; border-radius: 8px; text-align: center;">
            <p style="margin: 0; color: #856404; font-size: 0.95rem; line-height: 1.6; font-weight: 600;">
                <i class="fas fa-exclamation-triangle"></i> <strong>⚕️ AVISO IMPORTANTE:</strong><br>
                As informações fornecidas pela Sophia têm caráter educativo e de apoio. 
                <strong>Qualquer tipo de prescrição de medicamentos, suplementos, exercícios e outros procedimentos deve ser indicada e orientada por um profissional de saúde qualificado.</strong> 
                Procure orientação médica ou de enfermagem antes de usar qualquer medicamento, suplemento ou vitamina. 
                Medicamentos, pomadas, suplementos, exames e procedimentos médicos requerem prescrição profissional.<br><br>
                <strong>🚨 Em emergências, ligue imediatamente para 192 (SAMU).</strong>
            </p>
        </div>`;
        
        html += `<p style="color: #666; margin-bottom: 1.5rem;">${guia.descricao}</p>`;
        
        if (guia.causas) {
            html += `<div class="alerta-importante"><strong>Causas:</strong> ${guia.causas}</div>`;
        }
        
        if (guia.importante) {
            html += `<div class="alerta-importante"><strong>⚠️ IMPORTANTE:</strong> ${guia.importante}</div>`;
        }
        
        guia.passos.forEach(passo => {
                        // Valida e formata a URL da imagem corretamente
            let imagemHTML = '';
            if (passo.imagem) {
                try {
                    let imagemUrl = passo.imagem.trim();
                    if (imagemUrl) {
                        // Se a URL não começa com protocolo, adiciona https://
                        if (!imagemUrl.startsWith('http://') && !imagemUrl.startsWith('https://')) {
                            // Verifica se parece ser uma URL válida (contém domínio)
                            if (imagemUrl.includes('.') || imagemUrl.startsWith('//')) {
                                // Se começa com //, adiciona https:
                                if (imagemUrl.startsWith('//')) {
                                    imagemUrl = 'https:' + imagemUrl;
                                } else {
                                    // Adiciona https:// no início
                                    imagemUrl = 'https://' + imagemUrl;
                                }
                            } else {
                                // URL inválida, ignora
                                console.warn('URL de imagem inválida (sem domínio):', passo.imagem);
                                imagemUrl = null;
                            }
                        }
                        
                        // Se a URL for válida, renderiza a imagem
                        if (imagemUrl) {
                            // Usa encodeURI para garantir que a URL está corretamente formatada
                            imagemUrl = encodeURI(imagemUrl);
                            imagemHTML = `<img src="${imagemUrl}" alt="${passo.titulo}" class="passo-imagem" onerror="this.style.display='none';" loading="lazy">`;
                        }
                    }
                } catch (e) {
                    console.warn('Erro ao processar URL da imagem:', passo.imagem, e);
                    // Ignora imagens inválidas silenciosamente
                }
            }
            
            // Constrói informações técnicas se disponíveis
            let infoTecnicaHTML = '';
            if (passo.forca || passo.profundidade || passo.tecnica || passo.velocidade || passo.localizacao) {
                infoTecnicaHTML = '<div class="passo-info-tecnica">';
                
                if (passo.forca && passo.forca_nivel) {
                    const forcaPorcentagem = (passo.forca_nivel / 10) * 100;
                    infoTecnicaHTML += `
                        <div class="info-forca">
                            <span class="info-label">💪 Força:</span>
                            <span class="info-valor">${passo.forca}</span>
                            <div class="forca-bar">
                                <div class="forca-fill" style="width: ${forcaPorcentagem}%;"></div>
                            </div>
                            <span class="forca-nivel">Nível ${passo.forca_nivel}/10</span>
                        </div>
                    `;
                }
                
                if (passo.profundidade) {
                    infoTecnicaHTML += `
                        <div class="info-item">
                            <span class="info-label">📏 Profundidade:</span>
                            <span class="info-valor">${passo.profundidade}</span>
                        </div>
                    `;
                }
                
                if (passo.tecnica) {
                    infoTecnicaHTML += `
                        <div class="info-item">
                            <span class="info-label">✋ Técnica:</span>
                            <span class="info-valor">${passo.tecnica}</span>
                        </div>
                    `;
                }
                
                if (passo.localizacao) {
                    infoTecnicaHTML += `
                        <div class="info-item">
                            <span class="info-label">📍 Localização:</span>
                            <span class="info-valor">${passo.localizacao}</span>
                        </div>
                    `;
                }
                
                if (passo.velocidade) {
                    infoTecnicaHTML += `
                        <div class="info-item">
                            <span class="info-label">⚡ Velocidade:</span>
                            <span class="info-valor">${passo.velocidade}</span>
                        </div>
                    `;
                }
                
                if (passo.ritmo) {
                    infoTecnicaHTML += `
                        <div class="info-item">
                            <span class="info-label">🎵 Ritmo:</span>
                            <span class="info-valor">${passo.ritmo}</span>
                        </div>
                    `;
                }
                
                if (passo.detalhes) {
                    infoTecnicaHTML += `
                        <div class="info-detalhes">
                            <span class="info-label">📝 Detalhes:</span>
                            <p class="info-valor">${passo.detalhes}</p>
                        </div>
                    `;
                }
                
                // Temperatura
                if (passo.temperatura || passo.temperatura_ambiente) {
                    infoTecnicaHTML += `
                        <div class="info-temperatura">
                            <span class="info-label">🌡️ Temperatura:</span>
                            ${passo.temperatura ? `<span class="info-valor temperatura-destaque">${passo.temperatura}</span>` : ''}
                            ${passo.temperatura_ambiente ? `<div class="temperatura-ambiente">Ambiente: ${passo.temperatura_ambiente}</div>` : ''}
                            ${passo.como_testar ? `<div class="como-testar">${passo.como_testar}</div>` : ''}
                        </div>
                    `;
                }
                
                // Materiais necessários
                if (passo.materiais) {
                    let materiaisHTML = '';
                    if (Array.isArray(passo.materiais)) {
                        materiaisHTML = passo.materiais.map(item => `<li>${item}</li>`).join('');
                    } else {
                        materiaisHTML = `<p>${passo.materiais}</p>`;
                    }
                    infoTecnicaHTML += `
                        <div class="info-materiais">
                            <span class="info-label">📦 Materiais Necessários:</span>
                            ${Array.isArray(passo.materiais) ? `<ul class="materiais-lista">${materiaisHTML}</ul>` : materiaisHTML}
                        </div>
                    `;
                }
                
                // Ambiente/Segurança
                if (passo.ambiente || passo.seguranca) {
                    infoTecnicaHTML += `
                        <div class="info-seguranca">
                            <span class="info-label">🛡️ ${passo.ambiente ? 'Ambiente' : 'Segurança'}:</span>
                            ${passo.ambiente ? `<p class="info-valor">${passo.ambiente}</p>` : ''}
                            ${passo.seguranca ? `<p class="info-valor seguranca-destaque">${passo.seguranca}</p>` : ''}
                        </div>
                    `;
                }
                
                // Telefones úteis
                if (passo.telefones_uteis) {
                    infoTecnicaHTML += `
                        <div class="info-telefones">
                            <span class="info-label">📞 Telefones Úteis:</span>
                            <p class="info-valor telefones-destaque">${passo.telefones_uteis}</p>
                        </div>
                    `;
                }
                
                // Emergência
                if (passo.emergencia) {
                    infoTecnicaHTML += `
                        <div class="info-emergencia">
                            <span class="info-label">🚨 EMERGÊNCIA:</span>
                            <p class="info-valor emergencia-destaque">${passo.emergencia}</p>
                        </div>
                    `;
                }
                
                infoTecnicaHTML += '</div>';
            }
            
            html += `
                <div class="passo-card">
                    <span class="passo-numero">${passo.numero}</span>
                    <span class="passo-titulo">${passo.titulo}</span>
                    <p class="passo-descricao">${passo.descricao}</p>
                    ${imagemHTML}
                    ${infoTecnicaHTML}
                    <div class="passo-dica">💡 ${passo.dica}</div>
                    ${passo.aviso_medico ? `<div class="alerta-medico-passo" style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin-top: 1rem; border-radius: 8px;"><p style="margin: 0; color: #856404; font-size: 0.9rem; line-height: 1.6;">${passo.aviso_medico}</p></div>` : ''}
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
            
            // Adiciona aviso médico no TOPO (antes de tudo)
            let html = `<div class="alerta-medico-guia" style="background: #fff3cd; border: 2px solid #ffc107; padding: 1.2rem; margin-bottom: 1.5rem; border-radius: 8px; text-align: center;">
                <p style="margin: 0; color: #856404; font-size: 0.95rem; line-height: 1.6; font-weight: 600;">
                    <i class="fas fa-exclamation-triangle"></i> <strong>⚕️ AVISO IMPORTANTE:</strong><br>
                    As informações fornecidas pela Sophia têm caráter educativo e de apoio. 
                    <strong>Qualquer tipo de prescrição de medicamentos, suplementos, exercícios e outros procedimentos deve ser indicada e orientada por um profissional de saúde qualificado.</strong> 
                    Procure orientação médica ou de enfermagem antes de usar qualquer medicamento, suplemento ou vitamina. 
                    Medicamentos, suplementos, exames e procedimentos médicos requerem prescrição profissional.<br><br>
                    <strong>🚨 Em caso de dor intensa, sangramento, febre alta, inchaço repentino ou outros sintomas preocupantes, procure imediatamente um hospital com emergência obstétrica, onde há equipe especializada para gestantes.</strong>
                </p>
            </div>`;
            
            for (const [key, trimestre] of Object.entries(gestacao)) {
                html += `
                    <div class="trimestre-card">
                        <h4>${trimestre.nome}</h4>
                        <p style="margin-bottom: 0.5rem; color: #666;"><strong>${trimestre.semanas}</strong> - ${trimestre.descricao}</p>
                        ${trimestre.cuidados ? trimestre.cuidados.map(cuidado => `
                            <div class="semana-item">✅ ${cuidado}</div>
                        `).join('') : ''}
                        ${trimestre.desenvolvimento_bebe ? `<div style="margin-top: 1rem; padding: 0.8rem; background: #e8f5e9; border-radius: 8px;"><strong>👶 Desenvolvimento do bebê:</strong><br>${trimestre.desenvolvimento_bebe}</div>` : ''}
                        ${trimestre.informacao_ultrassonografia ? `<div style="margin-top: 1rem; padding: 0.8rem; background: #e3f2fd; border-left: 4px solid #2196F3; border-radius: 8px;"><strong>📊 Informação sobre Ultrassonografia:</strong><br>${trimestre.informacao_ultrassonografia}</div>` : ''}
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
            
            // Adiciona aviso médico no TOPO (antes de tudo)
            let html = `<div class="alerta-medico-guia" style="background: #fff3cd; border: 2px solid #ffc107; padding: 1.2rem; margin-bottom: 1.5rem; border-radius: 8px; text-align: center;">
                <p style="margin: 0; color: #856404; font-size: 0.95rem; line-height: 1.6; font-weight: 600;">
                    <i class="fas fa-exclamation-triangle"></i> <strong>⚕️ AVISO IMPORTANTE:</strong><br>
                    As informações fornecidas pela Sophia têm caráter educativo e de apoio. 
                    <strong>Qualquer tipo de prescrição de medicamentos, suplementos, exercícios e outros procedimentos deve ser indicada e orientada por um profissional de saúde qualificado.</strong> 
                    Procure orientação médica ou de enfermagem antes de usar qualquer medicamento, suplemento ou vitamina. 
                    Curativos, avaliações de cicatriz, medicações, diagnóstico de depressão pós-parto e outros procedimentos requerem acompanhamento profissional.<br><br>
                    <strong>🚨 Em caso de dor intensa, sangramento excessivo, febre alta, inchaço repentino ou outros sintomas preocupantes, procure imediatamente um hospital com emergência obstétrica, onde há equipe especializada para puérperas e recém-nascidos.</strong>
                </p>
            </div>`;
            
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
            
            // Adiciona aviso médico fixo no rodapé
            html += `<div class="alerta-medico-rodape" style="background: #fff3cd; border: 2px solid #ffc107; padding: 1.2rem; margin-top: 2rem; border-radius: 8px; text-align: center;">
                <p style="margin: 0; color: #856404; font-size: 0.95rem; line-height: 1.6; font-weight: 600;">
                    <i class="fas fa-exclamation-triangle"></i> <strong>⚕️ AVISO IMPORTANTE:</strong><br>
                    As informações fornecidas pela Sophia têm caráter educativo e de apoio. 
                    <strong>Todas as vacinas devem ser prescritas e administradas por profissional de saúde qualificado.</strong> 
                    Consulte sempre seu médico ou posto de saúde antes de tomar qualquer vacina.
                </p>
            </div>`;
            
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
                // Passa os dados para a comemoração personalizada
                this.showCelebration(data.tipo, data.baby_name, data.user_name);
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
    
    showCelebration(tipo = 'mae', babyName = null, userName = null) {
        const user = userName || this.currentUserName || 'Mamãe';
        const celebration = document.createElement('div');
        celebration.className = 'celebration-overlay';
        
        let messageHTML = '';
        
        if (tipo === 'bebe' && babyName) {
            // Comemoração para vacina do bebê com nome
            messageHTML = `
                <div class="celebration-content">
                    <div class="confetti-container"></div>
                    <div class="celebration-emoji">🎉👶</div>
                    <h2>Parabéns, ${babyName}! 🎉</h2>
                    <p>Você está protegido! 💪</p>
                    <p style="font-size: 0.9em; margin-top: 1rem;">E parabéns para você também, ${user}! 💕</p>
                    <p style="font-size: 0.85em; margin-top: 0.5rem; color: #8b5a5a;">Vocês estão cuidando da saúde juntos! 🤱</p>
                </div>
            `;
        } else if (tipo === 'bebe') {
            // Comemoração para vacina do bebê sem nome cadastrado
            messageHTML = `
                <div class="celebration-content">
                    <div class="confetti-container"></div>
                    <div class="celebration-emoji">🎉👶</div>
                    <h2>Parabéns para o bebê! 🎉</h2>
                    <p>Mais uma proteção! 💪</p>
                    <p style="font-size: 0.9em; margin-top: 1rem;">E parabéns para você também, ${user}! 💕</p>
                    <p style="font-size: 0.85em; margin-top: 0.5rem; color: #8b5a5a;">Vocês estão cuidando da saúde juntos! 🤱</p>
                </div>
            `;
        } else {
            // Comemoração para vacina da mãe
            messageHTML = `
                <div class="celebration-content">
                    <div class="confetti-container"></div>
                    <div class="celebration-emoji">🎉</div>
                    <h2>Parabéns, ${user}! 🎉</h2>
                    <p>Você cuidou da saúde!</p>
                    <p style="font-size: 0.9em; margin-top: 1rem;">Obrigada por se proteger 💕</p>
                </div>
            `;
        }
        
        celebration.innerHTML = messageHTML;
        document.body.appendChild(celebration);
        
        // Create confetti
        this.createConfetti();
        
        setTimeout(() => {
            celebration.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            if (celebration) {
                celebration.classList.remove('show');
                setTimeout(() => {
                    this.safeRemoveElement(celebration);
                }, 500);
            }
        }, 3000);
    }
    
    createConfetti() {
        const colors = ['#f4a6a6', '#e8b4b8', '#ffd89b', '#ff92a4', '#a8e6cf', '#ffaaa5'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.left = Math.random() * 100 + '%';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.animationDelay = Math.random() * 0.5 + 's';
                confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
                confetti.style.transform = 'rotate(' + Math.random() * 360 + 'deg)';
                document.body.appendChild(confetti);
                
                setTimeout(() => {
                    this.safeRemoveElement(confetti);
                }, 3000);
            }, i * 30);
        }
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
    
        // Verifica status da conexão periodicamente (apenas se já estiver logado)
    setInterval(() => {
        try {
            // Verifica se o chatbot existe e está logado
            if (!chatbot || !chatbot.userLoggedIn) {
                return;
            }
            // Verifica se o elemento ainda existe no DOM antes de chamar
            if (!chatbot.statusIndicator) {
                chatbot.statusIndicator = document.getElementById('status-indicator');
            }
            if (chatbot.statusIndicator && document.body && document.body.contains(chatbot.statusIndicator)) {
                chatbot.checkConnectionStatus();
            } else {
                // Se o elemento não existe, limpa a referência
                chatbot.statusIndicator = null;
            }
        } catch (error) {
            console.warn('Erro no setInterval de checkConnectionStatus:', error);
        }
    }, 5000);

    // Verifica status inicial apenas se estiver logado
    if (chatbot.userLoggedIn) {
        try {
            chatbot.checkConnectionStatus();
        } catch (error) {
            console.warn('Erro ao verificar status inicial:', error);
        }
    }

    // Adiciona evento de online/offline
    window.addEventListener('online', () => {
        try {
            if (chatbot && chatbot.userLoggedIn) {
                // Verifica se o elemento existe antes de chamar
                if (!chatbot.statusIndicator) {
                    chatbot.statusIndicator = document.getElementById('status-indicator');
                }
                if (chatbot.statusIndicator && document.body && document.body.contains(chatbot.statusIndicator)) {
                    chatbot.checkConnectionStatus();
                }
            }
        } catch (error) {
            console.warn('Erro no evento online:', error);
        }
    });
    window.addEventListener('offline', () => {
        try {
            if (chatbot && chatbot.userLoggedIn) {
                // Verifica se o elemento existe antes de chamar
                if (!chatbot.statusIndicator) {
                    chatbot.statusIndicator = document.getElementById('status-indicator');
                }
                if (chatbot.statusIndicator && document.body && document.body.contains(chatbot.statusIndicator)) {
                    chatbot.checkConnectionStatus();
                }
            }
        } catch (error) {
            console.warn('Erro no evento offline:', error);
        }
    });
    
    // Foca no input quando a página carrega (apenas se não estiver na tela de login)
    const messageInput = document.getElementById('message-input');
    if (messageInput && chatbot.userLoggedIn) {
        messageInput.focus();
    }

    // Inicializa o carrossel de features
    initFeatureCarousel();
});

/**
 * Inicializa o carrossel de botões de recursos
 * Carrossel horizontal com 4 botões que desliza horizontalmente
 */
function initFeatureCarousel() {
    const track = document.getElementById('feature-carousel-track');
    const prevBtn = document.getElementById('feature-carousel-prev');
    const nextBtn = document.getElementById('feature-carousel-next');
    const dotsContainer = document.getElementById('feature-carousel-dots');
    
    if (!track || !prevBtn || !nextBtn || !dotsContainer) {
        return; // Elementos não existem ainda
    }

    const buttons = track.querySelectorAll('.feature-btn');
    if (buttons.length === 0) {
        return;
    }

    let currentIndex = 0;
    let itemsPerView = calculateItemsPerView();

    // Calcula quantos itens mostrar por vez baseado no tamanho da tela
    function calculateItemsPerView() {
        const width = window.innerWidth;
        if (width <= 479) return 1;      // Mobile pequeno: 1 item
        if (width <= 767) return 2;      // Mobile médio/tablet: 2 itens
        if (width <= 1024) return 3;     // Tablet grande/desktop pequeno: 3 itens
        return 4;                        // Desktop: 4 itens (todos)
    }

    // Calcula quantos slides são necessários
    function calculateTotalSlides() {
        const items = calculateItemsPerView();
        if (items >= buttons.length) return 0; // Não precisa de carrossel se todos cabem
        return Math.ceil(buttons.length / items); // Número de slides necessários
    }

    // Cria ou atualiza os dots dinamicamente
    function createDots() {
        const totalSlides = calculateTotalSlides();
        
        // Se todos os botões cabem na tela, esconde os dots e botões de navegação
        if (totalSlides === 0) {
            dotsContainer.style.display = 'none';
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
            track.style.transform = 'translateX(0)'; // Reseta posição
            return;
        }

        // Mostra os controles
        dotsContainer.style.display = 'flex';
        prevBtn.style.display = 'flex';
        nextBtn.style.display = 'flex';

        // Remove dots antigos
        dotsContainer.innerHTML = '';

        // Cria novos dots baseado no número de slides necessários
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('span');
            dot.className = 'dot';
            if (i === 0) dot.classList.add('active');
            dot.setAttribute('data-index', i);
            dot.addEventListener('click', () => goToSlide(i));
            dotsContainer.appendChild(dot);
        }
    }

    // Atualiza o carrossel
    function updateCarousel() {
        itemsPerView = calculateItemsPerView();
        const totalSlides = calculateTotalSlides();
        
        // Se não precisa de carrossel, reseta tudo
        if (totalSlides === 0) {
            track.style.transform = 'translateX(0)';
            updateButtons();
            createDots();
            return;
        }

        // Aguarda o próximo frame para garantir que os tamanhos estão atualizados
        requestAnimationFrame(() => {
            const firstButton = track.querySelector('.feature-btn');
            if (!firstButton) return;
            
            // Obtém a largura real do botão incluindo gap
            const buttonWidth = firstButton.offsetWidth;
            const gap = parseFloat(window.getComputedStyle(track).gap) || 16;
            
            // Calcula o translateX baseado no índice
            // Desliza um "conjunto" de botões por vez (baseado em itemsPerView)
            // Cada slide move itemsPerView botões de uma vez
            const translateX = -(currentIndex * itemsPerView * (buttonWidth + gap));
            
            track.style.transform = `translateX(${translateX}px)`;
            updateButtons();
            updateDots();
        });
    }

    // Atualiza estado dos botões prev/next
    function updateButtons() {
        const totalSlides = calculateTotalSlides();
        if (totalSlides === 0) {
            prevBtn.disabled = true;
            nextBtn.disabled = true;
            return;
        }
        
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex >= totalSlides - 1;
    }

    // Atualiza os dots
    function updateDots() {
        const dots = dotsContainer.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });
    }

    // Vai para o próximo slide
    function nextSlide() {
        const totalSlides = calculateTotalSlides();
        if (totalSlides === 0) return;
        
        if (currentIndex < totalSlides - 1) {
            currentIndex++;
            updateCarousel();
        }
    }

    // Vai para o slide anterior
    function prevSlide() {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    }

    // Vai para um slide específico
    function goToSlide(index) {
        const totalSlides = calculateTotalSlides();
        if (totalSlides === 0) return;
        
        if (index >= 0 && index < totalSlides) {
            currentIndex = index;
            updateCarousel();
        }
    }

    // Event listeners
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);

    // Redimensionamento da janela
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const newItemsPerView = calculateItemsPerView();
            const newTotalSlides = calculateTotalSlides();
            
            if (newItemsPerView !== itemsPerView || newTotalSlides !== calculateTotalSlides()) {
                // Ajusta o índice atual se necessário
                if (newTotalSlides > 0 && currentIndex >= newTotalSlides) {
                    currentIndex = newTotalSlides - 1;
                } else if (newTotalSlides === 0) {
                    currentIndex = 0;
                }
                
                createDots();
                updateCarousel();
            }
        }, 250);
    });

    // Inicializa
    createDots();
    updateCarousel();
}

