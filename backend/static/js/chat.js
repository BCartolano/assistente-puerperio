// DEBUG_MODE global - controla debug visual em desenvolvimento
// Para desabilitar debug, definir: window.DEBUG_MODE = false antes de carregar este arquivo
// Por padrão, DESATIVADO para produção (Beta Fechado)
const DEBUG_MODE = window.DEBUG_MODE !== undefined ? window.DEBUG_MODE : false; // false = desativado para produção
window.DEBUG_MODE = DEBUG_MODE;

class ChatbotPuerperio {
    constructor() {
        // Modo de desenvolvimento (detecta localhost ou variável de ambiente)
        // IMPORTANTE: Definir ANTES de qualquer método que use this.log
        this.isDevelopment = window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1' ||
                           window.location.hostname.includes('.local') ||
                           window.DEBUG_MODE === true;
        
        // Wrapper para console logs - apenas em desenvolvimento
        // IMPORTANTE: Definir ANTES de chamar generateUserId()
        this.log = (...args) => {
            if (this.isDevelopment) {
                console.log(...args);
            }
        };
        this.warn = (...args) => {
            if (this.isDevelopment) {
                console.warn(...args);
            }
        };
        this.error = (...args) => {
            // Erros sempre logam, mas podem ser silenciados em produção se necessário
            if (this.isDevelopment) {
                console.error(...args);
            }
        };
        
        // Função de sanitização HTML básica
        this.sanitizeHTML = (str) => {
            if (!str) return '';
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        };
        
        // Agora pode chamar generateUserId() que usa this.log
        this.userId = this.generateUserId();
        
        // Função auxiliar para remover elementos de forma segura
        this.safeRemoveElement = (element) => {
            if (!element) return false;
            
            // Verifica se o elemento ainda está no DOM
            if (!element.parentNode) {
                this.warn('⚠️ [DOM] Elemento já foi removido do DOM');
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
                this.warn('⚠️ [DOM] Erro ao remover elemento:', e);
                // Última tentativa: verifica se ainda existe parentNode e tenta remover
                if (element.parentNode) {
                    try {
                        element.parentNode.removeChild(element);
                        return true;
                    } catch (e2) {
                        this.error('❌ [DOM] Erro crítico ao remover elemento:', e2);
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
        
        // Controle de debouncing e processamento de mensagens
        this.lastMessageTime = 0;
        this.minMessageInterval = 500; // 500ms entre mensagens
        this.isProcessing = false;
        
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
                        this.log('✅ [AUTH] Usuário já está logado:', user.name);
                        this.userLoggedIn = true;
                        this.currentUserName = user.name;
                        
                        // IMPORTANTE: Atualiza userId com o ID real do backend
                        if (user.id) {
                            this.userId = user.id;
                            this.log(`✅ [AUTH] userId atualizado para: ${this.userId}`);
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
                this.log('✅ [WELCOME] Botão antigo removido');
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
            this.log(`✅ [WELCOME] Mensagem atualizada: ${greeting}`);
        }
    }
    
    async initMainApp() {
        this.log('🚀 [INIT] initMainApp chamado');
        
        // Restaura histórico ao inicializar
        await this.restoreChatHistory();
        
        // Atualiza header do chat com contexto
        await this.updateChatHeader();
        
        // Verifica se é primeira visita e mostra mensagem de boas-vindas
        await this.showWelcomeMessageIfFirstVisit();
        const loginScreen = document.getElementById('login-screen');
        const mainContainer = document.getElementById('main-container');
        
        if (loginScreen) {
            loginScreen.classList.add('hidden');
            loginScreen.style.display = 'none';
            this.log('✅ [INIT] Tela de login ocultada');
        } else {
            this.error('❌ [INIT] Elemento login-screen não encontrado!');
        }
        
        if (mainContainer) {
            mainContainer.style.display = 'flex';
            mainContainer.classList.remove('hidden');
            this.log('✅ [INIT] Container principal exibido');
        } else {
            this.error('❌ [INIT] Elemento main-container não encontrado!');
        }
        
        // Mostra o footer quando o app é inicializado
        const footer = document.getElementById('app-footer');
        if (footer) {
            footer.style.display = 'block';
            this.log('✅ [INIT] Footer exibido');
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
              
              // Detecção de teclado virtual em mobile
              if (this.deviceType === 'mobile') {
                  this.detectKeyboard();
              }

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

                // Foca no input de mensagem se existir
                if (this.messageInput) {
                    setTimeout(() => {
                        this.messageInput.focus();
                    }, 300);
                }

                this.log('✅ [INIT] App inicializado com sucesso');
          } catch (error) {
              this.error('❌ [INIT] Erro ao inicializar app:', error);
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
        
        this.log('✅ [LOGIN] Tela de login exibida');
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
        
        // Login form submission - Previne submit padrão e adiciona handler no botão
        if (this.initialLoginForm) {
            // Previne submit padrão do formulário (Enter no input)
            this.initialLoginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleInitialLogin();
                return false;
            });
            
            // Handler no botão também (backup)
            const loginSubmitBtn = document.getElementById('initial-login-submit');
            if (loginSubmitBtn) {
                this.log('✅ [EVENTS] Event listener anexado ao botão de login');
                // Remove qualquer handler onclick existente para evitar duplicação
                loginSubmitBtn.onclick = null;
                loginSubmitBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.log('🔍 [EVENTS] Botão de login clicado, chamando handleInitialLogin...');
                    this.handleInitialLogin();
                    return false;
                });
            } else {
                this.error('❌ [EVENTS] Botão initial-login-submit não encontrado!');
            }
        }
        
        // Register form submission - Previne submit padrão e adiciona handler no botão
        if (this.initialRegisterForm) {
            // Previne submit padrão do formulário (Enter no input)
            this.initialRegisterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleInitialRegister();
                return false;
            });
            
            // Handler no botão também (backup)
            const registerSubmitBtn = document.getElementById('initial-register-submit');
            if (registerSubmitBtn) {
                registerSubmitBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.handleInitialRegister();
                    return false;
                });
            }
        }
        
        // Forgot password link
        const forgotPasswordLink = document.getElementById('forgot-password-link');
        if (forgotPasswordLink) {
            this.log('✅ [EVENTS] Event listener anexado ao link "Esqueci minha senha"');
            forgotPasswordLink.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.log('🔍 [EVENTS] Link "Esqueci minha senha" clicado, redirecionando...');
                this.handleForgotPassword();
                return false;
            });
        } else {
            this.warn('⚠️ [EVENTS] Link forgot-password-link não encontrado (pode não estar na página atual)');
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
            this.log('💾 [LOGIN] Email lembrado carregado:', rememberedEmail);
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
        // Log sempre (mesmo em produção) para debug
        console.log('🔍 [LOGIN] handleInitialLogin chamado');
        this.log('🔍 [LOGIN] handleInitialLogin chamado');
        
        const emailInput = document.getElementById('initial-login-email');
        const passwordInput = document.getElementById('initial-login-password');
        const rememberMeCheckbox = document.getElementById('initial-remember-me');
        
        if (!emailInput || !passwordInput) {
            this.error('❌ [LOGIN] Campos de email ou senha não encontrados!');
            alert('Erro: Campos de login não encontrados. Recarregue a página.');
            return;
        }
        
        const email = emailInput.value.trim().toLowerCase();
        const password = passwordInput.value.trim(); // Remove espaços
        const rememberMe = rememberMeCheckbox ? rememberMeCheckbox.checked : false;
        
        if (!email || !password) {
            alert('Por favor, preencha todos os campos! 💕');
            return;
        }
        
        this.log(`🔍 [LOGIN] Tentando login com email: ${email}, password length: ${password.length}, remember_me: ${rememberMe}`);
        
        // Salva email no localStorage se "Lembre-se de mim" estiver marcado
        if (rememberMe) {
            localStorage.setItem('remembered_email', email);
            this.log('💾 [LOGIN] Email salvo no localStorage');
        } else {
            localStorage.removeItem('remembered_email');
            this.log('🗑️ [LOGIN] Email removido do localStorage');
        }
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include',  // Importante para cookies de sessão
                body: JSON.stringify({email, password, remember_me: rememberMe})
            });
            
            const data = await response.json();
            this.log('🔍 [LOGIN] Resposta completa:', data);
            this.log('🔍 [LOGIN] Status HTTP:', response.status);
            this.log('🔍 [LOGIN] response.ok:', response.ok);
            this.log('🔍 [LOGIN] data.sucesso:', data.sucesso);
            this.log('🔍 [LOGIN] data.user:', data.user);
            
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
                this.log('✅ [LOGIN] Login bem-sucedido, inicializando app...');
                this.log('🔍 [LOGIN] Dados recebidos:', JSON.stringify(data));
                
                this.userLoggedIn = true;
                this.currentUserName = data.user ? data.user.name : email;
                
                // IMPORTANTE: Atualiza userId com o ID real do backend
                if (data.user && data.user.id) {
                    this.userId = data.user.id;
                    this.log(`✅ [LOGIN] userId atualizado para: ${this.userId}`);
                }
                
                // Atualiza mensagem de boas-vindas
                this.updateWelcomeMessage(this.currentUserName);
                
                // Mostra mensagem de boas-vindas se disponível
                if (data.mensagem) {
                    this.log('💕 Mensagem:', data.mensagem);
                }
                
                // IMPORTANTE: Esconde tela de login ANTES de chamar initMainApp
                const loginScreen = document.getElementById('login-screen');
                if (loginScreen) {
                    loginScreen.style.display = 'none';
                    loginScreen.classList.add('hidden');
                    this.log('✅ [LOGIN] Tela de login ocultada');
                }
                
                // Pequeno delay para garantir que a sessão está criada
                setTimeout(() => {
                    this.log('🚀 [LOGIN] Chamando initMainApp...');
                    try {
                        this.initMainApp();
                    } catch (error) {
                        this.error('❌ [LOGIN] Erro ao chamar initMainApp:', error);
                        // Tenta recarregar a página como fallback
                        window.location.reload();
                    }
                }, 200);
            } else {
                this.log('❌ [LOGIN] Login falhou ou resposta inválida');
                this.log('🔍 [LOGIN] Resposta completa:', JSON.stringify(data));
                this.log('🔍 [LOGIN] Status HTTP:', response.status);
                
                if (data.pode_login === false && data.mensagem) {
                    // Email não verificado
                    if (confirm(data.mensagem + '\n\nDeseja reenviar o email de verificação?')) {
                        await this.resendVerificationEmail(email);
                    }
                } else {
                    const errorMsg = data.erro || data.mensagem || 'Erro ao fazer login';
                    alert('⚠️ ' + errorMsg);
                    this.error('❌ [LOGIN] Erro detalhado:', data);
                }
            }
        } catch (error) {
            this.error('Erro ao fazer login:', error);
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
            this.error('Erro ao reenviar email:', error);
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
            this.error('Erro ao fazer logout:', error);
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
            
            this.log('[REGISTER] Enviando dados:', {
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
            
            this.log('[REGISTER] Status da resposta:', response.status);
            
            const data = await response.json();
            this.log('[REGISTER] Resposta do servidor:', data);
            
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
                this.error('[REGISTER] Erro:', errorMessage);
                this.showNotification(
                    'Erro no cadastro ⚠️',
                    errorMessage,
                    'error'
                );
            }
        } catch (error) {
            this.error('[REGISTER] Erro na requisição:', error);
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
            this.log('🆕 [USER_ID] Novo userId gerado e salvo:', userId);
        } else {
            this.log('✅ [USER_ID] userId recuperado do localStorage:', userId);
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
        this.log('🔍 [INIT] Elementos do sidebar:');
        this.log('🔍 [INIT] sidebar:', !!this.sidebar);
        this.log('🔍 [INIT] menuToggle:', !!this.menuToggle);
        this.log('🔍 [INIT] closeSidebar:', !!this.closeSidebar);
        this.clearHistoryBtn = document.getElementById('clear-history');
        this.categoriesContainer = document.getElementById('categories'); // Pode ser null se não existir no HTML
        
        // Sidebar new buttons
        this.sidebarBtnGuias = document.getElementById('sidebar-btn-guias');
        this.sidebarBtnGestacao = document.getElementById('sidebar-btn-gestacao');
        this.sidebarBtnPosparto = document.getElementById('sidebar-btn-posparto');
        this.sidebarBtnVacinas = document.getElementById('sidebar-btn-vacinas');
        this.sidebarBtnSintomas = document.getElementById('sidebar-btn-sintomas');
        this.sidebarBtnClear = document.getElementById('sidebar-btn-clear');
        this.sidebarBtnClearMemory = document.getElementById('sidebar-btn-clear-memory');
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
        
        // Chat header fixo (desktop)
        this.chatHeaderFixed = document.getElementById('chat-header-fixed');
        this.chatHeaderSubtitle = document.getElementById('chat-header-subtitle');
        
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

        // Profile modal
        this.profileModal = document.getElementById('profile-modal');
        this.closeProfileModalBtn = document.getElementById('close-profile-modal');
        this.profileForm = document.getElementById('profile-form');
        this.profileSaveBtn = document.getElementById('profile-save-btn');
        this.profileClearBtn = document.getElementById('profile-clear-btn');

        // Profile inputs
        this.profileInputs = {
            momName: document.getElementById('profile-mom-name'),
            momPhase: document.getElementById('profile-mom-phase'),
            momAllergies: document.getElementById('profile-mom-allergies'),
            momConditions: document.getElementById('profile-mom-conditions'),
            momContact: document.getElementById('profile-mom-contact'),
            babyName: document.getElementById('profile-baby-name'),
            babyBirth: document.getElementById('profile-baby-birth'),
            babyPediatrician: document.getElementById('profile-baby-pediatrician'),
            babyAllergies: document.getElementById('profile-baby-allergies'),
            babyVaccines: document.getElementById('profile-baby-vaccines'),
            docPlan: document.getElementById('profile-doc-plan'),
            docSus: document.getElementById('profile-doc-sus'),
            docExams: document.getElementById('profile-doc-exams'),
            docSupport: document.getElementById('profile-doc-support'),
            docEmergency: document.getElementById('profile-doc-emergency')
        };
        
        // Botão de iniciar conversa
        this.startChatBtn = document.getElementById('start-chat-btn');
        
        // Emergency numbers modal elements
        this.btnEmergencyNumbers = document.getElementById('btn-emergency-numbers');
        this.emergencyNumbersModal = document.getElementById('emergency-numbers-modal');
        this.closeEmergencyNumbers = document.getElementById('close-emergency-numbers');
        this.emergencyNumbersList = document.getElementById('emergency-numbers-list');
        this.btnFindHospitals = document.getElementById('btn-find-hospitals');
        
        // Hospitals modal elements
        this.hospitalsModal = document.getElementById('hospitals-modal');
        this.closeHospitals = document.getElementById('close-hospitals');
        this.hospitalsList = document.getElementById('hospitals-list');
        this.hospitalsLoading = document.getElementById('hospitals-loading');
        this.hospitalsError = document.getElementById('hospitals-error');
    }
    
        bindEvents() {
        // Envio de mensagem
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.handleSendClick());
        }
        
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendClick();
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
        this.sidebarBtnClearMemory?.addEventListener('click', () => {
            this.closeSidebarMenu();
            this.limparHistoricoTriagens();
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
            // Verifica se o clique foi no botão ou em um elemento dentro dele (como ícone)
            const quickBtn = e.target.closest('.quick-btn');
            if (quickBtn) {
                const question = quickBtn.dataset.question;
                if (this.messageInput && question) {
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
                    
                    // Footer CVV removido - código comentado
                    
                    // Define a pergunta e envia
                    this.messageInput.value = question;
                    this.handleSendClick();
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
        
        // Resources buttons (Hero Grid)
        this.btnGuias?.addEventListener('click', () => this.showGuias());
        this.btnGestacao?.addEventListener('click', () => this.showGestacao());
        this.btnPosparto?.addEventListener('click', () => this.showPosparto());
        this.btnVacinas?.addEventListener('click', () => this.showVacinas());
        
        // Header icons
        const headerSearchBtn = document.getElementById('header-search-btn');
        const headerProfileBtn = document.getElementById('header-profile-btn');
        
        if (headerSearchBtn) {
            headerSearchBtn.addEventListener('click', () => {
                // TODO: Implementar busca
                alert('Funcionalidade de busca em desenvolvimento');
            });
        }
        
        if (headerProfileBtn) {
            headerProfileBtn.addEventListener('click', () => {
                this.openProfileModal();
            });
        }

        if (this.closeProfileModalBtn) {
            this.closeProfileModalBtn.addEventListener('click', () => this.closeProfileModal());
        }

        if (this.profileModal) {
            this.profileModal.addEventListener('click', (e) => {
                if (e.target === this.profileModal) {
                    this.closeProfileModal();
                }
            });
        }

        if (this.profileSaveBtn) {
            this.profileSaveBtn.addEventListener('click', () => this.saveProfileData());
        }

        if (this.profileClearBtn) {
            this.profileClearBtn.addEventListener('click', () => this.clearProfileForm());
        }
        
        // Footer actions
        const footerFindHospitals = document.getElementById('footer-find-hospitals');
        const footerEmergencyNumbers = document.getElementById('footer-emergency-numbers');
        const footerClearHistory = document.getElementById('footer-clear-history');
        const footerClearMemory = document.getElementById('footer-clear-memory');
        
        if (footerFindHospitals) {
            footerFindHospitals.addEventListener('click', () => {
                this.closeSidebarMenu();
                this.findNearbyHospitals();
            });
        }
        
        if (footerEmergencyNumbers) {
            footerEmergencyNumbers.addEventListener('click', () => {
                this.closeSidebarMenu();
                this.openEmergencyNumbersModal();
            });
        }
        
        if (footerClearHistory) {
            footerClearHistory.addEventListener('click', () => {
                this.closeSidebarMenu();
                this.clearHistory();
            });
        }
        
        if (footerClearMemory) {
            footerClearMemory.addEventListener('click', () => {
                this.closeSidebarMenu();
                this.clearMemory();
            });
        }
        
        // Fechar resources modal
        this.closeResources?.addEventListener('click', () => this.hideResourcesModal());
        
        // Fechar resources modal clicando fora
        this.resourcesModal?.addEventListener('click', (e) => {
            if (e.target === this.resourcesModal) {
                this.hideResourcesModal();
            }
        });
        
        // Emergency numbers modal
        if (this.btnEmergencyNumbers) {
            this.btnEmergencyNumbers.addEventListener('click', () => this.openEmergencyNumbersModal());
        }
        if (this.closeEmergencyNumbers) {
            this.closeEmergencyNumbers.addEventListener('click', () => this.closeEmergencyNumbersModal());
        }
        
        if (this.emergencyNumbersModal) {
            this.emergencyNumbersModal.addEventListener('click', (e) => {
                if (e.target === this.emergencyNumbersModal) {
                    this.closeEmergencyNumbersModal();
                }
            });
        }
        if (this.btnFindHospitals) {
            this.btnFindHospitals.addEventListener('click', () => this.findNearbyHospitals());
        }
        
        // Hospitals modal
        if (this.closeHospitals) {
            this.closeHospitals.addEventListener('click', () => this.closeHospitalsModal());
        }
        if (this.hospitalsModal) {
            this.hospitalsModal.addEventListener('click', (e) => {
                if (e.target === this.hospitalsModal) {
                    this.closeHospitalsModal();
                }
            });
        }
        
        // Sintomas/Alerts button
        if (this.sidebarBtnSintomas) {
            this.sidebarBtnSintomas.addEventListener('click', () => {
                this.closeSidebarMenu();
                this.showSintomasTriagem();
            });
        }
        
        // ========================================
        // EVENT DELEGATION - PADRÃO OBRIGATÓRIO
        // ========================================
        // ⚠️ CRÍTICO: Sempre use event delegation para elementos dinâmicos
        // ✅ Isso garante que botões continuem funcionando mesmo se DOM for atualizado
        // 📚 Ver documentação: docs/style-guide-sophia.md
        // ========================================
        
        // Event delegation para botões de sintomas (dinâmicos)
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.sintoma-btn-yes, .sintoma-btn-no');
            if (btn) {
                const sintomaId = btn.getAttribute('data-sintoma-id');
                const resposta = btn.getAttribute('data-resposta');
                if (sintomaId && resposta) {
                    this.processarRespostaSintoma(sintomaId, resposta);
                }
            }
        });
        
        // Event delegation para botões de ação de sintomas (dinâmicos)
        document.addEventListener('click', (e) => {
            const acaoBtn = e.target.closest('.sintoma-acao-hospital, .sintoma-voltar-btn');
            if (acaoBtn && acaoBtn.onclick) {
                // onclick já está definido no HTML gerado
                return; // Deixa o onclick nativo funcionar
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
            this.error('Erro ao carregar categorias:', error);
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
            this.warn('categoriesContainer não encontrado');
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
    
    /**
     * Handler para clique no botão de enviar com debouncing
     */
    handleSendClick() {
        const now = Date.now();
        
        // Verifica debouncing - previne envio muito rápido
        if (now - this.lastMessageTime < this.minMessageInterval) {
            this.warn('⚠️ Aguarde um momento antes de enviar outra mensagem.');
            return;
        }
        
        // Previne múltiplas requisições simultâneas
        if (this.isProcessing) {
            this.warn('⚠️ Processando mensagem anterior. Aguarde...');
            return;
        }
        
        // Chama sendMessage
        this.sendMessage();
    }
    
    /**
     * Envia mensagem usando APIClient com todas as otimizações de resiliência
     */
    async sendMessage() {
        // Verifica se messageInput existe antes de usar
        if (!this.messageInput || !this.messageInput.value) {
            this.warn('messageInput não está disponível');
            return;
        }

        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Atualiza timestamp e marca como processando
        this.lastMessageTime = Date.now();
        this.isProcessing = true;

        // Marca que o usuário já interagiu (para mostrar mensagem de boas-vindas nas próximas vezes)
        localStorage.setItem(`sophia_has_interacted_${this.userId}`, 'true');

        // Adiciona mensagem do usuário
        await this.addMessage(message, 'user', {}, false); // Sem streaming para mensagens do usuário
        
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
        
        // Mostra header fixo do chat (desktop)
        if (this.chatHeaderFixed && window.innerWidth >= 1024) {
            this.chatHeaderFixed.style.display = 'block';
            this.updateChatHeader(); // Atualiza com informações contextuais
        }
        
        // Mostra o input do chat (usa .input-area diretamente)
        const inputArea = document.querySelector('.input-area');
        if (inputArea && inputArea.style) {
            inputArea.style.display = 'flex';
        }
        
        // Footer CVV removido - código comentado
        
        // Botão "Voltar ao Menu" removido - usuário pode usar o menu lateral

        // Mostra indicador de digitação
        this.showTyping();

        try {
            this.log('📤 Enviando mensagem:', message);
            
            // Verifica se apiClient está disponível
            if (!window.apiClient) {
                throw new Error('APIClient não está disponível. Verifique se api-client.js foi carregado.');
            }
            
            // Usa APIClient para requisição resiliente
            const data = await window.apiClient.post('/api/chat', {
                pergunta: message,
                user_id: this.userId,
                user_name: this.userName || 'Mamãe',
                baby_name: this.babyName || null
            }, {
                timeout: 30000, // 30 segundos
                retries: 3, // 3 tentativas
                priority: 'high', // Alta prioridade para mensagens de chat
                cancelPrevious: true // Cancela requisição anterior se houver
            });

            this.log('✅ Dados recebidos:', data);

            // Esconde indicador de digitação
            this.hideTyping();

            // Verifica se há uma resposta válida
            if (data.resposta) {
                // Verifica se há alerta de risco emocional/suicídio (mostrar aviso visual acolhedor)
                if (data.mostrar_aviso_visual && data.alerta_ativo) {
                    this.showAvisoVisualRisco(data.nivel_risco);
                } else if (!data.alerta_ativo) {
                    // Se não há alerta ativo, esconde o aviso visual (usuário pode ter dito que está bem)
                    this.hideAvisoVisualRisco();
                }
                
                // Adiciona resposta do assistente (com streaming)
                await this.addMessage(data.resposta, 'assistant', {
                    categoria: data.categoria,
                    alertas: data.alertas,
                    fonte: data.fonte,
                    alerta_ativo: data.alerta_ativo,
                    nivel_risco: data.nivel_risco,
                    contexto_tags: data.contexto_tags || []  // Tags de contexto do backend
                }, true); // true = usar streaming

                // Mostra alerta médico se necessário (alertas médicos normais)
                if (data.alertas && data.alertas.length > 0 && !data.alerta_ativo) {
                    this.showAlert(data.alertas);
                }
            } else {
                this.warn('⚠️ Resposta vazia recebida:', data);
                await this.addMessage(
                    'Desculpe, querida. Não consegui entender direito sua mensagem. Pode tentar reformular? Ou se preferir, me diga o que você está precisando e eu tento te ajudar da melhor forma que conseguir. Estou aqui para te apoiar! 💛',
                    'assistant',
                    {},
                    false // sem streaming para mensagens de erro
                );
            }

        } catch (error) {
            this.error('❌ Erro ao enviar mensagem:', error);
            this.hideTyping();
            
            // Mensagem de erro mais específica baseada no tipo de erro
            let errorMessage = 'Desculpe, ocorreu um erro ao processar sua pergunta.';
            let toastMessage = 'Ops, deu um probleminha! Tente novamente em alguns instantes. 💛';
            
            if (error.name === 'AbortError' || error.message.includes('cancelada')) {
                errorMessage = 'Requisição cancelada. Tente novamente.';
                toastMessage = 'Requisição cancelada. Tente novamente. 💛';
            } else if (error.message.includes('Timeout') || error.message.includes('timeout')) {
                errorMessage = 'Tempo de espera esgotado. O servidor está demorando para responder. Tente novamente.';
                toastMessage = 'A resposta está demorando um pouco mais que o normal. Aguarde mais um instante ou tente novamente. 💛';
            } else if (error.message.includes('HTTP 5') || error.response?.status === 500) {
                errorMessage = 'Erro no servidor. Tente novamente em alguns instantes.';
                toastMessage = 'Ops, deu um probleminha técnico do meu lado. Não se preocupe - não é culpa sua! Pode tentar novamente em alguns instantes? 💛';
            } else if (error.message.includes('rede') || error.message.includes('network')) {
                errorMessage = 'Erro de conexão. Verifique sua internet e tente novamente.';
                toastMessage = 'Parece que sua conexão está instável. Verifique sua internet e tente novamente. 💛';
            } else if (error.message.includes('APIClient')) {
                errorMessage = 'Erro na inicialização. Recarregue a página.';
                toastMessage = 'Algo deu errado na inicialização. Recarregue a página, por favor. 💛';
            }
            
            // Mostra toast notification acolhedor para erros (especialmente 500)
            if (window.toast && typeof window.toast.error === 'function') {
                window.toast.error(toastMessage, 6000); // 6 segundos de duração
            } else {
                // Fallback: mostra no console se toast não estiver disponível
                console.error('[TOAST] Toast notification não disponível:', toastMessage);
            }
            
            await this.addMessage(
                errorMessage.replace('Desculpe, ocorreu um erro', 'Opa, deu um probleminha aqui do meu lado 😅. Não se preocupe! Pode tentar novamente? Ou se quiser, me conte de outra forma o que você precisa e eu tento te ajudar. Você não está sozinha - estou aqui! 💛'),
                'assistant',
                {},
                false // sem streaming para mensagens de erro
            );
        } finally {
            // Reabilita o botão e input
            this.isProcessing = false;
            
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
    
    async addMessage(content, sender, metadata = {}, useStreaming = true) {
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

        // Verifica se chatMessages existe antes de adicionar mensagem
        if (!this.chatMessages) {
            this.warn('chatMessages não está disponível');
            return;
        }
        
        // Renderiza estrutura do message
        messageElement.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text"></div>
                ${categoryBadge}
                ${alertSection}
                <div class="message-time">${time}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageElement);
        
        // Seleciona elemento de texto para streaming
        const messageTextElement = messageElement.querySelector('.message-text');
        
        // Se for assistente e streaming habilitado, usa efeito máquina de escrever
        if (sender === 'assistant' && useStreaming && content.length > 20) {
            messageTextElement.classList.add('streaming');
            // Velocidade adaptativa: mais rápido em mobile para evitar sensação de lentidão no 4G
            const isMobile = window.innerWidth <= 1023;
            const streamingSpeed = isMobile ? 15 : 25; // 15ms no mobile, 25ms no desktop
            await this.typewriterEffect(messageTextElement, content, streamingSpeed);
            messageTextElement.classList.remove('streaming');
        } else {
            // Renderização normal (instantânea)
            messageTextElement.innerHTML = this.formatMessage(content);
        }
        
        // Salva no histórico após adicionar
        this.saveChatHistory();
        
        // Adiciona Quick Replies após resposta do assistente
        if (sender === 'assistant' && !metadata.alerta_ativo) {
            setTimeout(() => {
                this.showQuickReplies(content, metadata);
            }, 500);
        }
        
        this.scrollToBottom();
    }
    
    async typewriterEffect(element, text, speed = 25) {
        // Limpa elemento
        element.textContent = '';
        
        // Proteção: verifica se elemento ainda existe (evita race conditions)
        if (!element || !element.parentNode) {
            this.warn('⚠️ [STREAMING] Elemento removido durante streaming, abortando');
            return;
        }
        
        // Adiciona caractere por caractere (usa await para não "atropelar" DOM)
        for (let i = 0; i < text.length; i++) {
            // Verifica novamente se elemento ainda existe (proteção adicional)
            if (!element || !element.parentNode) {
                this.warn('⚠️ [STREAMING] Elemento removido durante streaming, abortando');
                break;
            }
            
            // Adiciona caractere (operação atômica)
            element.textContent += text[i];
            
            // Pausa entre caracteres (usa event loop, não bloqueia DOM)
            if (i < text.length - 1) {
                await new Promise(resolve => setTimeout(resolve, speed));
            }
            
            // Scroll automático suave durante digitação (a cada 10 caracteres ou ao final)
            // Usa requestAnimationFrame para melhor performance (se disponível)
            if (i % 10 === 0 || i === text.length - 1) {
                if (window.requestAnimationFrame) {
                    requestAnimationFrame(() => {
                        this.scrollToBottom(true); // true = scroll suave
                    });
                } else {
                    this.scrollToBottom(true); // Fallback para setTimeout
                }
            }
        }
    }
    
    formatMessage(content) {
        if (!content) return '';
        // Sanitiza o conteúdo primeiro para prevenir XSS
        const sanitized = this.sanitizeHTML(content);
        // Converte quebras de linha em HTML (seguro após sanitização)
        return sanitized.replace(/\n/g, '<br>');
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
    
    scrollToBottom(smooth = false) {
        if (!this.chatMessages) {
            return;
        }
        
        // Usa scroll suave durante streaming para melhor experiência
        const scrollBehavior = smooth ? 'smooth' : 'auto';
        this.chatMessages.style.scrollBehavior = scrollBehavior;
        
        setTimeout(() => {
            if (this.chatMessages && typeof this.chatMessages.scrollTop !== 'undefined') {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }
            // Restaura comportamento padrão após scroll
            if (smooth) {
                setTimeout(() => {
                    this.chatMessages.style.scrollBehavior = '';
                }, 300);
            }
        }, smooth ? 50 : 100);
    }
    
    // Salva histórico no localStorage (últimas 5 mensagens)
    saveChatHistory() {
        try {
            if (!this.chatMessages) return;
            
            const messages = Array.from(this.chatMessages.children)
                .filter(msg => msg.classList.contains('message'))
                .slice(-5) // Últimas 5 mensagens
                .map(msgEl => {
                    const sender = msgEl.classList.contains('user') ? 'user' : 'assistant';
                    const content = msgEl.querySelector('.message-text')?.textContent || '';
                    const time = msgEl.querySelector('.message-time')?.textContent || '';
                    const categoria = msgEl.querySelector('.message-category')?.textContent.replace('📁 ', '').trim() || null;
                    
                    return {
                        content: content,
                        sender: sender,
                        timestamp: new Date().toISOString(),
                        metadata: {
                            categoria: categoria
                        }
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
    
    // Carrega histórico do localStorage
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
    
    // Restaura histórico na tela
    async restoreChatHistory() {
        const history = this.loadChatHistory();
        
        if (history.length === 0) return;
        
        // Limpa mensagens atuais (se houver)
        if (this.chatMessages) {
            // Não limpa se já houver mensagens visíveis (evita duplicação)
            if (this.chatMessages.children.length === 0) {
                // Restaura mensagens (sem streaming, instantâneo)
                for (const msg of history) {
                    await this.addMessage(msg.content, msg.sender, msg.metadata || {}, false); // false = sem streaming
                }
                
                // Scroll para o final
                this.scrollToBottom();
                
                this.log(`✅ Histórico restaurado: ${history.length} mensagens`);
            }
        }
    }
    
    /**
     * Mostra mensagem de boas-vindas se for primeira visita
     * Verifica localStorage para não repetir a mensagem
     */
    async showWelcomeMessageIfFirstVisit() {
        try {
            // Verifica se já foi enviada a mensagem de boas-vindas
            const welcomeSent = localStorage.getItem('sophia_welcome_sent');
            
            if (welcomeSent === 'true') {
                this.log('ℹ️ [WELCOME] Mensagem de boas-vindas já foi enviada anteriormente');
                return;
            }
            
            // Verifica se há histórico de conversas (se já conversou, não mostra welcome)
            const history = this.loadChatHistory();
            if (history.length > 0) {
                this.log('ℹ️ [WELCOME] Usuária já tem histórico de conversas, pulando mensagem de boas-vindas');
                // Marca como enviada para não mostrar novamente
                localStorage.setItem('sophia_welcome_sent', 'true');
                return;
            }
            
            // Verifica se chatMessages está disponível
            if (!this.chatMessages) {
                this.warn('⚠️ [WELCOME] chatMessages não disponível, tentando novamente em 500ms');
                setTimeout(() => this.showWelcomeMessageIfFirstVisit(), 500);
                return;
            }
            
            // Mensagem de boas-vindas definida pela Mary (Analyst)
            // Ver docs/MENSAGEM_BOAS_VINDAS_MARY.md
            const welcomeMessage = `Olá, querida! 💕 Eu sou a Sophia, sua amiga digital do puerpério. 

Estou aqui para te escutar, te apoiar e te ajudar com informações sobre cuidados do bebê, amamentação e, claro, te lembrar das vacinas do seu pequeno através da nossa Agenda de Vacinação! 💉

Lembre-se: eu não substituo profissionais de saúde, mas estou sempre aqui quando você precisar de uma palavra amiga ou uma orientação rápida. 

Como você está se sentindo hoje? 💛`;
            
            // Delay de 800ms para parecer uma interação natural
            setTimeout(async () => {
                // Esconde welcome message se estiver visível
                if (this.welcomeMessage) {
                    this.welcomeMessage.style.display = 'none';
                }
                
                // Mostra chat messages
                if (this.chatMessages) {
                    this.chatMessages.classList.add('active');
                }
                
                // Mostra input area
                const inputArea = document.querySelector('.input-area');
                if (inputArea) {
                    inputArea.style.display = 'flex';
                }
                
                // Mostra header fixo do chat (desktop)
                if (this.chatHeaderFixed && window.innerWidth >= 1024) {
                    this.chatHeaderFixed.style.display = 'block';
                    this.updateChatHeader();
                }
                
                // Adiciona mensagem de boas-vindas com typewriter effect
                await this.addMessage(welcomeMessage, 'assistant', {}, true); // true = usar streaming
                
                // Marca como enviada no localStorage
                localStorage.setItem('sophia_welcome_sent', 'true');
                
                this.log('✅ [WELCOME] Mensagem de boas-vindas enviada');
            }, 800);
            
        } catch (error) {
            this.error('❌ [WELCOME] Erro ao mostrar mensagem de boas-vindas:', error);
        }
    }
    
    // Atualiza header do chat com informações contextuais
    async updateChatHeader() {
        if (!this.chatHeaderFixed) return;
        
        const subtitle = document.getElementById('chat-header-subtitle');
        if (!subtitle) return;
        
        try {
            // Busca contexto do usuário via API
            const response = await window.apiClient.get('/api/user-data');
            
            if (response && response.baby_profile) {
                const babyName = response.baby_profile.name;
                subtitle.textContent = `Apoio para a mamãe de ${babyName}`;
                this.babyName = babyName; // Salva para usar em sendMessage
            } else if (response && response.user) {
                this.userName = response.user.name || 'Mamãe';
                subtitle.textContent = 'Apoio para a mamãe';
            } else {
                subtitle.textContent = 'Apoio para a mamãe';
            }
            
            // Mostra header em desktop
            if (window.innerWidth >= 1024) {
                this.chatHeaderFixed.style.display = 'block';
            }
        } catch (error) {
            // Em caso de erro, usa texto padrão
            subtitle.textContent = 'Apoio para a mamãe';
            if (window.innerWidth >= 1024) {
                this.chatHeaderFixed.style.display = 'block';
            }
        }
    }
    
    // Mostra Quick Replies após resposta do assistente
    showQuickReplies(responseContent, metadata) {
        // Remove quick replies anteriores
        const existingReplies = document.querySelector('.quick-replies-container');
        if (existingReplies) {
            existingReplies.remove();
        }
        
        // Define quick replies baseados no contexto
        let quickReplies = [];
        
        // Quick replies padrão
        if (!metadata.alerta_ativo) {
            quickReplies = [
                { text: 'Ver calendário de vacinas', action: () => { if (window.chatApp) window.chatApp.showVacinas(); } },
                { text: 'Dúvidas sobre amamentação', action: () => { this.sendMessageText('Me fale sobre amamentação'); } },
                { text: 'Preciso de um incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } }
            ];
            
            // Quick replies contextuais baseados em tags de contexto (se disponíveis)
            const contextoTags = metadata.contexto_tags || [];
            const contentLower = responseContent.toLowerCase();
            
            // Mapeamento de Quick Replies por Tag (definido pela Analyst Mary)
            const QUICK_REPLIES_MAP = {
                'cansaço_extremo': [
                    { text: 'Dicas de descanso rápido', action: () => { this.sendMessageText('Preciso de dicas de descanso rápido'); } },
                    { text: 'Preciso de um incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } }
                ],
                'cansaço_extremo_critico': [
                    { text: 'Dicas de descanso rápido', action: () => { this.sendMessageText('Preciso de dicas de descanso rápido'); } },
                    { text: 'Preciso de um incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } }
                ],
                'celebração': [
                    { text: 'Contar uma conquista', action: () => { this.sendMessageText('Quero compartilhar uma conquista'); } },
                    { text: 'O que fazer hoje?', action: () => { this.sendMessageText('O que fazer hoje?'); } }
                ],
                'ansiedade': [
                    { text: 'Preciso de apoio emocional', action: () => { this.sendMessageText('Preciso de apoio emocional'); } },
                    { text: 'Frase de incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } }
                ],
                'tristeza': [
                    { text: 'Preciso de apoio emocional', action: () => { this.sendMessageText('Preciso de apoio emocional'); } },
                    { text: 'Buscar ajuda profissional', action: () => { this.showResources(); } }
                ],
                'dúvida_vacina': [
                    { text: 'Ver calendário completo', action: () => { if (window.chatApp) window.chatApp.showVacinas(); } },
                    { text: 'Qual a próxima vacina?', action: () => { this.sendMessageText('Qual a próxima vacina?'); } }
                ],
                'dúvida_amamentação': [
                    { text: 'Mais sobre amamentação', action: () => { this.sendMessageText('Me fale mais sobre amamentação'); } },
                    { text: 'Preciso de ajuda prática', action: () => { this.sendMessageText('Preciso de ajuda com amamentação'); } }
                ],
                'busca_orientação': [
                    { text: 'O que fazer hoje?', action: () => { this.sendMessageText('O que fazer hoje?'); } },
                    { text: 'Dicas práticas para hoje', action: () => { this.sendMessageText('Preciso de dicas práticas'); } }
                ],
                'busca_apoio_emocional': [
                    { text: 'Preciso de um incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } },
                    { text: 'Como me cuidar melhor?', action: () => { this.sendMessageText('Como cuidar de mim?'); } }
                ],
                'crise_emocional': [
                    { text: 'Buscar ajuda profissional', action: () => { this.showResources(); } },
                    { text: 'Preciso de apoio urgente', action: () => { this.sendMessageText('Preciso de apoio urgente'); } }
                ]
            };
            
            // Se houver tags de contexto, usa-as para determinar quick replies
            if (contextoTags.length > 0) {
                // Prioriza tags de crise
                let selectedTag = null;
                if (contextoTags.includes('crise_emocional')) {
                    selectedTag = 'crise_emocional';
                } else if (contextoTags.includes('cansaço_extremo_critico')) {
                    selectedTag = 'cansaço_extremo_critico';
                } else if (contextoTags.includes('cansaço_extremo')) {
                    selectedTag = 'cansaço_extremo';
                } else if (contextoTags.includes('tristeza')) {
                    selectedTag = 'tristeza';
                } else if (contextoTags.includes('ansiedade')) {
                    selectedTag = 'ansiedade';
                } else if (contextoTags.includes('celebração')) {
                    selectedTag = 'celebração';
                } else if (contextoTags.includes('dúvida_vacina')) {
                    selectedTag = 'dúvida_vacina';
                } else if (contextoTags.includes('dúvida_amamentação')) {
                    selectedTag = 'dúvida_amamentação';
                } else if (contextoTags.includes('busca_apoio_emocional')) {
                    selectedTag = 'busca_apoio_emocional';
                } else if (contextoTags.includes('busca_orientação')) {
                    selectedTag = 'busca_orientação';
                }
                
                if (selectedTag && QUICK_REPLIES_MAP[selectedTag]) {
                    quickReplies = QUICK_REPLIES_MAP[selectedTag];
                }
            } else if (contentLower.includes('vacina') || metadata.categoria === 'vacinação') {
                quickReplies = [
                    { text: 'Ver calendário completo', action: () => { if (window.chatApp) window.chatApp.showVacinas(); } },
                    { text: 'Qual a próxima vacina?', action: () => { this.sendMessageText('Qual a próxima vacina?'); } },
                    { text: 'O que fazer hoje?', action: () => { this.sendMessageText('O que fazer hoje?'); } }
                ];
            } else if (contentLower.includes('amament') || metadata.categoria === 'amamentação') {
                quickReplies = [
                    { text: 'Mais sobre amamentação', action: () => { this.sendMessageText('Me fale mais sobre amamentação'); } },
                    { text: 'Preciso de ajuda', action: () => { this.sendMessageText('Preciso de ajuda com amamentação'); } },
                    { text: 'O que fazer hoje?', action: () => { this.sendMessageText('O que fazer hoje?'); } }
                ];
            } else if (contentLower.includes('cansada') || contentLower.includes('exausta')) {
                quickReplies = [
                    { text: 'Preciso de um incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } },
                    { text: 'Como cuidar de mim?', action: () => { this.sendMessageText('Como cuidar de mim?'); } },
                    { text: 'Preciso de ajuda', action: () => { this.sendMessageText('Preciso de ajuda'); } }
                ];
            }
            
            // Cria container de quick replies
            const repliesContainer = document.createElement('div');
            repliesContainer.className = 'quick-replies-container';
            repliesContainer.innerHTML = quickReplies.map(reply => 
                `<button class="quick-reply-btn" data-action="${reply.text}">${reply.text}</button>`
            ).join('');
            
            // Adiciona ao final das mensagens
            if (this.chatMessages) {
                this.chatMessages.appendChild(repliesContainer);
            }
            
            // Adiciona event listeners
            repliesContainer.querySelectorAll('.quick-reply-btn').forEach((btn, index) => {
                btn.addEventListener('click', () => {
                    const reply = quickReplies[index];
                    if (reply && reply.action) {
                        reply.action();
                        repliesContainer.remove();
                    }
                });
            });
            
            // Scroll para mostrar quick replies
            this.scrollToBottom();
        }
    }
    
    // Helper para enviar mensagem de texto
    sendMessageText(text) {
        if (this.messageInput) {
            this.messageInput.value = text;
            this.updateCharCount();
            this.sendMessage();
        }
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
            this.log('Áudio não disponível');
        }
    }

    toggleSidebar() {
        this.log('🔍 [SIDEBAR] toggleSidebar chamado');
        this.log('🔍 [SIDEBAR] sidebar existe:', !!this.sidebar);
        this.log('🔍 [SIDEBAR] userId atual:', this.userId);
        
        if (!this.sidebar || !this.sidebar.classList) {
            this.error('❌ [SIDEBAR] Sidebar não encontrado ou sem classList');
            return;
        }
        
        // Verifica estado atual pela posição real, não apenas pela classe
        const rect = this.sidebar.getBoundingClientRect();
        const isActuallyOpen = rect.x >= 0;
        
        this.log('🔍 [SIDEBAR] Estado pela classe:', this.sidebar.classList.contains('open') ? 'ABERTO' : 'FECHADO');
        this.log('🔍 [SIDEBAR] Estado pela posição (x):', isActuallyOpen ? 'ABERTO' : 'FECHADO', `(x=${rect.x})`);
        
        // Se está fechado (x < 0), abre; se está aberto, fecha
        const isOpening = !isActuallyOpen;
        
        if (isOpening) {
            // FORÇA ABERTURA
            this.sidebar.classList.add('open');
            this.sidebar.style.transform = 'translateX(0)';
            setTimeout(() => {
                this.sidebar.style.removeProperty('transform'); // Remove inline style para usar CSS
            }, 10);
            this.log('✅ [SIDEBAR] ABRINDO - Classe "open" adicionada');
        } else {
            // FORÇA FECHAMENTO
            this.sidebar.classList.remove('open');
            this.sidebar.style.transform = 'translateX(-100%)';
            setTimeout(() => {
                this.sidebar.style.removeProperty('transform'); // Remove inline style para usar CSS
            }, 10);
            this.log('✅ [SIDEBAR] FECHANDO - Classe "open" removida');
        }
        
        // Adiciona/remove classe no body para controlar overlay no mobile
        if (document.body && document.body.classList) {
            if (isOpening) {
                document.body.classList.add('sidebar-open');
                this.log('✅ [SIDEBAR] Classe sidebar-open adicionada ao body');
                this.playSound(500, 150, 'sine'); // Som suave ao abrir
                
                // CORREÇÃO CRÍTICA: Força z-index do sidebar e reduz do header via JavaScript
                if (this.sidebar) {
                    this.sidebar.style.setProperty('z-index', '2147483647', 'important');
                }
                const headerModern = document.querySelector('.header-modern, header.header-modern');
                if (headerModern) {
                    headerModern.style.setProperty('z-index', '1', 'important');
                    headerModern.style.setProperty('position', 'relative', 'important');
                }
                const headerContent = document.querySelector('.header-modern-content');
                if (headerContent) {
                    headerContent.style.setProperty('z-index', '1', 'important');
                }
                // CORREÇÃO CRÍTICA: Força z-index do input-area e input-container para ZERO quando sidebar aberta
                const inputArea = document.querySelector('.input-area, div.input-area');
                if (inputArea) {
                    inputArea.style.setProperty('z-index', '0', 'important');
                }
                const inputContainer = document.querySelector('.input-container, div.input-container');
                if (inputContainer) {
                    inputContainer.style.setProperty('z-index', '0', 'important');
                }
            } else {
                document.body.classList.remove('sidebar-open');
                this.log('✅ [SIDEBAR] Classe sidebar-open removida do body');
                this.playSound(300, 100, 'sine'); // Som mais baixo ao fechar
                
                // Restaura z-index do header quando menu fecha
                const headerModern = document.querySelector('.header-modern, header.header-modern');
                if (headerModern) {
                    headerModern.style.removeProperty('z-index');
                    headerModern.style.removeProperty('position');
                }
                const headerContent = document.querySelector('.header-modern-content');
                if (headerContent) {
                    headerContent.style.removeProperty('z-index');
                }
                // Restaura z-index do input-area e input-container quando menu fecha
                const inputArea = document.querySelector('.input-area, div.input-area');
                if (inputArea) {
                    inputArea.style.removeProperty('z-index');
                }
                const inputContainer = document.querySelector('.input-container, div.input-container');
                if (inputContainer) {
                    inputContainer.style.removeProperty('z-index');
                }
            }
        }
        
        // Verifica estado final
        setTimeout(() => {
            const finalRect = this.sidebar.getBoundingClientRect();
            const finalIsOpen = finalRect.x >= 0;
            this.log('🔍 [SIDEBAR] Estado final:', finalIsOpen ? 'ABERTO' : 'FECHADO', `(x=${finalRect.x})`);
            this.log('🔍 [SIDEBAR] Classe "open" presente:', this.sidebar.classList.contains('open'));
            this.log('🔍 [SIDEBAR] Computed transform:', window.getComputedStyle(this.sidebar).transform);
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
            
            // Restaura z-index do header quando menu fecha
            const headerModern = document.querySelector('.header-modern, header.header-modern');
            if (headerModern) {
                headerModern.style.removeProperty('z-index');
                headerModern.style.removeProperty('position');
            }
            const headerContent = document.querySelector('.header-modern-content');
            if (headerContent) {
                headerContent.style.removeProperty('z-index');
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
        const intervalMs = 5000;
        const fadeDuration = 450;
        let rotationTimeout;

        const rotateMessage = () => {
            const currentElement = document.getElementById('rotating-text');
            if (!currentElement || !document.body.contains(currentElement)) {
                return; // Elemento removido, não agenda próximo tick
            }

            try {
                requestAnimationFrame(() => {
                    currentElement.style.opacity = '0';
                });

                setTimeout(() => {
                    const target = document.getElementById('rotating-text');
                    if (!target || !document.body.contains(target)) {
                        return;
                    }
                    currentIndex = (currentIndex + 1) % messages.length;
                    target.textContent = messages[currentIndex];

                    requestAnimationFrame(() => {
                        target.style.opacity = '1';
                    });

                    rotationTimeout = setTimeout(rotateMessage, intervalMs);
                }, fadeDuration);
            } catch (error) {
                this.warn('Erro ao atualizar mensagem rotativa:', error);
            }
        };

        rotationTimeout = setTimeout(rotateMessage, intervalMs);
    }

    initFeelingButtons() {
        const feelingButtons = document.querySelectorAll('.feeling-btn');
        const feelingFeedback = document.getElementById('feeling-feedback');
        const feelingResponses = {
            'cansada': 'Entendo que você está exausta. O puerpério é realmente exaustivo. Lembre-se de descansar quando possível e aceitar ajuda quando oferecida. Você está fazendo muito mais do que imagina! 💤',
            'feliz': 'Que alegria saber que você está em paz! Aproveite esses momentos de tranquilidade e celebre cada pequena vitória. Você merece sentir-se bem! 😊',
            'ansiosa': 'Entendo que você está se sentindo sobrecarregada. A ansiedade no puerpério é muito comum. Você não está sozinha nisso. Respirar fundo e focar no momento presente pode ajudar. Se a ansiedade persistir ou piorar, não hesite em buscar ajuda profissional. 🤗',
            'confusa': 'É totalmente normal se sentir confusa nessa fase. Há muitas mudanças acontecendo ao mesmo tempo. Tome um dia de cada vez e lembre-se: não há perguntas bobas. Estou aqui para ajudar! 💭',
            'triste': 'Sinto muito que você esteja se sentindo para baixo. Seus sentimentos são válidos e importantes. Se essa tristeza persistir ou interferir no seu dia a dia, considere buscar ajuda profissional. Você merece apoio. 💙',
            'gratidao': 'Que lindo sentir gratidão! Apreciar os momentos bons é muito importante. Guarde esses sentimentos para quando os dias estiverem mais difíceis. Você está criando memórias preciosas. 🙏'
        };

        feelingButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Feedback visual imediato
                btn.classList.add('clicked');
                btn.style.transform = 'scale(0.95)';
                
                        setTimeout(() => {
                    btn.classList.remove('clicked');
                    btn.style.transform = '';
                }, 200);
                
                const feeling = btn.dataset.feeling;
                const response = feelingResponses[feeling];
                if (response) {
                    // Remove seleção anterior
                    feelingButtons.forEach(b => b.classList.remove('selected'));
                    // Adiciona seleção ao botão clicado
                    btn.classList.add('selected');
                    
                    // Mostra feedback visual
                    if (feelingFeedback) {
                        feelingFeedback.style.display = 'flex';
                        setTimeout(() => {
                            if (feelingFeedback) {
                                feelingFeedback.style.display = 'none';
                            }
                        }, 3000);
                    }
                    
                    // Esconde welcome message e mostra chat após um breve delay
                    setTimeout(() => {
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

                        // Adiciona mensagem do usuário
                        this.addMessage(`Estou me sentindo ${btn.textContent.trim()}`, 'user');
                        
                        // Adiciona resposta empática
                        setTimeout(() => {
                            this.addMessage(response, 'assistant');
                        }, 500);
                    }, 800);
                }
            });
        });
        
        // Botão "Escrever com próprias palavras"
        const writeOwnBtn = document.getElementById('feeling-write-own');
        if (writeOwnBtn) {
            writeOwnBtn.addEventListener('click', () => {
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
            });
        }
        
        // Botão "Prefiro não responder agora"
        const skipBtn = document.getElementById('feeling-skip');
        if (skipBtn) {
            skipBtn.addEventListener('click', () => {
                // Apenas esconde a caixa de sentimentos suavemente
                const feelingBox = document.querySelector('.feeling-box');
                if (feelingBox) {
                    feelingBox.style.opacity = '0.5';
                    feelingBox.style.pointerEvents = 'none';
                    setTimeout(() => {
                        feelingBox.style.display = 'none';
                    }, 300);
                }
            });
        }
    }

    
    async loadChatHistory() {
        try {
            this.log(`🔍 [HISTORY] Carregando histórico para userId: ${this.userId}`);
            const response = await fetch(`/api/historico/${this.userId}`);
            const history = await response.json();
            
            this.log(`📋 [HISTORY] Histórico recebido: ${history.length} mensagens`);
            
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
                this.log(`✅ [HISTORY] Histórico carregado no backend (${history.length} mensagens) - NÃO exibido na tela para manter interface limpa`);
                // NÃO mostra mensagem automática - o usuário deve clicar no Menu Inicial para começar
                // A Sophia lembrará do histórico quando o usuário iniciar uma nova conversa
            } else {
                this.log(`ℹ️ [HISTORY] Nenhuma mensagem encontrada no histórico para userId: ${this.userId}`);
            }
            
            // SEMPRE garante que o Menu Inicial está visível ao recarregar
            // O usuário deve clicar para iniciar uma nova conversa
            this.backToWelcomeScreen();
        } catch (error) {
            this.error('❌ [HISTORY] Erro ao carregar histórico:', error);
            this.error('❌ [HISTORY] userId usado:', this.userId);
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
                    this.log('✅ [HISTORY] Histórico limpo no backend');
                } else {
                    this.warn('⚠️ [HISTORY] Erro ao limpar histórico no backend');
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
                this.error('Erro ao limpar histórico:', error);
                alert('Erro ao limpar histórico. Tente novamente.');
            }
        }
    }
    
    async clearMemory() {
        // Confirmação dupla para garantir que o usuário tem certeza
        const primeiraConfirmacao = confirm(
            '⚠️ ATENÇÃO: Esta ação irá apagar TODA a memória da Sophia!\n\n' +
            'Isso inclui:\n' +
            '• Nomes memorizados (seu nome, nome do bebê, etc.)\n' +
            '• Lugares mencionados\n' +
            '• Comidas e preferências\n' +
            '• Informações pessoais salvas\n\n' +
            'A Sophia não se lembrará mais desses dados em conversas futuras.\n\n' +
            'Deseja continuar?'
        );
        
        if (!primeiraConfirmacao) {
            return;
        }
        
        // Segunda confirmação
        const segundaConfirmacao = confirm(
            '🛑 ÚLTIMA CONFIRMAÇÃO\n\n' +
            'Tem CERTEZA ABSOLUTA de que deseja apagar toda a memória da Sophia?\n\n' +
            'Esta ação NÃO PODE ser desfeita.'
        );
        
        if (!segundaConfirmacao) {
            return;
        }
        
        try {
            // Limpa a memória no backend
            const response = await fetch('/api/limpar-memoria-ia', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok && data.sucesso) {
                this.log('✅ [MEMORY] Memória da Sophia limpa:', data);
                
                // Mostra mensagem de sucesso detalhada
                alert(
                    '✅ Memória da Sophia limpa com sucesso!\n\n' +
                    `• ${data.conversas_apagadas || 0} conversa(s) da memória\n` +
                    `• ${data.info_apagadas || 0} informação(ões) pessoal(is)\n` +
                    `• ${data.memoria_sophia_apagadas || 0} dado(s) memorizado(s) (nomes, lugares, comidas)\n\n` +
                    'A Sophia não se lembrará mais desses dados em conversas futuras.'
                );
            } else {
                this.error('❌ [MEMORY] Erro ao limpar memória:', data);
                alert('Erro ao limpar memória da Sophia. Tente novamente.');
            }
        } catch (error) {
            this.error('❌ [MEMORY] Erro ao limpar memória:', error);
            alert('Erro ao limpar memória da Sophia. Tente novamente.');
        }
    }
    
    showAlert(alertas) {
        if (!this.alertMessage || !this.alertModal) {
            this.warn('Elementos de alerta não estão disponíveis');
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
    
    showAvisoVisualRisco(nivelRisco = 'alto') {
        // Remove aviso anterior se existir
        const avisoAnterior = document.querySelector('.aviso-risco-visual');
        if (avisoAnterior) {
            avisoAnterior.remove();
        }
        
        // Cria elemento de aviso visual acolhedor
        const avisoRisco = document.createElement('div');
        avisoRisco.className = 'aviso-risco-visual';
        avisoRisco.setAttribute('data-nivel', nivelRisco);
        
        const nivelTexto = nivelRisco === 'alto' ? 'alto' : 'leve';
        const corFundo = nivelRisco === 'alto' ? '#fff3cd' : '#fff9e6'; // Amarelo claro, mais intenso para alto
        const corBorda = nivelRisco === 'alto' ? '#ffc107' : '#ffd700'; // Borda mais forte para alto
        
        avisoRisco.innerHTML = `
            <div class="aviso-risco-content">
                <div class="aviso-risco-icon">💛</div>
                <div class="aviso-risco-text">
                    <strong>Se estiver em um momento difícil, o CVV (188) pode te ouvir 24h.</strong>
                    <p>Você não precisa enfrentar isso sozinho(a).</p>
                    <a href="https://cvv.org.br/chat/" target="_blank" rel="noopener" class="aviso-risco-button">
                        Falar com alguém agora
                    </a>
                </div>
                <button class="aviso-risco-close" onclick="this.parentElement.parentElement.remove()" aria-label="Fechar aviso">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Estilização inline para garantir que apareça
        avisoRisco.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: ${corFundo};
            border-bottom: 3px solid ${corBorda};
            padding: 1rem;
            z-index: 10000;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            animation: slideDown 0.3s ease-out;
        `;
        
        // Adiciona ao body
        document.body.appendChild(avisoRisco);
        
        // Adiciona animação CSS
        if (!document.getElementById('aviso-risco-styles')) {
            const style = document.createElement('style');
            style.id = 'aviso-risco-styles';
            style.textContent = `
                @keyframes slideDown {
                    from {
                        transform: translateY(-100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
                @keyframes slideUp {
                    from {
                        transform: translateY(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateY(-100%);
                        opacity: 0;
                    }
                }
                .aviso-risco-content {
                    display: flex;
                    align-items: center;
                    max-width: 1200px;
                    margin: 0 auto;
                    gap: 1rem;
                }
                .aviso-risco-icon {
                    font-size: 2rem;
                    flex-shrink: 0;
                }
                .aviso-risco-text {
                    flex: 1;
                    color: #856404;
                }
                .aviso-risco-text strong {
                    display: block;
                    margin-bottom: 0.25rem;
                    font-size: 1.1rem;
                }
                .aviso-risco-text p {
                    margin: 0;
                    font-size: 0.95rem;
                }
                .aviso-risco-text a {
                    color: #856404;
                    text-decoration: underline;
                    font-weight: 600;
                }
                .aviso-risco-text a:hover {
                    color: #533f03;
                }
                .aviso-risco-button {
                    display: inline-block;
                    margin-top: 0.5rem;
                    padding: 0.5rem 1.5rem;
                    background: #856404;
                    color: white !important;
                    text-decoration: none !important;
                    border-radius: 25px;
                    font-weight: 600;
                    font-size: 0.9rem;
                    transition: background 0.3s;
                }
                .aviso-risco-button:hover {
                    background: #533f03;
                    color: white !important;
                }
                .aviso-risco-close {
                    background: transparent;
                    border: none;
                    font-size: 1.2rem;
                    color: #856404;
                    cursor: pointer;
                    padding: 0.5rem;
                    flex-shrink: 0;
                    transition: color 0.2s;
                }
                .aviso-risco-close:hover {
                    color: #533f03;
                }
                /* Ajusta padding do chat quando o aviso está visível */
                body:has(.aviso-risco-visual) .chat-container {
                    padding-top: 80px;
                }
                @media (max-width: 768px) {
                    .aviso-risco-content {
                        flex-direction: column;
                        text-align: center;
                    }
                    .aviso-risco-icon {
                        font-size: 1.5rem;
                    }
                    .aviso-risco-text {
                        font-size: 0.9rem;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Ajusta o padding do container de chat para não ficar sobreposto
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.style.paddingTop = '80px';
        }
        
        this.log('✅ [ALERTA] Aviso visual de risco exibido (nível: ' + nivelRisco + ')');
    }
    
    hideAvisoVisualRisco() {
        const avisoRisco = document.querySelector('.aviso-risco-visual');
        if (avisoRisco) {
            avisoRisco.style.animation = 'slideUp 0.3s ease-out';
            setTimeout(() => {
                avisoRisco.remove();
                // Remove padding do chat
                const chatContainer = document.querySelector('.chat-container');
                if (chatContainer) {
                    chatContainer.style.paddingTop = '';
                }
            }, 300);
        }
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
                this.warn('Status indicator não tem propriedade className');
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
                    this.warn('Erro ao definir className online:', e);
                    this.statusIndicator = null;
                    return;
                }
                try {
                    if (this.statusIndicator && this.statusIndicator.nodeType === 1 && 'innerHTML' in this.statusIndicator) {
                        this.statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Online';
                    }
                } catch (e) {
                    this.warn('Erro ao definir innerHTML online:', e);
                    // Não retorna aqui, apenas loga o erro
                }
            } else {
                try {
                    if (this.statusIndicator && this.statusIndicator.nodeType === 1 && 'className' in this.statusIndicator) {
                        this.statusIndicator.className = 'status-offline';
                    }
                } catch (e) {
                    this.warn('Erro ao definir className offline:', e);
                    this.statusIndicator = null;
                    return;
                }
                try {
                    if (this.statusIndicator && this.statusIndicator.nodeType === 1 && 'innerHTML' in this.statusIndicator) {
                        this.statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Offline';
                    }
                } catch (e) {
                    this.warn('Erro ao definir innerHTML offline:', e);
                    // Não retorna aqui, apenas loga o erro
                }
            }
        } catch (error) {
            // Se houver erro geral, reseta a referência
            this.warn('Erro ao atualizar status de conexão:', error);
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
        
        // Footer CVV removido - código comentado
        
        // Marca que o usuário já interagiu
        localStorage.setItem(`sophia_has_interacted_${this.userId}`, 'true');
        
        // Sophia faz uma pergunta inicial ao usuário
        const initialQuestion = "Olá! Como você está se sentindo hoje? Como posso te ajudar nessa jornada do puerpério? 💛";
        this.addMessage(initialQuestion, 'assistant');
        
        // Foca no input para o usuário responder
        if (this.messageInput && typeof this.messageInput.focus === 'function') {
            setTimeout(() => {
                this.messageInput.focus();
            }, 100);
        }
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
        
        // Footer CVV removido - código comentado
        
        // NÃO gera novo userId - mantém o mesmo para preservar histórico
        // O userId é persistente e mantém a memória da Sophia
        // this.userId = this.generateUserId(); // REMOVIDO - mantém userId persistente
    }
    
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.log('Permissão para notificações concedida');
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
    
    /**
     * Detecta quando teclado virtual abre/fecha no mobile
     * Ajusta posição do input para não ser coberto pelo teclado
     */
    detectKeyboard() {
        const inputArea = document.querySelector('.input-area');
        if (!inputArea) return;
        
        // DEBUG_MODE global (definido no topo do arquivo)
        const DEBUG_MODE = window.DEBUG_MODE || false;
        
        const viewportHeight = window.visualViewport?.height || window.innerHeight;
        let lastHeight = viewportHeight;
        
        // Debug: Cria indicador visual apenas em desenvolvimento
        let debugIndicator = null;
        if (DEBUG_MODE) {
            // Remove indicador anterior se existir
            const existing = document.getElementById('keyboard-debug-indicator');
            if (existing) existing.remove();
            
            debugIndicator = document.createElement('div');
            debugIndicator.id = 'keyboard-debug-indicator';
            debugIndicator.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: rgba(255, 0, 0, 0.8);
                color: white;
                padding: 0.25rem 0.5rem;
                font-size: 0.75rem;
                z-index: 10000;
                text-align: center;
                font-weight: bold;
                display: none;
            `;
            debugIndicator.textContent = '🔴 KEYBOARD-OPEN DISPARADO';
            document.body.appendChild(debugIndicator);
        }
        
        // Usa visualViewport API quando disponível (melhor detecção)
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => {
                const currentHeight = window.visualViewport.height;
                const heightDiff = lastHeight - currentHeight;
                
                // Se altura diminuiu significativamente (> 150px), teclado abriu
                if (heightDiff > 150) {
                    inputArea.classList.add('keyboard-open');
                    if (DEBUG_MODE && debugIndicator) {
                        debugIndicator.style.display = 'block';
                        this.log('🔴 [KEYBOARD] Teclado virtual DETECTADO (heightDiff:', heightDiff, 'px)');
                    }
                } else if (heightDiff < -50) {
                    // Se altura aumentou, teclado fechou
                    inputArea.classList.remove('keyboard-open');
                    if (DEBUG_MODE && debugIndicator) {
                        debugIndicator.style.display = 'none';
                        this.log('✅ [KEYBOARD] Teclado virtual FECHADO (heightDiff:', heightDiff, 'px)');
                    }
                }
                
                lastHeight = currentHeight;
            });
        } else {
            // Fallback: usa resize event (menos preciso)
            window.addEventListener('resize', () => {
                const currentHeight = window.innerHeight;
                const heightDiff = lastHeight - currentHeight;
                
                if (heightDiff > 150) {
                    inputArea.classList.add('keyboard-open');
                    if (DEBUG_MODE && debugIndicator) {
                        debugIndicator.style.display = 'block';
                        this.log('🔴 [KEYBOARD] Teclado virtual DETECTADO (heightDiff:', heightDiff, 'px)');
                    }
                } else if (heightDiff < -50) {
                    inputArea.classList.remove('keyboard-open');
                    if (DEBUG_MODE && debugIndicator) {
                        debugIndicator.style.display = 'none';
                        this.log('✅ [KEYBOARD] Teclado virtual FECHADO (heightDiff:', heightDiff, 'px)');
                    }
                }
                
                lastHeight = currentHeight;
            });
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
                this.log('💾 [LOGIN MODAL] Email lembrado carregado:', rememberedEmail);
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
        
        this.log(`🔍 [LOGIN MODAL] Tentando login com email: ${email}, password length: ${password.length}, remember_me: ${rememberMe}`);
        
        // Salva email no localStorage se "Lembre-se de mim" estiver marcado
        if (rememberMe) {
            localStorage.setItem('remembered_email', email);
            this.log('💾 [LOGIN MODAL] Email salvo no localStorage');
        } else {
            localStorage.removeItem('remembered_email');
            this.log('🗑️ [LOGIN MODAL] Email removido do localStorage');
        }
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'include',  // Importante para cookies de sessão (especialmente em mobile)
                body: JSON.stringify({email, password, remember_me: rememberMe})
            });
            
            const data = await response.json();
            this.log('🔍 [LOGIN MODAL] Resposta completa:', data);
            this.log('🔍 [LOGIN MODAL] Status HTTP:', response.status);
            this.log('🔍 [LOGIN MODAL] response.ok:', response.ok);
            
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
                this.log('✅ [LOGIN MODAL] Login bem-sucedido');
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
                this.error('❌ [LOGIN MODAL] Erro no login:', data.erro);
                alert('⚠️ ' + (data.erro || 'Email ou senha incorretos'));
            }
        } catch (error) {
            this.error('❌ [LOGIN MODAL] Erro na requisição:', error);
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
                                this.warn('URL de imagem inválida (sem domínio):', passo.imagem);
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
                    this.warn('Erro ao processar URL da imagem:', passo.imagem, e);
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
                        ${trimestre.exames ? `
                            <div class="exames-container" style="margin-top: 1.5rem;">
                                <div class="exames-header">
                                    <i class="fas fa-vial"></i>
                                    <strong>🔬 Exames recomendados:</strong>
                                </div>
                                <div class="exames-list">
                                    ${trimestre.exames.map(ex => {
                                        // Separa o nome do exame do aviso médico
                                        const parts = ex.split(' - ⚕️ ');
                                        const nomeExame = parts[0];
                                        const aviso = parts[1] || '';
                                        return `
                                            <div class="exame-item">
                                                <div class="exame-content">
                                                    <i class="fas fa-check-circle exame-icon"></i>
                                                    <span class="exame-nome">${nomeExame}</span>
                                                </div>
                                                ${aviso ? `<div class="exame-aviso"><i class="fas fa-stethoscope"></i> ${aviso}</div>` : ''}
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        ` : ''}
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
            console.error('❌ Erro ao carregar vacinas:', error);
            alert('❌ Erro ao carregar vacinas. Verifique o console para mais detalhes.');
        }
    }
    
    async fetchVacinasStatus() {
        try {
            const response = await fetch('/api/vacinas/status');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            this.error('Erro ao buscar status:', error);
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
        // Reduzido para 20 partículas para melhor performance no mobile (era 50)
        const confettiCount = 20;
        
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
    
    // Emergency Numbers Modal Functions
    async openEmergencyNumbersModal() {
        if (!this.emergencyNumbersModal) return;
        
        this.emergencyNumbersModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Carrega os números de emergência
        await this.loadEmergencyNumbers();
    }
    
    closeEmergencyNumbersModal() {
        if (this.emergencyNumbersModal) {
            this.emergencyNumbersModal.style.display = 'none';
        }
        document.body.style.overflow = '';
    }

    // Profile Modal
    openProfileModal() {
        if (!this.profileModal) return;
        this.loadProfileData();
        this.profileModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    closeProfileModal() {
        if (this.profileModal) {
            this.profileModal.style.display = 'none';
        }
        document.body.style.overflow = '';
    }

    getProfileStorageKey() {
        return 'sophia_profile_data';
    }

    loadProfileData() {
        if (!this.profileInputs) return;
        try {
            const stored = localStorage.getItem(this.getProfileStorageKey());
            if (!stored) return;
            const data = JSON.parse(stored);
            Object.entries(this.profileInputs).forEach(([key, el]) => {
                if (!el) return;
                el.value = data[key] ?? '';
            });
        } catch (error) {
            this.error('Erro ao carregar perfil:', error);
        }
    }

    collectProfileData() {
        const data = {};
        Object.entries(this.profileInputs || {}).forEach(([key, el]) => {
            data[key] = el?.value?.trim() || '';
        });
        return data;
    }

    saveProfileData() {
        try {
            const data = this.collectProfileData();
            localStorage.setItem(this.getProfileStorageKey(), JSON.stringify(data));
            this.showNotification('Perfil salvo com sucesso!');
        } catch (error) {
            this.error('Erro ao salvar perfil:', error);
            this.showNotification('Não foi possível salvar agora. Tente novamente.');
        }
    }

    clearProfileForm() {
        Object.values(this.profileInputs || {}).forEach((el) => {
            if (el) el.value = '';
        });
    }
    
    async loadEmergencyNumbers() {
        if (!this.emergencyNumbersList) return;
        
        try {
            const response = await fetch('/api/telefones');
            const data = await response.json();
            
            let html = '';
            
            // Emergências
            if (data.emergencias) {
                html += '<div class="emergency-numbers-section"><h4>🚨 Emergências</h4><div class="emergency-numbers-grid">';
                for (const key in data.emergencias) {
                    const item = data.emergencias[key];
                    html += this.createEmergencyNumberCard(item);
                }
                html += '</div></div>';
            }
            
            // Saúde Mental
            if (data.saude_mental) {
                html += '<div class="emergency-numbers-section"><h4>💚 Saúde Mental</h4><div class="emergency-numbers-grid">';
                for (const key in data.saude_mental) {
                    const item = data.saude_mental[key];
                    html += this.createEmergencyNumberCard(item);
                }
                html += '</div></div>';
            }
            
            this.emergencyNumbersList.innerHTML = html;
        } catch (error) {
            this.error('Erro ao carregar números de emergência:', error);
            if (this.emergencyNumbersList) {
                this.emergencyNumbersList.innerHTML = '<p>Erro ao carregar números de emergência. Tente novamente.</p>';
            }
        }
    }
    
    createEmergencyNumberCard(item) {
        const freeBadge = item.gratuito ? '<span class="emergency-free">Gratuito</span>' : '';
        const phoneLink = item.disque ? `tel:${item.disque}` : '#';
        return `
            <div class="emergency-number-card">
                ${item.disque ? `<a href="${phoneLink}" class="emergency-call-btn">
                    <i class="fas fa-phone"></i>
                </a>` : ''}
                <div class="emergency-number-info">
                    <h5>${item.nome || ''}</h5>
                    <p>${item.descricao || ''}</p>
                    ${item.horario ? `<p><small>⏰ ${item.horario}</small></p>` : ''}
                    ${freeBadge}
                </div>
            </div>
        `;
    }
            
    // Hospitals Modal Functions
    closeHospitalsModal() {
        if (this.hospitalsModal) {
            this.hospitalsModal.style.display = 'none';
        }
        document.body.style.overflow = '';
    }
    
    async findNearbyHospitals() {
        if (!this.hospitalsModal) return;
        
        // Fecha o modal de números de emergência
        this.closeEmergencyNumbersModal();
        
        // Abre o modal de hospitais
        this.hospitalsModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Mostra loading
        if (this.hospitalsLoading) {
            this.hospitalsLoading.style.display = 'block';
        }
        if (this.hospitalsError) {
            this.hospitalsError.style.display = 'none';
        }
        if (this.hospitalsList) {
            this.hospitalsList.innerHTML = '';
        }
        
        try {
            // Solicita permissão de geolocalização
            if (!navigator.geolocation) {
                throw new Error('Geolocalização não é suportada pelo seu navegador');
            }
            
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                });
            });
            
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            // Busca hospitais próximos
            const hospitals = await this.searchHospitalsNearby(lat, lon);
            
            // Esconde loading
            if (this.hospitalsLoading) {
                this.hospitalsLoading.style.display = 'none';
            }
            
            // Exibe os hospitais encontrados
            if (hospitals && hospitals.length > 0) {
                this.displayHospitals(hospitals);
                } else {
                this.showEmptyState();
            }
        } catch (error) {
            if (this.hospitalsLoading) {
                this.hospitalsLoading.style.display = 'none';
            }
            if (this.hospitalsError) {
                this.hospitalsError.style.display = 'block';
                this.hospitalsError.innerHTML = `<p>Erro: ${error.message}</p>`;
            }
            // Mostra estado vazio mesmo em caso de erro
            this.showEmptyState();
            this.error('Erro ao buscar hospitais:', error);
        }
    }
    
    async searchHospitalsNearby(lat, lon, radius = 50000) {
        /** 
         * Busca hospitais próximos usando Overpass API
         * OTIMIZADO: Query simplificada + filtragem no cliente
         */
        
        // ========================================
        // QUERY OTIMIZADA: Busca hospitais (filtragem específica no cliente)
        // ========================================
        // Busca todos os hospitais. A filtragem e priorização por maternidade/obstetrícia
        // acontece no cliente, priorizando hospitais com tags ou nomes relacionados.
        const query = `[out:json][timeout:30];
(node["amenity"="hospital"](around:${radius},${lat},${lon});
 way["amenity"="hospital"](around:${radius},${lat},${lon});
 relation["amenity"="hospital"](around:${radius},${lat},${lon}););
out center tags;`;
        
        // Lista de servidores Overpass para tentar
        const servers = [
            'https://overpass-api.de/api/interpreter',
            'https://overpass.kumi.systems/api/interpreter',
            'https://overpass.openstreetmap.ru/api/interpreter'
        ];
        
        // Armazena o último erro para exibição ao usuário
        let lastError = null;
        
        // Tenta cada servidor até um funcionar
        for (let serverIndex = 0; serverIndex < servers.length; serverIndex++) {
            const server = servers[serverIndex];
            
            try {
                const controller = new AbortController();
                // Timeout aumentado para 30 segundos (era 20)
                const timeoutId = setTimeout(() => controller.abort(), 30000);
                
                let response;
                try {
                    response = await fetch(server, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `data=${encodeURIComponent(query)}`,
                        signal: controller.signal
                    });
                    clearTimeout(timeoutId);
                } catch (fetchError) {
                    clearTimeout(timeoutId);
                    lastError = fetchError;
                    if (serverIndex < servers.length - 1) {
                        continue; // Tenta próximo servidor
                    }
                    // Se esgotou todos os servidores, lança erro amigável
                    throw new Error('O servidor de mapas está demorando para responder. Tente novamente em alguns segundos ou reduza o raio de busca.');
                }
                
                // Tratamento de erros HTTP com mensagens amigáveis
                if (!response.ok) {
                    if (response.status === 504 || response.status === 500) {
                        lastError = new Error('O servidor de mapas está demorando para responder. Tente novamente em alguns segundos ou reduza o raio de busca.');
                        if (serverIndex < servers.length - 1) {
                            continue; // Tenta próximo servidor
                        }
                        // Se esgotou todos os servidores, lança erro
                        throw lastError;
                    }
                    if (response.status === 429) {
                        lastError = new Error('Muitas solicitações. Aguarde alguns segundos antes de tentar novamente.');
                        if (serverIndex < servers.length - 1) {
                            continue; // Tenta próximo servidor
                        }
                        throw lastError;
                    }
                    if (serverIndex < servers.length - 1) {
                        continue; // Tenta próximo servidor para outros erros
                    }
                    throw new Error(`Erro ao buscar hospitais: ${response.status} ${response.statusText}`);
                }
                
                const responseText = await response.text();
                
                let data;
                try {
                    data = JSON.parse(responseText);
                } catch (parseError) {
                    if (serverIndex < servers.length - 1) {
                        continue;
                    }
                    return [];
                }
                
                const hospitals = [];
                
                if (data.elements && data.elements.length > 0) {
                    for (const element of data.elements) {
                        const street = element.tags?.['addr:street'] || '';
                        const houseNumber = element.tags?.['addr:housenumber'] || '';
                        const neighborhood = element.tags?.['addr:suburb'] || element.tags?.['addr:neighbourhood'] || '';
                        const city = element.tags?.['addr:city'] || element.tags?.['addr:town'] || '';
                        const state = element.tags?.['addr:state'] || '';
                        
                        let fullAddress = '';
                        if (street) {
                            fullAddress = street;
                            if (houseNumber) {
                                fullAddress += `, ${houseNumber}`;
                            }
                            if (neighborhood) {
                                fullAddress += ` - ${neighborhood}`;
                            }
                            if (city) {
                                fullAddress += `, ${city}`;
                            }
                            if (state) {
                                fullAddress += ` - ${state}`;
                            }
                        } else if (neighborhood) {
                            fullAddress = neighborhood;
                            if (city) {
                                fullAddress += `, ${city}`;
                            }
                        } else if (city) {
                            fullAddress = city;
                        }
                        
                        let hospitalName = element.tags?.name || 
                                          element.tags?.['name:pt'] || 
                                          element.tags?.['official_name'] ||
                                          element.tags?.['alt_name'] ||
                                          element.tags?.['short_name'] || '';
                        
                        const specialty = (element.tags?.['healthcare:speciality'] || '').toLowerCase();
                        const healthcare = (element.tags?.['healthcare'] || '').toLowerCase();
                        const nameLower = (hospitalName || '').toLowerCase();
                        const emergency = (element.tags?.['emergency'] || '').toLowerCase();
                        const payment = (element.tags?.['healthcare:payment'] || '').toLowerCase();
                        const operatorType = (element.tags?.['operator:type'] || '').toLowerCase();
                        
                        // ========================================
                        // FILTRO DUPLO OBRIGATÓRIO DE SEGURANÇA
                        // ========================================
                        // REGRA 1: Validar TIPO - Deve ser Hospital (excluir UBS, Clínicas, UPAs, Postos)
                        const isValidHospitalType = this.validateHospitalType(element.tags, hospitalName);
                        if (!isValidHospitalType) {
                            // Rejeita estabelecimentos que não são hospitais
                            continue;
                        }
                        
                        // REGRA 2: Validar INFRAESTRUTURA - Aceita hospitais gerais, bloqueia especializados que não atendem parto
                        const infrastructureValidation = this.validateMaternityInfrastructure(element.tags, hospitalName, specialty, healthcare);
                        if (!infrastructureValidation.accepted) {
                            // Rejeita hospitais especializados que não atendem parto (lista negra)
                            continue;
                        }
                        
                        // Se chegou aqui, passou no filtro duplo obrigatório
                        // ========================================
                        
                        const isEmergency = emergency === 'yes' || emergency === 'emergency_ward' || 
                                           nameLower.includes('pronto socorro') || nameLower.includes('pronto atendimento') ||
                                           nameLower.includes('emergency') || nameLower.includes('urgência');
                        
                        // Verifica se aceita SUS (hospital público)
                        const acceptsSUS = payment === 'public' || payment === 'yes' || 
                                          operatorType === 'public';
                        
                        // Extrai informação sobre se é confirmação explícita ou dedução
                        const hasExplicitMaternity = infrastructureValidation.explicit; // true = explícito, false = dedução
                        
                        // Marca como maternidade: sempre true pois passou no filtro (geral ou com maternidade explícita)
                        const isMaternity = true;
                        
                        if (!hospitalName || hospitalName.trim() === '') {
                            hospitalName = hasExplicitMaternity ? 'Hospital com Ala de Maternidade' : 'Hospital Geral';
                        }
                        
                        // Identifica se é público ou privado baseado no nome
                        const isPublic = nameLower.includes('ubs') || 
                                        nameLower.includes('upa') || 
                                        nameLower.includes('municipal') || 
                                        nameLower.includes('estadual') || 
                                        nameLower.includes('federal') ||
                                        nameLower.includes('santa casa') ||
                                        nameLower.includes('santa casa de misericórdia') ||
                                        payment === 'public' || 
                                        operatorType === 'public';
                        
                        const hospital = {
                            name: hospitalName,
                            lat: element.lat || element.center?.lat,
                            lon: element.lon || element.center?.lon,
                            address: fullAddress,
                            street: street,
                            houseNumber: houseNumber,
                            neighborhood: neighborhood,
                            city: city,
                            state: state,
                            phone: element.tags?.['phone'] || element.tags?.['contact:phone'] || element.tags?.['contact:mobile'] || '',
                            website: element.tags?.['website'] || element.tags?.['contact:website'] || '',
                            distance: this.calculateDistance(lat, lon, element.lat || element.center?.lat, element.lon || element.center?.lon),
                            isMaternity: isMaternity, // Sempre true pois passou no filtro duplo
                            isMaternityExplicit: hasExplicitMaternity, // true = confirmação explícita, false = dedução (hospital geral)
                            isEmergency: isEmergency,
                            acceptsSUS: acceptsSUS,
                            isPublic: isPublic
                        };
                        
                        if (hospital.lat && hospital.lon) {
                            hospitals.push(hospital);
                        }
                    }
                }
                
                // Remove duplicatas
                let filteredHospitals = this.deduplicateHospitals(hospitals);
                
                // Filtra hospitais que têm TODAS as informações completas: nome, endereço, telefone e coordenadas
                filteredHospitals = filteredHospitals.filter(h => {
                    const hasName = h.name && h.name.trim() !== '' && h.name !== 'Hospital';
                    const hasAddress = h.address && h.address.trim() !== '';
                    const hasPhone = h.phone && h.phone.trim() !== '';
                    const hasCoordinates = h.lat && h.lon;
                    return hasName && hasAddress && hasPhone && hasCoordinates;
                });
                
                // Adiciona score de prioridade baseado em palavras-chave de maternidade/obstetrícia no nome
                filteredHospitals.forEach(h => {
                    const nameLower = (h.name || '').toLowerCase();
                    const maternityKeywords = ['maternidade', 'maternity', 'obstetrícia', 'obstetrics', 'obstetricia', 'parto', 'nascimento'];
                    h.maternityScore = 0;
                    maternityKeywords.forEach(keyword => {
                        if (nameLower.includes(keyword)) {
                            h.maternityScore += 10; // Score alto para palavras-chave no nome
                        }
                    });
                    // Bonus para hospitais com confirmação explícita
                    if (h.isMaternityExplicit) {
                        h.maternityScore += 5;
                    }
                });
                
                // Ordena: 1) Por score de maternidade (maior primeiro), 2) Por distância (mais próximo primeiro)
                filteredHospitals.sort((a, b) => {
                    // Prioridade 1: Hospitais com maior score de maternidade primeiro
                    if (b.maternityScore !== a.maternityScore) {
                        return b.maternityScore - a.maternityScore;
                    }
                    // Prioridade 2: Entre hospitais com mesmo score, ordena por distância (mais próximo primeiro)
                    return a.distance - b.distance;
                });
                
                return filteredHospitals;
            
            } catch (error) {
                // Captura erros da requisição ou processamento
                lastError = error;
                if (serverIndex < servers.length - 1) {
                    continue; // Tenta próximo servidor
                }
                // Se esgotou todos os servidores, propaga o erro
                // O erro já foi tratado com mensagem amigável nas verificações anteriores
                throw error;
            }
        }
        
        // Se chegou aqui sem retornar, nenhum servidor funcionou
        if (lastError) {
            throw lastError; // Lança o último erro capturado (já com mensagem amigável)
        }
        
        return []; // Fallback: retorna array vazio se nenhum erro foi capturado
    }
    
    calculateDistance(lat1, lon1, lat2, lon2) {
        /** Calcula distância em metros usando fórmula de Haversine */
        const R = 6371000; // Raio da Terra em metros
        const dLat = this.toRad(lat2 - lat1);
        const dLon = this.toRad(lon2 - lon1);
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }
    
    toRad(degrees) {
        return degrees * (Math.PI / 180);
    }
    
    /**
     * ========================================
     * VALIDAÇÃO DE TIPO DE HOSPITAL
     * ========================================
     * REGRA DE SEGURANÇA: Apenas hospitais reais devem aparecer.
     * Exclui: UBS, Clínicas, UPAs, Postos de Saúde, Unidades Básicas, etc.
     * 
     * @param {Object} tags - Tags do elemento OSM
     * @param {string} hospitalName - Nome do estabelecimento
     * @returns {boolean} - true se for hospital válido, false caso contrário
     */
    validateHospitalType(tags, hospitalName) {
        const nameLower = (hospitalName || '').toLowerCase();
        const healthcareType = (tags?.['healthcare'] || '').toLowerCase();
        const amenity = (tags?.['amenity'] || '').toLowerCase();
        
        // PALAVRAS-CHAVE QUE INDICAM QUE NÃO É HOSPITAL (EXCLUIR)
        const excludeKeywords = [
            'ubs', 'unidade básica de saúde',
            'clínica', 'clinica',
            'upa', 'unidade de pronto atendimento',
            'posto de saúde', 'posto',
            'centro de saúde',
            'unidade de saúde',
            'ambulatório', 'ambulatorio',
            'consultório', 'consultorio',
            'laboratório', 'laboratorio',
            'farmácia', 'farmacia',
            'policlínica', 'policlinica',
            'emergência', 'emergencia', // Se não tiver "hospital" no contexto
            'pronto atendimento', // Se não tiver "hospital" no contexto
        ];
        
        // Verificar se o nome contém palavras de exclusão
        for (const keyword of excludeKeywords) {
            if (nameLower.includes(keyword)) {
                // EXCEÇÃO: Se contiver "hospital" no nome, ainda pode ser hospital
                if (!nameLower.includes('hospital')) {
                    return false; // Rejeita: não é hospital
                }
            }
        }
        
        // PALAVRAS-CHAVE QUE INDICAM QUE É HOSPITAL (INCLUIR)
        const includeKeywords = [
            'hospital',
            'maternidade', // Maternidades são hospitais especializados
            'hsp', // Abreviação comum
            'hosp.', // Abreviação comum
        ];
        
        // Verificar se o nome contém palavras de inclusão
        let hasHospitalKeyword = false;
        for (const keyword of includeKeywords) {
            if (nameLower.includes(keyword)) {
                hasHospitalKeyword = true;
                break;
            }
        }
        
        // Validação do tipo healthcare
        const validHealthcareTypes = ['hospital', 'maternity'];
        const isValidHealthcareType = validHealthcareTypes.includes(healthcareType);
        
        // Validação do amenity (deve ser hospital)
        const isValidAmenity = amenity === 'hospital';
        
        // REGRA: Deve ter "hospital" no nome OU ser do tipo hospital no healthcare OU ter amenity=hospital
        // Se tiver palavra de exclusão E não tiver "hospital" no contexto, rejeita
        const hasExclusionWithoutHospital = excludeKeywords.some(kw => nameLower.includes(kw)) && !hasHospitalKeyword;
        
        if (hasExclusionWithoutHospital) {
            return false; // Rejeita: tem palavra de exclusão e não tem "hospital"
        }
        
        // Aceita se: tem palavra de inclusão OU é do tipo hospital no healthcare OU tem amenity=hospital
        return hasHospitalKeyword || isValidHealthcareType || isValidAmenity;
    }
    
    /**
     * ========================================
     * VALIDAÇÃO DE INFRAESTRUTURA DE MATERNIDADE
     * ========================================
     * NOVA ESTRATÉGIA: Lista Negra (Exclusão) em vez de Inclusão Estrita
     * 
     * REGRA: Aceitar por padrão hospitais gerais e bloquear apenas especializados que não atendem parto.
     * 
     * Lógica:
     * 1. PRIORIDADE ALTA: Aceitar se contém indicadores de maternidade (confirmação explícita)
     * 2. PADRÃO: Aceitar "Hospital Geral" ou apenas "Hospital" (presumimos que hospitais gerais atendem partos ou estabilizam melhor)
     * 3. BLOQUEAR: Excluir hospitais especializados que NÃO atendem parto (Lista Negra)
     * 
     * @param {Object} tags - Tags do elemento OSM
     * @param {string} hospitalName - Nome do estabelecimento
     * @param {string} specialty - Especialidade do healthcare
     * @param {string} healthcare - Tipo de healthcare
     * @returns {{accepted: boolean, explicit: boolean}} - Objeto com accepted (aceita/bloqueia) e explicit (confirmação explícita ou dedução)
     */
    validateMaternityInfrastructure(tags, hospitalName, specialty, healthcare) {
        const nameLower = (hospitalName || '').toLowerCase();
        const specialtyLower = (specialty || '').toLowerCase();
        const healthcareLower = (healthcare || '').toLowerCase();
        const healthcareSpeciality = (tags?.['healthcare:speciality'] || '').toLowerCase();
        
        // ========================================
        // PRIORIDADE ALTA: Indicadores explícitos de maternidade (aceita imediatamente)
        // ========================================
        const maternityKeywords = [
            'maternidade', 'maternity',
            'obstetrícia', 'obstetrics',
            'ala maternal', 'ala de maternidade',
            'mulher', 'women', 'saúde da mulher',
            'ginecologia', 'gynaecology', 'gynecology',
            'parto', 'birth', 'centro de parto',
        ];
        
        // Verificar indicadores de maternidade (PRIORIDADE ALTA)
        const hasMaternityIndicator = 
            maternityKeywords.some(kw => nameLower.includes(kw)) ||
            maternityKeywords.some(kw => specialtyLower.includes(kw)) ||
            maternityKeywords.some(kw => healthcareLower.includes(kw)) ||
            maternityKeywords.some(kw => healthcareSpeciality.includes(kw));
        
        if (hasMaternityIndicator) {
            return { accepted: true, explicit: true }; // Aceita imediatamente - confirmação explícita
        }
        
        // ========================================
        // LISTA NEGRA: Especialidades que NÃO atendem parto (bloquear)
        // ========================================
        // IMPORTANTE: Inclui variações, abreviações e termos sem acento para evitar falsos positivos
        const blacklistSpecialties = [
            // Oftalmologia
            'oftalmologia', 'ophthalmology', 'olhos', 'eyes', 'ocular', 'oftalmo',
            
            // Cardiologia
            'cardiologia', 'cardiology', 'cardíaco', 'cardiac', 'coracao', 'coração', 'cardio',
            
            // Oncologia
            'oncologia', 'oncology', 'câncer', 'cancer', 'onco',
            
            // Ortopedia (ATUALIZADO: inclui variações e abreviações)
            'ortopedia', 'orthopedics', 'ortopédico', 'orthopedic', 'orto', 'trauma', 'traumatologia', 'fraturas', 'acidentados',
            
            // Psiquiatria
            'psiquiatria', 'psychiatry', 'psiquiátrico', 'psychiatric',
            
            // Cirurgia Plástica/Estética (ATUALIZADO: inclui variações)
            'plástica', 'plastic', 'cirurgia plástica', 'plastic surgery', 'plastica', 'estetica', 'estética', 'lipo', 'lipoaspiração', 'lipoaspiracao',
            
            // Day Hospital (geralmente cirurgias pequenas, não atende parto)
            'day hospital', 'day-hospital', 'day',
            
            // Dermatologia
            'dermatologia', 'dermatology',
            
            // Neurologia
            'neurologia', 'neurology', 'neurológico', 'neurological',
            
            // Urologia / Rim / Renal
            'urologia', 'urology', 'rim', 'renal', 'nefrologia', 'nephrology',
            
            // Otorrino
            'otorrino', 'otorhinolaryngology', 'ouvido', 'ear', 'nose', 'garganta', 'throat',
        ];
        
        // Verificar se contém termos da lista negra usando WORD BOUNDARIES (\b)
        // CRÍTICO: Usar Regex com \b para evitar falsos positivos como "Porto Alegre" ou "Hortolândia"
        const hasBlacklistedSpecialty = 
            blacklistSpecialties.some(term => {
                // Escapa caracteres especiais do termo para uso seguro em Regex
                const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                // Cria regex com word boundaries para verificar palavra inteira
                const regex = new RegExp(`\\b${escapedTerm}\\b`, 'i');
                return regex.test(nameLower) || 
                       regex.test(specialtyLower) || 
                       regex.test(healthcareLower) || 
                       regex.test(healthcareSpeciality);
            });
        
        if (hasBlacklistedSpecialty) {
            return { accepted: false, explicit: false }; // BLOQUEIA: Hospital especializado que não atende parto
        }
        
        // ========================================
        // PADRÃO: Aceitar hospitais gerais (presumimos que atendem partos ou estabilizam melhor)
        // ========================================
        // Se chegou aqui, não tem indicador explícito de maternidade, mas também não está na lista negra
        // Presumimos que é um "Hospital Geral" e aceitamos por padrão (dedução)
        return { accepted: true, explicit: false }; // Aceito por dedução (não é explícito, mas passou na lista negra)
    }
    
    calculateHospitalScore(tags, hospitalName) {
        /** Calcula score baseado na completude das informações */
        let score = 0;
        if (hospitalName && hospitalName.trim() !== '') score += 10;
        if (tags?.['addr:street']) score += 5;
        if (tags?.['addr:housenumber']) score += 2;
        if (tags?.['addr:city']) score += 3;
        if (tags?.['phone'] || tags?.['contact:phone']) score += 5;
        if (tags?.['website'] || tags?.['contact:website']) score += 3;
        return score;
    }
    
    deduplicateHospitals(hospitals) {
        /** Remove hospitais duplicados baseado em proximidade e nome similar */
        const unique = [];
        for (const hospital of hospitals) {
            let isDuplicate = false;
            for (const existing of unique) {
                const distance = this.calculateDistance(
                    hospital.lat, hospital.lon,
                    existing.lat, existing.lon
                );
                if (distance < 100) { // Menos de 100m
                    const similarity = this.calculateNameSimilarity(hospital.name, existing.name);
                    if (similarity > 0.7) {
                        isDuplicate = true;
                        // Prioriza: Maternos COM SUS > Maternos > Com SUS > Outros
                        const hospitalPriority = (hospital.isMaternity && hospital.acceptsSUS ? 3 : 
                                                  hospital.isMaternity ? 2 : 
                                                  hospital.acceptsSUS ? 1 : 0);
                        const existingPriority = (existing.isMaternity && existing.acceptsSUS ? 3 : 
                                                  existing.isMaternity ? 2 : 
                                                  existing.acceptsSUS ? 1 : 0);
                        if (hospitalPriority > existingPriority) {
                            const index = unique.indexOf(existing);
                            unique[index] = hospital;
                        }
                        break;
                    }
                }
            }
            if (!isDuplicate) {
                unique.push(hospital);
            }
        }
        return unique;
    }
    
    calculateNameSimilarity(name1, name2) {
        /** Calcula similaridade entre dois nomes */
        const words1 = name1.toLowerCase().split(/\s+/);
        const words2 = name2.toLowerCase().split(/\s+/);
        const commonWords = words1.filter(w => words2.includes(w));
        return commonWords.length / Math.max(words1.length, words2.length);
    }
    
    /**
     * Sanitiza string para exibição elegante (remove CAIXA ALTA excessiva, normaliza espaços)
     */
    sanitizeString(str) {
        if (!str || typeof str !== 'string') return '';
        
        // Remove espaços múltiplos
        str = str.replace(/\s+/g, ' ').trim();
        
        // Se a string está toda em CAIXA ALTA (exceto palavras curtas), converte para Title Case
        const isAllCaps = str === str.toUpperCase() && str.length > 3;
        if (isAllCaps) {
            // Converte para Title Case, mas preserva siglas conhecidas
            str = str.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
            // Preserva siglas comuns
            str = str.replace(/\b(Sus|SUS|UBS|UPA|SAMU|CRO|CRM)\b/gi, (match) => match.toUpperCase());
        }
        
        return str;
    }
    
    /**
     * Sanitiza número de telefone para link tel: (remove espaços, parênteses, traços)
     */
    sanitizePhone(phone) {
        if (!phone || typeof phone !== 'string') return '';
        // Remove tudo exceto números e +
        return phone.replace(/[^\d+]/g, '');
    }
    
    /**
     * Formata nome do hospital para exibição elegante
     */
    formatHospitalName(name) {
        if (!name) return 'Hospital';
        const sanitized = this.sanitizeString(name);
        return this.escapeHtml(sanitized);
    }
    
    /**
     * Cria badge com fallback seguro (nunca retorna badge vazio)
     */
    createBadge(type, text, icon = '') {
        if (!text || !type) return '';
        
        const iconHtml = icon ? `<i class="${icon}"></i> ` : '';
        const classes = {
            'sus': 'hospital-badge-sus',
            'maternity': 'hospital-badge-maternity',
            'emergency': 'hospital-badge-emergency'
        };
        
        return `<span class="${classes[type]}">${iconHtml}${this.escapeHtml(text)}</span>`;
    }
    
    /**
     * Copia texto para área de transferência
     */
    async copyToClipboard(text) {
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
                return true;
            } else {
                // Fallback para navegadores antigos
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.opacity = '0';
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return true;
            }
        } catch (error) {
            console.error('Erro ao copiar:', error);
            return false;
        }
    }
    
    displayHospitals(hospitals) {
        if (!this.hospitalsList) return;
        
        if (!hospitals || hospitals.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Filtra apenas hospitais com informações completas (nome, endereço, telefone)
        const completeHospitals = hospitals.filter(h => {
            const hasName = h.name && h.name.trim() !== '' && h.name !== 'Hospital';
            const hasAddress = h.address && h.address.trim() !== '';
            const hasPhone = h.phone && h.phone.trim() !== '';
            return hasName && hasAddress && hasPhone;
        });
        
        // Ordena: 1) Hospitais com ala maternal primeiro, 2) Por distância (mais próximo primeiro)
        const sortedHospitals = [...completeHospitals].sort((a, b) => {
            // Prioridade 1: Hospitais com ala maternal primeiro
            if (a.isMaternity && !b.isMaternity) return -1;
            if (!a.isMaternity && b.isMaternity) return 1;
            
            // Prioridade 2: Entre maternos ou não-maternos, ordena por distância (mais próximo primeiro)
            return a.distance - b.distance;
        });
        
        if (sortedHospitals.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Renderização otimizada: cria fragmento para melhor performance
        const fragment = document.createDocumentFragment();
        const container = document.createElement('div');
        // Conta hospitais com confirmação explícita vs dedução
        const explicitCount = sortedHospitals.filter(h => h.isMaternityExplicit === true).length;
        const generalCount = sortedHospitals.filter(h => h.isMaternityExplicit === false).length;
        
        let messageText = '';
        if (explicitCount > 0 && generalCount > 0) {
            messageText = `Encontrados ${sortedHospitals.length} hospital(is) próximo(s): ${explicitCount} com Ala de Maternidade confirmada e ${generalCount} hospital(is) geral(is).`;
        } else if (explicitCount > 0) {
            messageText = `Encontrados ${sortedHospitals.length} hospital(is) com Ala de Maternidade confirmada próximo(s):`;
        } else {
            messageText = `Encontrados ${sortedHospitals.length} hospital(is) geral(is) próximo(s) (atendimento provável):`;
        }
        
        container.innerHTML = `<p style="margin-bottom: var(--sophia-spacing-md); color: var(--sophia-text-secondary);">${messageText}</p>`;
        
        sortedHospitals.forEach((hospital, index) => {
            const distanceKm = (hospital.distance / 1000).toFixed(1);
            const badges = [];
            
            // Badge Pronto Socorro
            if (hospital.isEmergency === true) {
                badges.push(this.createBadge('emergency', 'Pronto Socorro', 'fas fa-ambulance'));
            }
            
            // Sanitiza dados
            const hospitalName = hospital.name || 'Hospital';
            const sanitizedPhone = hospital.phone ? this.sanitizePhone(hospital.phone) : '';
            const sanitizedAddress = hospital.address ? this.sanitizeString(hospital.address) : '';
            const sanitizedStreet = hospital.street ? this.sanitizeString(hospital.street) : '';
            const sanitizedHouseNumber = hospital.houseNumber ? this.sanitizeString(hospital.houseNumber) : '';
            
            // Identifica se é público ou privado
            const publicPrivateTag = hospital.isPublic ? 
                '<span class="hospital-badge-sus hospital-tag-public" style="display: inline-block; background: #4CAF50; color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Provável SUS/Público</span>' :
                '<span class="hospital-tag-private" style="display: inline-block; background: #FF9800; color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Provável Privado</span>';
            
            // Badge de Maternidade: Diferenciação entre Certeza Explícita e Dedução
            let maternityMessage = '';
            if (hospital.isMaternityExplicit === true) {
                // Badge Verde (✅ Confirmada): Apenas se o hospital tiver passado pela regra de Inclusão Explícita
                maternityMessage = `
                    <div class="hospital-maternity-info" style="background: rgba(76, 175, 80, 0.15); border-left: 3px solid #4CAF50; padding: 0.75rem; margin-bottom: 0.75rem; border-radius: 6px; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-check-circle" style="color: #4CAF50; font-size: 1rem;"></i>
                        <span style="color: #2E7D32; font-weight: 600; font-size: 0.9rem;">✅ Ala de Maternidade Confirmada</span>
                    </div>
                `;
            } else {
                // Badge Azul/Neutro (ℹ️ Hospital Geral): Se o hospital passou apenas porque não caiu na lista negra
                maternityMessage = `
                    <div class="hospital-maternity-info" style="background: rgba(33, 150, 243, 0.15); border-left: 3px solid #2196F3; padding: 0.75rem; margin-bottom: 0.75rem; border-radius: 6px; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-info-circle" style="color: #2196F3; font-size: 1rem;"></i>
                        <span style="color: #1565C0; font-weight: 600; font-size: 0.9rem;">ℹ️ Hospital Geral (Atendimento Provável)</span>
                    </div>
                `;
            }
            
            // Aviso de segurança
            const safetyWarning = `
                <div class="hospital-safety-warning" style="background: #fff3cd; border-left: 3px solid #ffb703; padding: 0.75rem; margin-bottom: 0.75rem; border-radius: 6px;">
                    <i class="fas fa-exclamation-triangle" style="color: #ffb703; margin-right: 0.5rem;"></i>
                    <span style="color: #856404; font-weight: 600; font-size: 0.85rem;">⚠️ Recomendamos ligar para confirmar se há plantão obstétrico disponível no momento</span>
                </div>
            `;
            
            // Monta endereço formatado (rua e número separados)
            let formattedAddress = '';
            if (sanitizedStreet) {
                formattedAddress = sanitizedStreet;
                if (sanitizedHouseNumber) {
                    formattedAddress += `, ${sanitizedHouseNumber}`;
                }
                if (hospital.neighborhood) {
                    formattedAddress += ` - ${this.escapeHtml(hospital.neighborhood)}`;
                }
                if (hospital.city) {
                    formattedAddress += `, ${this.escapeHtml(hospital.city)}`;
                }
                if (hospital.state) {
                    formattedAddress += ` - ${this.escapeHtml(hospital.state)}`;
                }
            } else {
                formattedAddress = sanitizedAddress;
            }
            
            // Monta query para Google Maps usando nome + endereço
            const mapQuery = encodeURIComponent(`${hospitalName} ${formattedAddress}`);
            
            const cardHtml = `
                <div class="hospital-card" data-index="${index}">
                    <div class="hospital-header">
                        <div class="hospital-header-top">
                            <h4 class="hospital-name">${this.escapeHtml(hospitalName)}</h4>
                        </div>
                        <div class="hospital-header-bottom">
                            <div class="hospital-header-tags">
                                ${publicPrivateTag}
                            </div>
                            <span class="hospital-distance">${distanceKm} km</span>
                        </div>
                    </div>
                    ${badges.length > 0 ? `<div class="hospital-badges">${badges.join('')}</div>` : ''}
                    ${maternityMessage}
                    ${safetyWarning}
                    <div class="hospital-info">
                        ${formattedAddress ? `
                            <p class="hospital-address">
                                <i class="fas fa-map-marker-alt"></i> 
                                <span>${this.escapeHtml(formattedAddress)}</span>
                                <button class="hospital-copy-btn" 
                                        data-copy="${this.escapeHtml(formattedAddress)}" 
                                        aria-label="Copiar endereço"
                                        title="Copiar endereço">
                                    <i class="fas fa-copy"></i>
                                </button>
                            </p>
                        ` : ''}
                        ${sanitizedPhone ? `
                            <p class="hospital-phone">
                                <i class="fas fa-phone"></i> 
                                <a href="tel:${sanitizedPhone}" 
                                   class="hospital-phone-link" 
                                   data-phone="${sanitizedPhone}">${this.escapeHtml(hospital.phone)}</a>
                            </p>
                        ` : ''}
                        ${hospital.website ? `
                            <p class="hospital-website">
                                <i class="fas fa-globe"></i> 
                                <a href="${hospital.website}" target="_blank" rel="noopener" class="hospital-website-link">${this.escapeHtml(hospital.website)}</a>
                            </p>
                        ` : ''}
                    </div>
                    <div class="hospital-actions">
                        ${sanitizedPhone ? `
                            <a href="tel:${sanitizedPhone}" 
                               class="btn-sophia btn-sophia-compact hospital-call-btn hospital-call-btn-primary"
                               data-phone="${sanitizedPhone}"
                               style="background: var(--sophia-emergency); color: white; font-weight: 700; flex: 1; min-width: 120px;">
                                <i class="fas fa-phone"></i> Ligar
                            </a>
                        ` : ''}
                        <a href="https://www.google.com/maps/dir/?api=1&destination=${hospital.lat},${hospital.lon}" 
                           target="_blank" 
                           class="btn-sophia btn-sophia-compact hospital-route-btn">
                            <i class="fas fa-route"></i> Rota
                        </a>
                        <a href="https://www.google.com/maps/search/?api=1&query=${mapQuery}" 
                           target="_blank" 
                           class="btn-sophia btn-sophia-compact hospital-map-btn">
                            <i class="fas fa-map"></i> Ver no Mapa
                        </a>
                    </div>
                    </div>
                `;
            
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = cardHtml;
            container.appendChild(tempDiv.firstElementChild);
        });
        
        fragment.appendChild(container);
        this.hospitalsList.innerHTML = '';
        this.hospitalsList.appendChild(fragment);
        
        // Adiciona event listeners para botões de copiar e feedback visual
        this.attachHospitalEventListeners();
    }
    
    /**
     * Mostra estado vazio com sugestão de SAMU
     */
    showEmptyState() {
        if (!this.hospitalsList) return;
        
        this.hospitalsList.innerHTML = `
            <div class="hospital-empty-state">
                <div class="hospital-empty-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3 class="hospital-empty-title">Nenhum hospital encontrado próximo</h3>
                <p class="hospital-empty-message">
                    Não foi possível encontrar hospitais próximos à sua localização.
                </p>
                <div class="hospital-empty-actions">
                    <a href="tel:192" class="btn-sophia hospital-emergency-btn">
                        <i class="fas fa-phone-alt"></i> Ligar SAMU (192)
                    </a>
                    <button class="btn-sophia hospital-retry-btn" onclick="window.chatApp?.findNearbyHospitals()">
                        <i class="fas fa-redo"></i> Tentar Novamente
                    </button>
                </div>
            </div>
        `;
    }
    
    /**
     * Carrega e exibe o módulo de triagem de sintomas
     */
    async showSintomasTriagem() {
        try {
            // Carrega dados dos sintomas
            const response = await fetch('/static/data/sintomas_puerperio.json');
            const data = await response.json();
            
            // Esconde welcome message e mostra recursos
            if (this.welcomeMessage) {
                this.welcomeMessage.style.display = 'none';
            }
            
            if (this.resourcesModal) {
                this.resourcesTitle.textContent = '⚠️ Sinais de Alerta';
                this.resourcesContent.innerHTML = this.renderSintomasTriagem(data.sintomas);
                this.resourcesModal.classList.add('show');
            }
        } catch (error) {
            this.error('Erro ao carregar sintomas:', error);
            alert('❌ Erro ao carregar sinais de alerta. Por favor, tente novamente.');
        }
    }
    
    /**
     * Renderiza a interface de triagem de sintomas
     */
    renderSintomasTriagem(sintomas) {
        // Agrupa por gravidade
        const criticos = sintomas.filter(s => s.gravidade === 'critico');
        const medios = sintomas.filter(s => s.gravidade === 'medio');
        const baixos = sintomas.filter(s => s.gravidade === 'baixo');
        
        let html = `
            <div class="sintomas-triagem-container">
                <p class="sintomas-intro">Selecione os sintomas que você está sentindo. Baseado nas suas respostas, te orientaremos sobre o que fazer.</p>
        `;
        
        // Sintomas Críticos
        if (criticos.length > 0) {
            html += `
                <div class="sintomas-section">
                    <h3 class="sintomas-section-title sintomas-critico">
                        <i class="fas fa-exclamation-circle"></i> Sintomas Críticos
                    </h3>
                    <div class="sintomas-grid">
                        ${criticos.map(s => this.renderSintomaCard(s)).join('')}
            </div>
            </div>
        `;
        }
        
        // Sintomas Médios
        if (medios.length > 0) {
            html += `
                <div class="sintomas-section">
                    <h3 class="sintomas-section-title sintomas-medio">
                        <i class="fas fa-exclamation-triangle"></i> Atenção
                    </h3>
                    <div class="sintomas-grid">
                        ${medios.map(s => this.renderSintomaCard(s)).join('')}
                    </div>
                </div>
            `;
        }
        
        // Sintomas Baixos
        if (baixos.length > 0) {
            html += `
                <div class="sintomas-section">
                    <h3 class="sintomas-section-title sintomas-baixo">
                        <i class="fas fa-info-circle"></i> Monitorar
                    </h3>
                    <div class="sintomas-grid">
                        ${baixos.map(s => this.renderSintomaCard(s)).join('')}
                    </div>
                    </div>
                `;
        }
        
        html += `</div>`;
        return html;
    }
    
    /**
     * Renderiza um card de sintoma individual
     */
    renderSintomaCard(sintoma) {
        const gravidadeClass = `sintoma-${sintoma.gravidade}`;
        const badgeClass = sintoma.gravidade === 'critico' ? 'sintoma-badge-critico' : 
                          sintoma.gravidade === 'medio' ? 'sintoma-badge-medio' : 
                          'sintoma-badge-baixo';
        
        return `
            <div class="sintoma-card ${gravidadeClass}" data-sintoma-id="${sintoma.id}">
                <div class="sintoma-header">
                    <h4 class="sintoma-titulo">${this.escapeHtml(this.sanitizeString(sintoma.titulo))}</h4>
                    <span class="sintoma-badge ${badgeClass}">${this.getGravidadeLabel(sintoma.gravidade)}</span>
                    </div>
                <p class="sintoma-pergunta">${this.escapeHtml(this.sanitizeString(sintoma.pergunta))}</p>
                <div class="sintoma-actions">
                    <button class="btn-sophia sintoma-btn-yes" data-sintoma-id="${sintoma.id}" data-resposta="sim">
                        <i class="fas fa-check"></i> Sim
                    </button>
                    <button class="btn-sophia sintoma-btn-no" data-sintoma-id="${sintoma.id}" data-resposta="nao">
                        <i class="fas fa-times"></i> Não
                    </button>
                    </div>
            </div>
        `;
    }
    
    /**
     * Retorna label de gravidade
     */
    getGravidadeLabel(gravidade) {
        const labels = {
            'critico': 'Crítico',
            'medio': 'Atenção',
            'baixo': 'Monitorar'
        };
        return labels[gravidade] || 'Monitorar';
    }
    
    /**
     * Processa resposta do sintoma e exibe recomendação
     */
    async processarRespostaSintoma(sintomaId, resposta) {
        try {
            // Carrega dados novamente para garantir que temos o sintoma completo
            const response = await fetch('/static/data/sintomas_puerperio.json');
            const data = await response.json();
            const sintoma = data.sintomas.find(s => s.id === sintomaId);
            
            if (!sintoma) {
                this.error('Sintoma não encontrado:', sintomaId);
                return;
            }
            
            // Se resposta for "Sim" e gravidade for crítica, mostra ação imediata
            if (resposta === 'sim' && sintoma.gravidade === 'critico') {
                this.mostrarRecomendacaoCritica(sintoma);
            } else if (resposta === 'sim' && sintoma.gravidade === 'medio') {
                this.mostrarRecomendacaoMedia(sintoma);
            } else if (resposta === 'sim' && sintoma.gravidade === 'baixo') {
                this.mostrarRecomendacaoBaixa(sintoma);
            } else {
                // Resposta "Não" - apenas confirma
                this.mostrarFeedbackNegativo(sintoma);
            }
            
            // Salva no histórico local
            this.salvarTriagemHistorico(sintoma, resposta);
            
        } catch (error) {
            this.error('Erro ao processar resposta:', error);
        }
    }
    
    /**
     * Mostra recomendação para sintoma crítico
     */
    mostrarRecomendacaoCritica(sintoma) {
        const html = `
            <div class="sintoma-resultado sintoma-resultado-critico">
                <div class="sintoma-resultado-icon">
                    <i class="fas fa-exclamation-circle"></i>
                </div>
                <h3 class="sintoma-resultado-titulo">${this.escapeHtml(sintoma.recomendacao)}</h3>
                <p class="sintoma-resultado-descricao">${this.escapeHtml(sintoma.descricao)}</p>
                <div class="sintoma-resultado-acoes">
                    ${sintoma.acoes.map(acao => {
                        if (acao.tipo === 'hospital') {
                            return `
                                <button class="btn-sophia sintoma-acao-btn sintoma-acao-hospital" 
                                        onclick="window.chatApp?.findNearbyHospitals()">
                                    <i class="fas fa-hospital"></i> ${this.escapeHtml(acao.texto)}
                                </button>
                            `;
                        } else if (acao.tipo === 'telefone') {
                            const phoneSanitized = this.sanitizePhone(acao.numero);
                            return `
                                <a href="tel:${phoneSanitized}" class="btn-sophia sintoma-acao-btn sintoma-acao-telefone">
                                    <i class="fas fa-phone-alt"></i> ${this.escapeHtml(acao.texto)}
                                </a>
                            `;
                        }
                        return '';
                    }).join('')}
                    </div>
                    </div>
        `;
        
        // Substitui o conteúdo do modal
        if (this.resourcesContent) {
            this.resourcesContent.innerHTML = html;
        }
    }
    
    /**
     * Mostra recomendação para sintoma médio
     */
    mostrarRecomendacaoMedia(sintoma) {
        const html = `
            <div class="sintoma-resultado sintoma-resultado-medio">
                <div class="sintoma-resultado-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                    </div>
                <h3 class="sintoma-resultado-titulo">${this.escapeHtml(sintoma.recomendacao)}</h3>
                <p class="sintoma-resultado-descricao">${this.escapeHtml(sintoma.descricao)}</p>
                <div class="sintoma-resultado-acoes">
                    ${sintoma.acoes.map(acao => {
                        if (acao.tipo === 'hospital') {
                            return `
                                <button class="btn-sophia sintoma-acao-btn" 
                                        onclick="window.chatApp?.findNearbyHospitals()">
                                    <i class="fas fa-hospital"></i> ${this.escapeHtml(acao.texto)}
                                </button>
                            `;
                        } else if (acao.tipo === 'telefone') {
                            const phoneSanitized = this.sanitizePhone(acao.numero);
                            return `
                                <a href="tel:${phoneSanitized}" class="btn-sophia sintoma-acao-btn">
                                    <i class="fas fa-phone-alt"></i> ${this.escapeHtml(acao.texto)}
                                </a>
                            `;
                        }
                        return '';
                    }).join('')}
                    </div>
                <button class="btn-sophia sintoma-voltar-btn" onclick="window.chatApp?.showSintomasTriagem()">
                    <i class="fas fa-arrow-left"></i> Voltar aos Sintomas
                </button>
                </div>
            `;
        
        if (this.resourcesContent) {
            this.resourcesContent.innerHTML = html;
        }
    }
    
    /**
     * Mostra recomendação para sintoma baixo
     */
    mostrarRecomendacaoBaixa(sintoma) {
        const html = `
            <div class="sintoma-resultado sintoma-resultado-baixo">
                <div class="sintoma-resultado-icon">
                    <i class="fas fa-info-circle"></i>
                    </div>
                <h3 class="sintoma-resultado-titulo">${this.escapeHtml(sintoma.recomendacao)}</h3>
                <p class="sintoma-resultado-descricao">${this.escapeHtml(sintoma.descricao)}</p>
                <button class="btn-sophia sintoma-voltar-btn" onclick="window.chatApp?.showSintomasTriagem()">
                    <i class="fas fa-arrow-left"></i> Voltar aos Sintomas
                </button>
                </div>
            `;
        
        if (this.resourcesContent) {
            this.resourcesContent.innerHTML = html;
        }
    }
    
    /**
     * Mostra feedback para resposta negativa
     */
    mostrarFeedbackNegativo(sintoma) {
        // Feedback discreto - apenas confirma que não tem o sintoma
        const card = document.querySelector(`[data-sintoma-id="${sintoma.id}"]`);
        if (card) {
            card.classList.add('sintoma-respondido');
            const actions = card.querySelector('.sintoma-actions');
            if (actions) {
                actions.innerHTML = '<p class="sintoma-feedback-positivo">✓ Obrigada por responder. Continue monitorando.</p>';
            }
        }
    }
    
    /**
     * Salva triagem no histórico local
     */
    salvarTriagemHistorico(sintoma, resposta) {
        try {
            const historico = JSON.parse(localStorage.getItem('sophia_triagem_historico') || '[]');
            historico.push({
                sintoma: sintoma.titulo,
                categoria: sintoma.categoria,
                gravidade: sintoma.gravidade,
                resposta: resposta,
                timestamp: new Date().toISOString()
            });
            
            // Mantém apenas últimos 50 registros
            if (historico.length > 50) {
                historico.shift();
            }
            
            localStorage.setItem('sophia_triagem_historico', JSON.stringify(historico));
        } catch (error) {
            this.error('Erro ao salvar histórico de triagem:', error);
        }
    }
    
    /* Função mostrarHistoricoTriagens() removida - botão "Ver meu Histórico" foi removido */
    
    /**
     * Limpa o histórico de triagens do localStorage
     */
    limparHistoricoTriagens() {
        try {
            const historico = JSON.parse(localStorage.getItem('sophia_triagem_historico') || '[]');
            
            if (historico.length === 0) {
                this.showNotification('Histórico vazio', 'Não há registros para limpar.', 'info');
                return;
            }
            
            // Confirmação amigável
            if (confirm(`Tem certeza que deseja limpar todo o histórico de triagens?\n\nVocê tem ${historico.length} registro(s) salvo(s). Esta ação não pode ser desfeita.`)) {
                localStorage.removeItem('sophia_triagem_historico');
                this.showNotification('Histórico limpo', 'Todos os registros de triagem foram removidos com sucesso.', 'success');
                
                // Feedback visual no botão (se existir)
                if (this.sidebarBtnClearMemory) {
                    const textoOriginal = this.sidebarBtnClearMemory.innerHTML;
                    this.sidebarBtnClearMemory.innerHTML = '<i class="fas fa-check"></i> Limpo!';
                    this.sidebarBtnClearMemory.style.background = 'var(--sophia-pink-light, #F4A6A6)';
                    this.sidebarBtnClearMemory.style.color = '#ffffff';
                    
                    setTimeout(() => {
                        this.sidebarBtnClearMemory.innerHTML = textoOriginal;
                        this.sidebarBtnClearMemory.style.background = '';
                        this.sidebarBtnClearMemory.style.color = '';
                    }, 2000);
                }
            }
        } catch (error) {
            this.error('Erro ao limpar histórico de triagens:', error);
            this.showNotification('Erro', 'Não foi possível limpar o histórico. Tente novamente.', 'error');
        }
    }
    
    /**
     * Anexa event listeners para interações dos cards
     */
    attachHospitalEventListeners() {
        // Botões de copiar endereço
        const copyButtons = this.hospitalsList.querySelectorAll('.hospital-copy-btn');
        copyButtons.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const textToCopy = btn.getAttribute('data-copy');
                if (textToCopy) {
                    const success = await this.copyToClipboard(textToCopy);
                    if (success) {
                        // Feedback visual
                        btn.classList.add('copied');
                        btn.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(() => {
                            btn.classList.remove('copied');
                            btn.innerHTML = '<i class="fas fa-copy"></i>';
                        }, 2000);
                    }
                }
            });
        });
        
        // Botões de ligar - feedback visual
        const callButtons = this.hospitalsList.querySelectorAll('.hospital-call-btn, .hospital-phone-link');
        callButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Feedback visual imediato
                btn.classList.add('clicked');
                setTimeout(() => {
                    btn.classList.remove('clicked');
                }, 300);
            });
        });
    }
}

// Inicializa o chatbot quando a página carrega
// Tenta inicializar imediatamente se DOM já está pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChatApp);
} else {
    // DOM já está pronto, inicializa imediatamente
    initializeChatApp();
}

function initializeChatApp() {
    console.log('🚀 [INIT] Inicializando ChatbotPuerperio...');
    try {
        const chatbot = new ChatbotPuerperio();
        // Expõe globalmente para handlers inline
        window.chatApp = chatbot;
        console.log('✅ [INIT] chatApp exposto globalmente:', typeof window.chatApp);
        console.log('✅ [INIT] chatApp.handleInitialLogin disponível:', typeof window.chatApp.handleInitialLogin);
        
        // Verifica status da conexão periodicamente (apenas se já estiver logado)
        // Intervalo aumentado para 30s para reduzir requisições (otimização para ngrok)
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
        }, 30000); // Aumentado de 5s para 30s para reduzir carga no ngrok

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
        if (typeof initFeatureCarousel === 'function') {
            initFeatureCarousel();
        }
    } catch (error) {
        console.error('❌ [INIT] Erro ao inicializar ChatbotPuerperio:', error);
        window.chatApp = null;
    }
}

/**
 * Inicializa o carrossel de botões de recursos
 * Carrossel horizontal com 4 botões que desliza horizontalmente
 */
function initFeatureCarousel() {
    const track = document.getElementById('feature-carousel-track');
    const prevBtn = document.getElementById('feature-carousel-prev');
    const nextBtn = document.getElementById('feature-carousel-next');
    const dotsContainer = document.getElementById('feature-carousel-dots');
    
    if (!track || !prevBtn || !dotsContainer) {
        return; // Elementos não existem ainda (nextBtn é opcional)
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
            if (nextBtn) nextBtn.style.display = 'none';
            track.style.transform = 'translateX(0)'; // Reseta posição
            return;
        }

        // Mostra os controles
        dotsContainer.style.display = 'flex';
        prevBtn.style.display = 'flex';
        if (nextBtn) nextBtn.style.display = 'flex';

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
            if (nextBtn) nextBtn.disabled = true;
            return;
        }
        
        prevBtn.disabled = currentIndex === 0;
        if (nextBtn) nextBtn.disabled = currentIndex >= totalSlides - 1;
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
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);
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

