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
        
        // Flag para prevenir login duplicado
        this.isLoggingIn = false;
        
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
        // Timeout para evitar loading infinito se /api/user demorar (rede lenta, servidor travado)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);
        const opts = { credentials: 'include', signal: controller.signal };
        const userPromise = (typeof window !== 'undefined' && window.dedupedFetchJSON)
            ? window.dedupedFetchJSON('/api/user', opts).catch(() => null)
            : fetch('/api/user', opts).then(res => res.ok ? res.json() : null);
        userPromise
            .then(user => {
                clearTimeout(timeoutId);
                if (user) {
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
                } else {
                    // User not logged in, show login screen
                    // 401 / null é esperado quando não está logado - não é um erro
                    this.userLoggedIn = false;
                    this.currentUserName = null;
                    this.showLoginScreen();
                    
                    // Carrega histórico mesmo sem estar logado (para usuários anônimos)
                    // O userId já foi gerado no constructor e está salvo no localStorage
                    this.loadChatHistory();
                }
            })
            .catch((_error) => {
                clearTimeout(timeoutId);
                // Erro na requisição ou timeout - assume que não está logado
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
        // Evita execução múltipla
        if (this._initMainAppRunning) {
            this.log('⚠️ [INIT] initMainApp já está em execução, ignorando...');
            return;
        }
        this._initMainAppRunning = true;
        
        this.log('🚀 [INIT] initMainApp chamado');
        
        try {
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

              this.loadChatHistoryFromServer();
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
                // Recarrega agenda de vacinas (e alerta Dia D, se houver) após login
                if (window.vaccinationTimeline && typeof window.vaccinationTimeline.loadVaccinationData === 'function') {
                    window.vaccinationTimeline.loadVaccinationData();
                }
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
          } finally {
              // Libera flag após inicialização completa
              this._initMainAppRunning = false;
          }
        } catch (error) {
            this.error('❌ [INIT] Erro geral em initMainApp:', error);
            this._initMainAppRunning = false;
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
        // "Novo cadastro? Entre aqui" / "Já tem conta? Entre aqui"
        document.querySelectorAll('#login-screen .login-switch-link .link-button').forEach(btn => {
            if (btn.dataset.tab) btn.addEventListener('click', () => this.switchInitialTab(btn.dataset.tab));
        });
        
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
        
        // Reenviar link de verificação
        const resendVerificationLink = document.getElementById('resend-verification-link');
        if (resendVerificationLink) {
            resendVerificationLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.resendVerificationEmail();
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
            // Limpa o formulário de cadastro para evitar autofill com email do login
            var regEmail = document.getElementById('initial-register-email');
            var regName = document.getElementById('initial-register-name');
            var regPass = document.getElementById('initial-register-password');
            var regBaby = document.getElementById('initial-register-baby');
            if (regEmail) regEmail.value = '';
            if (regName) regName.value = '';
            if (regPass) regPass.value = '';
            if (regBaby) regBaby.value = '';
        }
    }
    
    async handleInitialLogin() {
        // Previne execução duplicada
        if (this.isLoggingIn) {
            this.log('⚠️ [LOGIN] Login já em progresso, ignorando chamada duplicada');
            return;
        }
        
        this.isLoggingIn = true;
        
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
                localStorage.removeItem('sophia_vaccine_banner_dismissed'); // Banner volta a aparecer no novo login
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
            // Fallback: no Safari/mobile ou quando fetch falha (ex.: ngrok), submete o form nativamente
            const form = document.getElementById('initial-login-form');
            if (form && form.action && form.method && form.action.indexOf('/auth/login') !== -1) {
                try {
                    form.submit();
                    return;
                } catch (e) {
                    this.error('Fallback form.submit falhou:', e);
                }
            }
            alert('❌ Erro ao fazer login. Tente novamente.');
        } finally {
            // Libera flag após 500ms para permitir nova tentativa
            setTimeout(() => {
                this.isLoggingIn = false;
            }, 500);
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
            const _response = await fetch('/api/logout', {
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
        const email = document.getElementById('initial-register-email').value.trim().toLowerCase();
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
                headers: {'Content-Type': 'application/json; charset=utf-8'},
                body: JSON.stringify(requestData)
            });
            
            this.log('[REGISTER] Status da resposta:', response.status);
            
            const data = await response.json();
            this.log('[REGISTER] Resposta do servidor:', data);
            
            if (response.ok) {
                // Mostra notificação de sucesso
                const msg = data.mensagem || (data.verification_sent
                    ? 'Verifique seu email para ativar sua conta. Um link foi enviado para ' + email
                    : 'Cadastro realizado. Use "Reenviar link de verificação" se não recebeu o email.');
                this.showNotification(
                    'Cadastro realizado! 🎉',
                    msg,
                    'success'
                );
                // Auto switch to login e preenche o email para login imediato
                this.switchInitialTab('login');
                const loginEmail = document.getElementById('initial-login-email');
                const loginPass = document.getElementById('initial-login-password');
                if (loginEmail) loginEmail.value = email;
                if (loginPass) { loginPass.value = ''; loginPass.focus(); }
            } else {
                // Mostra mensagem de erro específica do servidor
                const errorMessage = data.erro || data.mensagem || 'Erro ao cadastrar. Tente novamente.';
                this.error('[REGISTER] Erro:', errorMessage);
                
                // Se for erro 409 (email já existe), oferece opções
                if (response.status === 409) {
                    if (data.email_nao_verificado) {
                        // Email não verificado - oferece ir para "Esqueci minha senha"
                        this.showNotification(
                            'Email já cadastrado ⚠️',
                            errorMessage + '\n\nDeseja reenviar o link de verificação? Use "Esqueci minha senha".',
                            'error'
                        );
                        // Destaca o link "Esqueci minha senha" após 1 segundo
                        setTimeout(() => {
                            const forgotLink = document.getElementById('forgot-password-link');
                            if (forgotLink) {
                                forgotLink.style.border = '2px solid #ff8fa3';
                                forgotLink.style.animation = 'pulse 2s infinite';
                                forgotLink.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }
                        }, 1000);
                    } else {
                        // Email já verificado - sugere fazer login
                        this.showNotification(
                            'Email já cadastrado ✅',
                            errorMessage + '\n\nVocê já tem uma conta! Faça login.',
                            'error'
                        );
                        // Auto switch para login após 2 segundos
                        setTimeout(() => {
                            this.switchInitialTab('login');
                            const loginEmailInput = document.getElementById('initial-login-email');
                            if (loginEmailInput) {
                                loginEmailInput.value = email;
                                loginEmailInput.focus();
                            }
                        }, 2000);
                    }
                } else {
                    // Outros erros
                    this.showNotification(
                        'Erro no cadastro ⚠️',
                        errorMessage,
                        'error'
                    );
                }
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
        const onToggleSidebar = (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleSidebar();
        };
        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', onToggleSidebar);
        }
        if (this.menuToggleHeader) {
            this.menuToggleHeader.addEventListener('click', onToggleSidebar);
        }
        // Fallback: delegação em fase de captura para o botão do menu (garante abertura da sidebar mesmo com sobreposição)
        document.addEventListener('click', (e) => {
            const menuBtn = e.target.closest('#menu-toggle-header');
            if (!menuBtn) return;
            e.preventDefault();
            e.stopPropagation();
            this.toggleSidebar();
        }, true);
        
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
        
        // Header: botão de perfil (abre modal)
        const headerProfileBtn = document.getElementById('header-profile-btn');
        
        if (headerProfileBtn) {
            headerProfileBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
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
        const btnMyRegion = document.getElementById('btn-find-hospitals-my-region');
        if (btnMyRegion) {
            btnMyRegion.addEventListener('click', () => this.findNearbyHospitals());
        }
        const btnByRegion = document.getElementById('btn-find-hospitals-by-region');
        if (btnByRegion) {
            btnByRegion.addEventListener('click', () => this.findHospitalsByRegion());
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

        const maxChars = 2000;
        const count = this.messageInput.value ? this.messageInput.value.length : 0;
        this.charCount.textContent = `${count}/${maxChars}`;

        if (count > maxChars * 0.95) {
            this.charCount.style.color = '#e74c3c';
        } else if (count > maxChars * 0.8) {
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
                // Se backend usou fallback (ex.: Groq falhou), inclui request_id para suporte
                var respostaExibir = data.resposta;
                if (data.request_id) {
                    respostaExibir += '\n\n_(Se o problema persistir, informe este ID ao suporte: ' + data.request_id + ')_';
                }
                // Verifica se há alerta de risco emocional/suicídio (mostrar aviso visual acolhedor)
                if (data.mostrar_aviso_visual && data.alerta_ativo) {
                    this.showAvisoVisualRisco(data.nivel_risco);
                } else if (!data.alerta_ativo) {
                    // Se não há alerta ativo, esconde o aviso visual (usuário pode ter dito que está bem)
                    this.hideAvisoVisualRisco();
                }
                
                // Adiciona resposta do assistente (com streaming)
                await this.addMessage(respostaExibir, 'assistant', {
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
        
        // Resposta sempre instantânea (efeito de digitação desativado para priorizar rapidez no puerpério)
        messageTextElement.innerHTML = this.formatMessage(content);
        
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
                    const _time = msgEl.querySelector('.message-time')?.textContent || '';
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
            // Tenta /api/user-data; se 404, fallback para /api/user (compatível com build antigo)
            let response = await window.apiClient.get('/api/user-data').catch(() => null);
            if (!response || response.erro) {
                response = await window.apiClient.get('/api/user').catch(() => null);
            }
            const userName = (response && !response.erro && ((response.user && response.user.name) || response.name)) ? (response.user ? response.user.name : response.name) : null;
            const babyName = (response && !response.erro && ((response.baby_profile && response.baby_profile.name) || response.baby_name)) ? (response.baby_profile ? response.baby_profile.name : response.baby_name) : null;
            if (babyName) {
                subtitle.textContent = `Apoio para a mamãe de ${babyName}`;
                this.babyName = babyName;
            } else if (userName) {
                this.userName = userName;
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
                    { text: 'Ver Unidades de Apoio Próximas', action: () => { this.findNearbyHospitals(); } },
                    { text: 'Preciso de um incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } }
                ],
                'cansaço_extremo_critico': [
                    { text: 'Ver Unidades de Apoio Próximas', action: () => { this.findNearbyHospitals(); } },
                    { text: 'Dicas de descanso rápido', action: () => { this.sendMessageText('Preciso de dicas de descanso rápido'); } },
                    { text: 'Preciso de um incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } }
                ],
                'celebração': [
                    { text: 'Contar uma conquista', action: () => { this.sendMessageText('Quero compartilhar uma conquista'); } },
                    { text: 'O que fazer hoje?', action: () => { this.sendMessageText('O que fazer hoje?'); } }
                ],
                'ansiedade': [
                    { text: 'Preciso de apoio emocional', action: () => { this.sendMessageText('Preciso de apoio emocional'); } },
                    { text: 'Ver Unidades de Apoio Próximas', action: () => { this.findNearbyHospitals(); } },
                    { text: 'Frase de incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } }
                ],
                'tristeza': [
                    { text: 'Preciso de apoio emocional', action: () => { this.sendMessageText('Preciso de apoio emocional'); } },
                    { text: 'Ver Unidades de Apoio Próximas', action: () => { this.findNearbyHospitals(); } },
                    { text: 'Buscar ajuda profissional', action: () => { this.openEmergencyNumbersModal(); } }
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
                    { text: 'Ver Unidades de Apoio Próximas', action: () => { this.findNearbyHospitals(); } },
                    { text: 'Números de Emergência', action: () => { this.openEmergencyNumbersModal(); } },
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
            } else if (contentLower.includes('cansada') || contentLower.includes('exausta') || contentLower.includes('sobrecarregada')) {
                quickReplies = [
                    { text: 'Ver Unidades de Apoio Próximas', action: () => { this.findNearbyHospitals(); } },
                    { text: 'Preciso de um incentivo', action: () => { this.sendMessageText('Preciso de um incentivo'); } },
                    { text: 'Como cuidar de mim?', action: () => { this.sendMessageText('Como cuidar de mim?'); } }
                ];
            } else if (contentLower.includes('hospital') || contentLower.includes('emergência') || contentLower.includes('emergencia') || contentLower.includes('unidade') || contentLower.includes('sintoma')) {
                quickReplies = [
                    { text: 'Ver Unidades de Apoio Próximas', action: () => { this.findNearbyHospitals(); } },
                    { text: 'Números de Emergência', action: () => { this.openEmergencyNumbersModal(); } },
                    { text: 'Preciso de apoio', action: () => { this.sendMessageText('Preciso de apoio'); } }
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
        const sidebar = document.getElementById('sidebar');
        if (!sidebar || !sidebar.classList) {
            this.error('❌ [SIDEBAR] Sidebar não encontrado');
            return;
        }
        this.log('🔍 [SIDEBAR] toggleSidebar chamado');
        
        // Usa a classe .open para decidir (evita conflito com translateY no mobile)
        const isActuallyOpen = sidebar.classList.contains('open');
        
        const isOpening = !isActuallyOpen;
        
        if (isOpening) {
            sidebar.classList.add('open');
            this.log('✅ [SIDEBAR] ABRINDO');
        } else {
            sidebar.classList.remove('open');
            this.log('✅ [SIDEBAR] FECHANDO');
        }
        
        if (document.body && document.body.classList) {
            if (isOpening) {
                document.body.classList.add('sidebar-open');
                this.playSound(500, 150, 'sine');
                sidebar.style.setProperty('z-index', '2147483647', 'important');
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
        let _rotationTimeout;

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

                    _rotationTimeout = setTimeout(rotateMessage, intervalMs);
                }, fadeDuration);
            } catch (error) {
                this.warn('Erro ao atualizar mensagem rotativa:', error);
            }
        };

        _rotationTimeout = setTimeout(rotateMessage, intervalMs);
    }

    initFeelingButtons() {
        const feelingButtons = document.querySelectorAll('.feeling-btn');
        const feelingFeedback = document.getElementById('feeling-feedback');
        // Mensagens predefinidas enviadas para a IA (não respostas locais)
        const feelingMessages = {
            'cansada': 'Sophia, eu estou exausta',
            'feliz': 'Sophia, hoje me sinto em paz',
            'ansiosa': 'Sophia, eu estou sobrecarregada',
            'confusa': 'Sophia, eu estou confusa',
            'triste': 'Sophia, eu me sinto para baixo hoje',
            'gratidao': 'Sophia, hoje me sinto grata'
        };

        feelingButtons.forEach(btn => {
            btn.addEventListener('click', (_e) => {
                // Feedback visual imediato
                btn.classList.add('clicked');
                btn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    btn.classList.remove('clicked');
                    btn.style.transform = '';
                }, 200);

                const feeling = btn.dataset.feeling;
                const message = feelingMessages[feeling];
                if (message) {
                    // Remove seleção anterior
                    feelingButtons.forEach(b => b.classList.remove('selected'));
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

                    // Esconde welcome message e mostra chat
                    if (this.welcomeMessage) {
                        this.welcomeMessage.style.display = 'none';
                    }
                    if (this.chatMessages) {
                        this.chatMessages.classList.add('active');
                    }
                    const inputArea = document.querySelector('.input-area');
                    if (inputArea && inputArea.style) {
                        inputArea.style.display = 'flex';
                    }
                    if (this.messageInput) {
                        setTimeout(() => this.messageInput.focus(), 100);
                    }

                    // Envia a mensagem predefinida para a IA (mesma função do envio normal)
                    this.sendMessageText(message);
                }
            });
        });
    }

    /** Carrega histórico do servidor (fetch) e reseta UI; não confundir com loadChatHistory() que retorna array do localStorage */
    async loadChatHistoryFromServer() {
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
        
        const _nivelTexto = nivelRisco === 'alto' ? 'alto' : 'leve';
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
        const _height = window.innerHeight;
        const _isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
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
    showResources() {
        this.openEmergencyNumbersModal();
    }

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
            
            for (const [_key, trimestre] of Object.entries(gestacao)) {
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
            
            for (const [_key, periodo] of Object.entries(posparto)) {
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
                    timeout: 15000,
                    maximumAge: 0
                });
            });
            // Localização exata do usuário (sem cache) para Hospitais Maternos Próximos
            
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            // LOG: Início da busca
            console.log(`[MAPS DEBUG] Iniciando busca de hospitais próximos`);
            console.log(`[MAPS DEBUG] Coordenadas: lat=${lat}, lon=${lon}`);
            this.lastSearchLat = lat;
            this.lastSearchLon = lon;
            if (typeof window.sophiaAdminBadgeUpdatePos === 'function') {
                window.sophiaAdminBadgeUpdatePos(lat, lon);
            }

            // Busca hospitais próximos (com timeout aumentado implicitamente na função)
            const hospitals = await this.searchHospitalsNearby(lat, lon, 25);
            
            // LOG: Resultado da busca
            console.log(`[MAPS DEBUG] Busca concluída: ${hospitals ? hospitals.length : 0} unidades encontradas`);
            
            // Esconde loading
            if (this.hospitalsLoading) {
                this.hospitalsLoading.style.display = 'none';
            }
            
            // Exibe os hospitais encontrados (pode vir { list, nearbyConfirmed } ou array)
            const list = Array.isArray(hospitals) ? hospitals : (hospitals && hospitals.list) || [];
            const nearbyConfirmed = (hospitals && hospitals.nearbyConfirmed) || [];
            if (list.length > 0 || nearbyConfirmed.length > 0) {
                console.log(`[MAPS DEBUG] Exibindo ${list.length} unidades` + (nearbyConfirmed.length ? ` + ${nearbyConfirmed.length} confirmados próximos (até 100 km)` : '') + ' na interface');
                this.displayHospitals(list, nearbyConfirmed);
            } else {
                console.warn(`[MAPS DEBUG] Nenhuma unidade encontrada - exibindo estado vazio`);
                this.showEmptyState();
            }
        } catch (error) {
            // LOG: Erro na busca
            console.error(`[MAPS DEBUG] ❌ ERRO na busca de hospitais:`, error);
            console.error(`[MAPS DEBUG] Tipo:`, error.name);
            console.error(`[MAPS DEBUG] Mensagem:`, error.message);
            
            if (this.hospitalsLoading) {
                this.hospitalsLoading.style.display = 'none';
            }
            if (this.hospitalsError) {
                this.hospitalsError.style.display = 'block';
                let errorMessage = error.message || 'Erro desconhecido';
                if (error.name === 'AbortError' || error.message.includes('timeout')) {
                    errorMessage = 'A busca está demorando muito. Tente novamente em instantes.';
                } else if (error.message.includes('geolocalização') || error.message.includes('permissão')) {
                    errorMessage = 'É necessário permitir acesso à sua localização para buscar hospitais próximos.';
                } else if (error.message.includes('Servidor') || error.message.includes('503') || error.message.includes('rede') || error.message.includes('fetch')) {
                    errorMessage = 'Serviço temporariamente indisponível. Tente novamente em alguns minutos ou ligue 192 em caso de emergência.';
                }
                this.hospitalsError.innerHTML = '<p class="hospitals-error-msg">' + this.escapeHtml(errorMessage) + '</p>';
            }
            // Mostra estado vazio mesmo em caso de erro
            this.showEmptyState();
            this.error('Erro ao buscar hospitais:', error);
        }
    }
    
    async findHospitalsByRegion() {
        if (!this.hospitalsModal) return;
        const stateEl = document.getElementById('hospital-state');
        const cityEl = document.getElementById('hospital-city');
        const state = (stateEl && stateEl.value || '').trim();
        const city = (cityEl && cityEl.value || '').trim();
        if (!state) {
            this.warn('Selecione pelo menos o estado (UF).');
            if (stateEl) stateEl.focus();
            return;
        }
        this.closeEmergencyNumbersModal();
        this.hospitalsModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        if (this.hospitalsLoading) {
            this.hospitalsLoading.style.display = 'block';
            const sub = this.hospitalsLoading.querySelector('.loading-sub');
            if (sub) sub.textContent = `Buscando hospitais com maternidade em ${state}${city ? ' / ' + city : ''}...`;
        }
        if (this.hospitalsError) this.hospitalsError.style.display = 'none';
        if (this.hospitalsList) this.hospitalsList.innerHTML = '';
        try {
            const API_BASE_URL = window.location.hostname.includes('ngrok') ? window.location.origin : '';
            const body = {
                filter_type: 'MATERNITY',
                is_emergency: true,
                search_mode: 'all',
                radius_km: 25,
                state: state,
                city: city || undefined
            };
            const res = await fetch(`${API_BASE_URL}/api/v1/facilities/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!res.ok) throw new Error(`API: ${res.status} ${res.statusText}`);
            const data = await res.json();
            const hospitals = this.convertFacilitiesToHospitals(data.results || [], 0, 0);
            if (this.hospitalsLoading) this.hospitalsLoading.style.display = 'none';
            if (hospitals && hospitals.length > 0) {
                this.displayHospitals(hospitals);
            } else {
                this.showEmptyState();
            }
        } catch (e) {
            if (this.hospitalsLoading) this.hospitalsLoading.style.display = 'none';
            if (this.hospitalsError) {
                this.hospitalsError.style.display = 'block';
                this.hospitalsError.innerHTML = `<p>Erro: ${e.message || 'Erro ao buscar.'}</p>`;
            }
            this.showEmptyState();
            this.error('Erro ao buscar por região:', e);
        }
    }
    
    async searchHospitalsNearby(lat, lon, radiusKm = 25) {
        /**
         * ✅ Busca obstétrica via GET /api/v1/emergency/search (geo v2).
         * radiusKm: raio em km (default 25). Use 100 para "Ver tudo (100 km)".
         * min_results: 8 mobile, 12 desktop; limit=20; expand busca mais sem o usuário tocar no raio.
         * Health gate: se dataset.present=false, mostra "Atualizando dados" e evita tela vazia durante update.
         */
        const API_BASE_URL = window.location.hostname.includes('ngrok')
            ? window.location.origin
            : '';
        const radiusKmNum = Number(radiusKm) || 25;
        const limit = 20;
        const MIN_RESULTS = window.innerWidth < 768 ? 8 : 12;
        this.lastBanner192 = false;
        this.lastDebug = null;

        try {
            // Health gate: evitar tela vazia durante atualização do dataset
            const healthBase = API_BASE_URL || window.location.origin;
            try {
                const healthRes = await fetch(healthBase.replace(/\/$/, '') + '/api/v1/health', { headers: { 'Accept': 'application/json' } });
                if (healthRes.ok) {
                    const healthData = await healthRes.json();
                    if (healthData.dataset && healthData.dataset.present === false) {
                        throw new Error('Atualizando dados. Aguarde alguns instantes e tente novamente.');
                    }
                }
            } catch (e) {
                if (e.message && e.message.indexOf('Atualizando dados') !== -1) throw e;
                // Falha ao checar health (rede etc.): segue com a busca
            }

            const qs = new URLSearchParams({
                lat: String(lat),
                lon: String(lon),
                radius_km: String(radiusKmNum),
                expand: 'true',
                limit: String(limit),
                min_results: String(MIN_RESULTS),
                debug: 'true'
            }).toString();
            const path = `/api/v1/emergency/search?${qs}`;
            const bases = [
                API_BASE_URL || window.location.origin,
                'http://localhost:5000',
                'http://127.0.0.1:5000',
                'http://localhost:8000',
                'http://127.0.0.1:8000'
            ];
            if (typeof window !== 'undefined' && window.SOPHIA_API_BASE) {
                bases.unshift(window.SOPHIA_API_BASE);
            }
            const EMERGENCY_SEARCH_TIMEOUT_MS = 60000; // 60s para primeira carga do CNES (lazy)
            const maxAttempts = 2; // retry automático em timeout/falha de rede
            let data = null;
            let lastErr = null;
            for (let attempt = 1; attempt <= maxAttempts; attempt++) {
                for (const base of bases) {
                    const url = base.replace(/\/$/, '') + path;
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), EMERGENCY_SEARCH_TIMEOUT_MS);
                    try {
                        if (attempt > 1) console.log(`[MAPS DEBUG] [EMERGENCY] Retry ${attempt}/${maxAttempts} GET ${url}`);
                        else console.log(`[MAPS DEBUG] [EMERGENCY] GET ${url}`);
                        const response = await fetch(url, {
                            headers: { 'Accept': 'application/json' },
                            signal: controller.signal
                        });
                        clearTimeout(timeoutId);
                        console.warn('[MAPS DEBUG]', url, '->', response.status, response.statusText);
                        if (response.ok) {
                            data = await response.json();
                            break;
                        }
                        lastErr = new Error(`API retornou erro: ${response.status} ${response.statusText}`);
                    } catch (e) {
                        clearTimeout(timeoutId);
                        lastErr = e;
                        const isTimeout = e.name === 'AbortError' || (e.message && (e.message.toLowerCase().indexOf('timeout') !== -1 || e.message.toLowerCase().indexOf('aborted') !== -1));
                        console.warn(`[MAPS DEBUG] ${url} falhou:`, e.message || e, isTimeout ? '(será reattemptado)' : '');
                        if (isTimeout && attempt < maxAttempts) break; // sai do for bases para reattempt
                    }
                }
                if (data) break;
                if (attempt < maxAttempts && lastErr) {
                    const isRetryable = lastErr.name === 'AbortError' || (lastErr.message && (String(lastErr.message).toLowerCase().indexOf('timeout') !== -1 || String(lastErr.message).toLowerCase().indexOf('aborted') !== -1 || String(lastErr.message).toLowerCase().indexOf('failed') !== -1));
                    if (!isRetryable) break;
                    await new Promise(r => setTimeout(r, 800)); // breve pausa antes do retry
                }
            }
            if (!data) {
                const msg = (lastErr && (lastErr.message || '').toLowerCase().indexOf('connection refused') !== -1)
                    ? 'Servidor indisponível. Confira se o Flask está rodando em http://localhost:5000 (comando: python -m flask --app backend.app run -p 5000). Em emergência, ligue 192.'
                    : 'Não foi possível buscar hospitais. Tente novamente ou ligue 192 em caso de emergência.';
                throw lastErr ? new Error(msg) : new Error(msg);
            }
            console.log(`[MAPS DEBUG] ✅ API respondeu: ${(data.results || []).length} unidades encontradas`);
            if (typeof window.sophiaAdminBadgeUpdatePos === 'function') {
                window.sophiaAdminBadgeUpdatePos(lat, lon);
            }
            if (data.debug) {
                console.debug('[EMERGENCY DEBUG]', data.debug);
                this.lastDebug = data.debug;
            }

            this.lastBanner192 = !!data.banner_192;
            if (data.banner_192 && this.hospitalsList) {
                const banner = document.getElementById('hospitals-banner-192');
                if (banner) banner.style.display = 'block';
                else this.maybeInsertBanner192(data.banner_192);
            }

            // Log de diagnóstico: payload da API antes de processar
            if (data.results && data.results.length > 0) {
                console.log('[DIAGNÓSTICO] Payload da API (primeiros 3):');
                console.table((data.results || []).slice(0, 3).map(function(it) {
                    return {
                        nome: it.nome,
                        cnes_id: it.cnes_id,
                        esfera: it.esfera,
                        sus_badge: it.sus_badge,
                        telefone: it.telefone,
                        telefone_formatado: it.telefone_formatado,
                        endereco: it.endereco,
                        logradouro: it.logradouro,
                        numero: it.numero,
                        bairro: it.bairro,
                        cidade: it.cidade,
                        estado: it.estado,
                        convenios: Array.isArray(it.convenios) ? it.convenios.length : 0,
                        has_convenios: it.has_convenios,
                        override_hit: it.override_hit
                    };
                }));
            }

            // Mapear formato emergency/search -> formato esperado por convertFacilitiesToHospitals (sus_badge, esfera, convenios da API)
            const raw = (data.results || []).map(it => {
                const maternityBadge = (it.label_maternidade && it.label_maternidade !== 'Hospital') ? it.label_maternidade : null;
                const susBadge = (it.sus_badge && String(it.sus_badge).trim()) ? String(it.sus_badge).trim() : null;
                const esferaBadge = (it.esfera && String(it.esfera).trim()) ? it.esfera : null;
                const convenios = Array.isArray(it.convenios) ? it.convenios.filter(Boolean) : [];
                
                // Debug: log primeiro item para verificar campos disponíveis
                if (it === (data.results || [])[0]) {
                    console.log('[DEBUG] Primeiro item da API:', {
                        nome: it.nome,
                        endereco: it.endereco,
                        logradouro: it.logradouro,
                        numero: it.numero,
                        bairro: it.bairro,
                        cidade: it.cidade,
                        estado: it.estado,
                        telefone: it.telefone,
                        telefone_formatado: it.telefone_formatado,
                        convenios: it.convenios,
                        esfera: it.esfera,
                        sus_badge: it.sus_badge
                    });
                }
                
                // 0072: telefone — preferir telefone_formatado; fallback CO_DDD+NU_TELEFONE se API enviar
                var phoneVal = it.telefone_formatado || it.telefone || '';
                if (!phoneVal && it.co_ddd && it.nu_telefone) {
                    var d = String(it.co_ddd).replace(/\D/g, '').slice(0, 2);
                    var n = String(it.nu_telefone).replace(/\D/g, '');
                    phoneVal = n.length >= 8 ? '(' + d + ') ' + (n.length > 8 ? n.slice(0, 5) + '-' + n.slice(5) : n) : (d && n ? '(' + d + ') ' + n : '');
                }
                return {
                    name: it.nome,
                    address: it.endereco,
                    street: it.logradouro || null,
                    houseNumber: it.numero || null,
                    neighborhood: it.bairro || null,
                    city: it.cidade || null,
                    state: it.estado || null,
                    long: it.lon,
                    lat: it.lat,
                    distance_km: it.distancia_km,
                    tags: { sus: (it.sus_badge === 'Aceita Cartão SUS' || it.sus_badge === 'Aceita SUS') || it.atende_sus === 'Sim' },
                    phone: phoneVal,
                    type: 'hospital',
                    sus_badge: susBadge,
                    esfera: esferaBadge,
                    convenios: convenios,
                    has_convenios: !!it.has_convenios || convenios.length > 0,
                    badges: [maternityBadge, susBadge, esferaBadge].filter(Boolean)
                };
            });

            const hospitals = this.convertFacilitiesToHospitals(raw, lat, lon);
            // Log de diagnóstico: após convertFacilitiesToHospitals (primeiros 3)
            if (hospitals.length > 0) {
                console.log('[DIAGNÓSTICO] Após convertFacilitiesToHospitals (primeiros 3):');
                console.table(hospitals.slice(0, 3).map(function(it) {
                    return {
                        nome: it.name,
                        esfera: it.esfera,
                        sus: it.sus_badge
                    };
                }));
            }
            const hasConfirmedInResults = (data.results || []).some(it => it.has_maternity === true);
            let nearbyConfirmed = [];
            if (Array.isArray(data.nearby_confirmed) && data.nearby_confirmed.length > 0 && !hasConfirmedInResults) {
                const rawNearby = data.nearby_confirmed.map(it => {
                    const maternityBadge = (it.label_maternidade && it.label_maternidade !== 'Hospital') ? it.label_maternidade : ('Ala de Maternidade');
                    const susBadge = (it.sus_badge && String(it.sus_badge).trim()) ? String(it.sus_badge).trim() : null;
                    const esferaBadge = (it.esfera && String(it.esfera).trim()) ? it.esfera : null;
                    const convenios = Array.isArray(it.convenios) ? it.convenios.filter(Boolean) : [];
                    var phoneNearby = it.telefone_formatado || it.telefone || '';
                    if (!phoneNearby && it.co_ddd && it.nu_telefone) {
                        var dn = String(it.co_ddd).replace(/\D/g, '').slice(0, 2);
                        var nn = String(it.nu_telefone).replace(/\D/g, '');
                        phoneNearby = nn.length >= 8 ? '(' + dn + ') ' + (nn.length > 8 ? nn.slice(0, 5) + '-' + nn.slice(5) : nn) : (dn && nn ? '(' + dn + ') ' + nn : '');
                    }
                    return {
                        name: it.nome,
                        address: it.endereco || '',
                        street: it.logradouro || null,
                        houseNumber: it.numero || null,
                        neighborhood: it.bairro || null,
                        city: it.cidade || null,
                        state: it.estado || null,
                        long: it.lon,
                        lat: it.lat,
                        distance_km: it.distancia_km,
                        tags: { sus: (it.sus_badge === 'Aceita Cartão SUS' || it.sus_badge === 'Aceita SUS') || it.atende_sus === 'Sim' },
                        phone: phoneNearby,
                        type: 'hospital',
                        sus_badge: susBadge,
                        esfera: esferaBadge,
                        convenios: convenios,
                        has_convenios: !!it.has_convenios || convenios.length > 0,
                        badges: [maternityBadge, susBadge, esferaBadge].filter(Boolean)
                    };
                });
                nearbyConfirmed = this.convertFacilitiesToHospitals(rawNearby, lat, lon);
            }
            console.log(`[MAPS DEBUG] ✅ Conversão concluída: ${hospitals.length} hospitais formatados` + (nearbyConfirmed.length ? `; nearby_confirmed: ${nearbyConfirmed.length}` : ''));
            return nearbyConfirmed.length ? { list: hospitals, nearbyConfirmed } : hospitals;
        } catch (error) {
            console.error(`[MAPS DEBUG] ❌ ERRO ao buscar emergency/search:`, error);
            if (error && error.message && (error.message.indexOf('Servidor indisponível') !== -1 || error.message.indexOf('Confira se o Flask') !== -1)) {
                throw error;
            }
            throw new Error('Não foi possível buscar hospitais. Tente novamente ou ligue 192 em caso de emergência.');
        }
    }

    maybeInsertBanner192(show) {
        if (!this.hospitalsList || !show) return;
        let banner = document.getElementById('hospitals-banner-192');
        if (!banner) {
            banner = document.createElement('div');
            banner.id = 'hospitals-banner-192';
            banner.className = 'banner-192';
            banner.style.cssText = 'display:block;margin-bottom:12px;padding:10px 14px;background:#fef2f2;border-left:4px solid #dc2626;color:#991b1b;font-weight:600;border-radius:6px;';
            banner.textContent = 'Sintomas graves? Ligue 192 (SAMU) agora.';
            this.hospitalsList.insertBefore(banner, this.hospitalsList.firstChild);
        }
        banner.style.display = show ? 'block' : 'none';
    }

    /**
     * Converte formato da API FastAPI para formato esperado pelo displayHospitals
     * @param {Array} facilities - Resultados da API FastAPI
     * @param {number} userLat - Latitude do usuário
     * @param {number} userLon - Longitude do usuário
     * @returns {Array} - Array de hospitais no formato esperado
     */
    convertFacilitiesToHospitals(facilities, _userLat, _userLon) {
        return facilities.map(facility => {
            // Converter distância de km para metros
            const distanceMeters = (facility.distance_km || 0) * 1000;
            
            // Extrair informações do endereço
            // PRIORIDADE: Usar campos separados da API (logradouro, número, bairro, cidade, estado)
            let street = facility.street || '';
            let houseNumber = facility.houseNumber || '';
            let neighborhood = facility.neighborhood || '';
            let city = facility.city || '';
            let state = facility.state || '';
            
            // Se não temos campos separados, tentar extrair do endereço completo
            const fullAddress = facility.address || '';
            if (fullAddress && (!street || !city)) {
                // Tenta extrair componentes do endereço completo
                const addressParts = fullAddress.split(',').map(s => s.trim()).filter(Boolean);
                
                // Primeira parte geralmente é o logradouro (rua)
                if (!street && addressParts.length > 0) {
                    street = addressParts[0];
                }
                
                // Procura por cidade/estado no formato "Cidade/UF" ou "Cidade - UF"
                for (let i = addressParts.length - 1; i >= 0; i--) {
                    const part = addressParts[i];
                    if (part.includes('/')) {
                        const [cidade, uf] = part.split('/').map(s => s.trim());
                        if (!city && cidade) city = cidade;
                        if (!state && uf) state = uf;
                        break;
                    } else if (part.includes(' - ') && !city) {
                        const parts = part.split(' - ').map(s => s.trim());
                        if (parts.length >= 2) {
                            city = parts[parts.length - 2];
                            state = parts[parts.length - 1];
                            break;
                        }
                    }
                }
                
                // Se ainda não tem cidade/estado, tenta pegar das últimas partes
                if (!city && addressParts.length >= 2) {
                    const lastPart = addressParts[addressParts.length - 1];
                    const secondLastPart = addressParts[addressParts.length - 2];
                    // Se a última parte parece ser estado (2 letras), a penúltima é cidade
                    if (lastPart.length === 2 && !state) {
                        state = lastPart;
                        city = secondLastPart;
                    }
                }
            }
            
            // Fallback: só usar endereço completo como "street" se for curto (evita duplicação "Rua – RUA, 123 – ...")
            if (!street && fullAddress) {
                if (fullAddress.includes(',') || fullAddress.includes(' – ')) {
                    const first = fullAddress.split(/[,–]/)[0].trim();
                    street = first || fullAddress;
                } else {
                    street = fullAddress;
                }
            }
            
            // Determinar se é público baseado em tags (dados exatos do CSV)
            const isPublic = facility.tags?.sus === true;
            
            // Determinar tipo de unidade
            let healthcareType = 'hospital';
            if (facility.type === 'UPA') {
                healthcareType = 'emergency';
            } else if (facility.type === 'UBS') {
                healthcareType = 'centre';
            }
            
            // FASE 2: Usar display_name e display_subtitle se disponíveis (melhor UX)
            const displayName = facility.display_name || facility.fantasy_name || facility.name || 'Hospital';
            const displaySubtitle = facility.display_subtitle || '';
            
            return {
                name: displayName,
                subtitle: displaySubtitle, // FASE 2: Subtítulo (ex: nome do profissional)
                lat: facility.lat,
                lon: facility.long,
                address: fullAddress,
                street: street,
                houseNumber: houseNumber, // Número do endereço (se disponível)
                neighborhood: neighborhood,
                city: city,
                state: state,
                phone: facility.phone || '', // FASE 1: Telefone do CSV (NU_TELEFONE)
                website: '',
                distance: distanceMeters,
                distance_km: facility.distance_km || (distanceMeters / 1000), // FASE 2: Distância em km
                isEmergency: facility.tags?.emergency_only === true,
                acceptsSUS: facility.tags?.sus === true,
                isPublic: isPublic,
                healthcareType: healthcareType,
                // Campos adicionais da nossa API (preservados para displayHospitals)
                tags: facility.tags,
                badges: facility.badges || [],
                esfera: facility.esfera || null,
                sus_badge: facility.sus_badge || null,
                convenios: facility.convenios || [],
                has_convenios: !!facility.has_convenios,
                warning_message: facility.warning_message,
                type: facility.type,
                // FASE 1: Dados adicionais para validação jurídica
                management: facility.management, // Gestão (Municipal/Estadual/Federal/Privado)
                natureza_juridica: facility.natureza_juridica, // Para transparência
                // FASE 3: Validação de dados
                data_validation: facility.data_validation || null
            };
        });
    }
    
    async searchHospitalsNearby_OLD_OVERPASS(lat, lon, radius = 50000) {
        /** 
         * ⚠️ MÉTODO ANTIGO - MANTIDO APENAS PARA REFERÊNCIA
         * NÃO DEVE SER USADO EM PRODUÇÃO - Violação de segurança (.cursorrules)
         * Busca usando Overpass API direto (SEM validação CNES)
         */
        
        // ========================================
        // QUERY AMPLIADA: Busca TODAS as unidades de saúde próximas
        // ========================================
        const query = `[out:json][timeout:30];
(
  node["amenity"="hospital"](around:${radius},${lat},${lon});
  way["amenity"="hospital"](around:${radius},${lat},${lon});
  relation["amenity"="hospital"](around:${radius},${lat},${lon});
  node["amenity"="clinic"](around:${radius},${lat},${lon});
  way["amenity"="clinic"](around:${radius},${lat},${lon});
  relation["amenity"="clinic"](around:${radius},${lat},${lon});
  node["healthcare"="hospital"](around:${radius},${lat},${lon});
  way["healthcare"="hospital"](around:${radius},${lat},${lon});
  relation["healthcare"="hospital"](around:${radius},${lat},${lon});
  node["healthcare"="clinic"](around:${radius},${lat},${lon});
  way["healthcare"="clinic"](around:${radius},${lat},${lon});
  relation["healthcare"="clinic"](around:${radius},${lat},${lon});
  node["healthcare"="centre"](around:${radius},${lat},${lon});
  way["healthcare"="centre"](around:${radius},${lat},${lon});
  relation["healthcare"="centre"](around:${radius},${lat},${lon});
);
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
                // Timeout aumentado para 45 segundos (era 30) para dar mais tempo à API
                const timeoutId = setTimeout(() => controller.abort(), 45000);
                
                // LOG: Início da requisição
                console.log(`[MAPS DEBUG] Tentativa ${serverIndex + 1}/${servers.length} - Servidor: ${server}`);
                console.log(`[MAPS DEBUG] Query Overpass:`, query.substring(0, 200) + '...');
                
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
                    
                    // LOG: Status da resposta
                    console.log(`[MAPS DEBUG] Resposta recebida - Status: ${response.status} ${response.statusText}`);
                } catch (fetchError) {
                    clearTimeout(timeoutId);
                    lastError = fetchError;
                    console.error(`[MAPS DEBUG] Erro na requisição fetch:`, fetchError);
                    if (serverIndex < servers.length - 1) {
                        console.log(`[MAPS DEBUG] Tentando próximo servidor...`);
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
                
                // LOG: Conteúdo da resposta (primeiros 500 caracteres)
                console.log(`[MAPS DEBUG] Resposta da API (primeiros 500 chars):`, responseText.substring(0, 500));
                
                let data;
                try {
                    data = JSON.parse(responseText);
                    
                    // LOG: Estrutura do JSON retornado
                    console.log(`[MAPS DEBUG] JSON parseado com sucesso`);
                    console.log(`[MAPS DEBUG] Número de elementos:`, data.elements ? data.elements.length : 0);
                    if (data.elements && data.elements.length > 0) {
                        console.log(`[MAPS DEBUG] Primeiro elemento (amostra):`, JSON.stringify(data.elements[0]).substring(0, 300));
                    }
                    
                    // Verifica se há erros na resposta da API Overpass
                    if (data.error) {
                        console.error(`[MAPS DEBUG] ERRO DA API OVERPASS:`, data.error);
                        console.error(`[MAPS DEBUG] Status: ${data.error.status || 'N/A'}`);
                        console.error(`[MAPS DEBUG] Mensagem: ${data.error.message || 'N/A'}`);
                        lastError = new Error(`Erro da API de mapas: ${data.error.message || 'Erro desconhecido'}`);
                        if (serverIndex < servers.length - 1) {
                            continue; // Tenta próximo servidor
                        }
                        throw lastError;
                    }
                    
                } catch (parseError) {
                    console.error(`[MAPS DEBUG] ERRO ao fazer parse do JSON:`, parseError);
                    console.error(`[MAPS DEBUG] Resposta completa (últimos 1000 chars):`, responseText.substring(Math.max(0, responseText.length - 1000)));
                    if (serverIndex < servers.length - 1) {
                        continue;
                    }
                    return [];
                }
                
                const hospitals = [];
                
                // LOG: Início do processamento
                console.log(`[MAPS DEBUG] Processando ${data.elements ? data.elements.length : 0} elementos da API`);
                
                if (data.elements && data.elements.length > 0) {
                    let processedCount = 0;
                    let skippedCount = 0;
                    
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
                        
                        const _specialty = (element.tags?.['healthcare:speciality'] || '').toLowerCase();
                        const healthcare = (element.tags?.['healthcare'] || '').toLowerCase();
                        const amenity = (element.tags?.['amenity'] || '').toLowerCase();
                        const nameLower = (hospitalName || '').toLowerCase();
                        const emergency = (element.tags?.['emergency'] || '').toLowerCase();
                        const payment = (element.tags?.['healthcare:payment'] || '').toLowerCase();
                        const operatorType = (element.tags?.['operator:type'] || '').toLowerCase();
                        
                        // ========================================
                        // FILTROS REMOVIDOS: Aceita TODAS as unidades de saúde
                        // ========================================
                        // REMOVIDO: Validação restritiva de tipo de hospital
                        // REMOVIDO: Validação de infraestrutura de maternidade
                        // Agora aceita todas as unidades de saúde retornadas pela API
                        // ========================================
                        
                        const isEmergency = emergency === 'yes' || emergency === 'emergency_ward' || 
                                           nameLower.includes('pronto socorro') || nameLower.includes('pronto atendimento') ||
                                           nameLower.includes('emergency') || nameLower.includes('urgência');
                        
                        // Verifica se aceita SUS (hospital público)
                        const acceptsSUS = payment === 'public' || payment === 'yes' || 
                                          operatorType === 'public';
                        
                        // REMOVIDO: Validação de maternidade - agora aceita todas as unidades
                        // Define nome padrão se não houver
                        if (!hospitalName || hospitalName.trim() === '') {
                            hospitalName = 'Unidade de Saúde';
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
                            // REMOVIDO: Campos relacionados a maternidade (não mais utilizados)
                            isEmergency: isEmergency,
                            acceptsSUS: acceptsSUS,
                            isPublic: isPublic,
                            // Tipo de unidade de saúde (hospital, clinic, centre, etc)
                            healthcareType: healthcare || amenity || 'health'
                        };
                        
                        if (hospital.lat && hospital.lon) {
                            hospitals.push(hospital);
                            processedCount++;
                        } else {
                            skippedCount++;
                            console.warn(`[MAPS DEBUG] Elemento sem coordenadas ignorado:`, element.tags?.name || 'Sem nome');
                        }
                    }
                    
                    // LOG: Resultado do processamento
                    console.log(`[MAPS DEBUG] Processamento concluído: ${processedCount} unidades adicionadas, ${skippedCount} ignoradas`);
                } else {
                    console.warn(`[MAPS DEBUG] AVISO: API retornou 0 elementos (ZERO_RESULTS ou resposta vazia)`);
                    console.warn(`[MAPS DEBUG] Estrutura da resposta:`, Object.keys(data));
                }
                
                // Remove duplicatas
                let filteredHospitals = this.deduplicateHospitals(hospitals);
                console.log(`[MAPS DEBUG] Após remoção de duplicatas: ${filteredHospitals.length} unidades`);
                
                // Filtra unidades que têm informações básicas: nome e coordenadas (critério mínimo)
                // REMOVIDO: Exigência de telefone e endereço completo (muito restritivo)
                const beforeFilter = filteredHospitals.length;
                filteredHospitals = filteredHospitals.filter(h => {
                    const hasName = h.name && h.name.trim() !== '' && h.name !== 'Unidade de Saúde';
                    const hasCoordinates = h.lat && h.lon;
                    return hasName && hasCoordinates;
                });
                console.log(`[MAPS DEBUG] Após filtro de informações básicas: ${filteredHospitals.length} unidades (${beforeFilter - filteredHospitals.length} removidas)`);
                
                // REMOVIDO: Scoring e priorização por maternidade
                // Agora ordena APENAS por distância (mais próximo primeiro)
                filteredHospitals.sort((a, b) => {
                    return a.distance - b.distance;
                });
                
                // LOG: Resultado final
                console.log(`[MAPS DEBUG] ✅ Busca concluída com sucesso: ${filteredHospitals.length} unidades de saúde encontradas`);
                if (filteredHospitals.length > 0) {
                    console.log(`[MAPS DEBUG] Primeira unidade:`, filteredHospitals[0].name, `- Distância: ${(filteredHospitals[0].distance / 1000).toFixed(1)} km`);
                }
                
                return filteredHospitals;
            
            } catch (error) {
                // LOG: Erro capturado
                console.error(`[MAPS DEBUG] ERRO na tentativa ${serverIndex + 1}:`, error);
                console.error(`[MAPS DEBUG] Tipo do erro:`, error.name);
                console.error(`[MAPS DEBUG] Mensagem:`, error.message);
                if (error.stack) {
                    console.error(`[MAPS DEBUG] Stack trace:`, error.stack.substring(0, 500));
                }
                
                // Captura erros da requisição ou processamento
                lastError = error;
                if (serverIndex < servers.length - 1) {
                    console.log(`[MAPS DEBUG] Tentando próximo servidor...`);
                    continue; // Tenta próximo servidor
                }
                // Se esgotou todos os servidores, propaga o erro
                console.error(`[MAPS DEBUG] ❌ Todos os servidores falharam. Último erro:`, lastError);
                throw error;
            }
        }
        
        // Se chegou aqui sem retornar, nenhum servidor funcionou
        if (lastError) {
            console.error(`[MAPS DEBUG] ❌ FALHA FINAL: Nenhum servidor funcionou. Último erro:`, lastError);
            throw lastError; // Lança o último erro capturado (já com mensagem amigável)
        }
        
        console.warn(`[MAPS DEBUG] ⚠️ AVISO: Nenhum servidor retornou dados e nenhum erro foi capturado`);
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
                            // REMOVIDO: Priorização por maternidade
                            // Prioriza apenas: Com SUS > Outros (mantém o que aceita SUS)
                            const hospitalPriority = hospital.acceptsSUS ? 1 : 0;
                            const existingPriority = existing.acceptsSUS ? 1 : 0;
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
            'sus_no': 'hospital-badge-sus-no',
            'maternity': 'hospital-badge-maternity',
            'emergency': 'hospital-badge-emergency',
            'private': 'hospital-badge-private',
            'public': 'hospital-badge-public',
            'philanthropic': 'hospital-badge-philanthropic'
        };
        
        // data-badge por tipo: evita match por texto no dedupe; DOM estável ante variações de copy
        const safeType = (type && typeof type === 'string') ? type.replace(/"/g, '&quot;') : '';
        const dataBadge = safeType ? ` data-badge="${safeType}"` : '';
        return `<span class="${classes[type] || 'hospital-badge-info'}"${dataBadge}>${iconHtml}${this.escapeHtml(text)}</span>`;
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

    /** Hotfix: esfera/SUS do payload com override por nome (municip|mun.|h mun|…). Nunca sobrescrever Público com Privado. */
    deriveEsferaFromName(nome) {
        const n = (nome || '').toString().toLowerCase();
        if (/(municip|mun\.|h\s+mun|estad|federal|prefeit|sec\.\s*sa[úu]de|secretaria)/.test(n)) return 'Público';
        if (/(santa casa|filantr|beneficen|miseric[oó]rdia|irmandade|fund(a|ação|acao))/.test(n)) return 'Filantrópico';
        return null;
    }
    mapEsfera(esferaPayload, nome) {
        const e = (esferaPayload || '').toString().trim();
        // Payload canônico da API: nunca trocar (Público/Privado/Filantrópico)
        if (e === 'Público' || e === 'Privado' || e === 'Filantrópico') return e;
        // Se payload vazio/null, tenta override por nome (só para casos legados sem API)
        const override = this.deriveEsferaFromName(nome);
        if (override) return override;
        // NUNCA retornar "Privado" como fallback - se não souber, retorna vazio/null
        return null;
    }
    mapSusBadge(susBadgePayload, atendeLabel, esferaFinal) {
        const s = (susBadgePayload || '').toString().trim();
        if (s === 'Aceita Cartão SUS' || s === 'Aceita SUS') return 'Aceita Cartão SUS';
        if ((s === '' || s === 'Desconhecido') && esferaFinal === 'Público') return 'Aceita Cartão SUS';
        if (s === 'Não atende SUS' || (atendeLabel || '').toString().trim() === 'Não') return 'Não atende SUS';
        return '';
    }

    /**
     * Helper único: identifica se um texto é badge SUS (aceita/não atende).
     * Delega para window.Badges.isSusBadge quando badges.js está carregado (normalização + canonical + \bsus\b).
     * Fallback mínimo se badges.js não estiver disponível.
     */
    isSusBadge(text) {
        if (!text || typeof text !== 'string') return false;
        try {
            if (typeof window !== 'undefined' && window.Badges && typeof window.Badges.isSusBadge === 'function') {
                return window.Badges.isSusBadge(text);
            }
        } catch (e) {}
        const n = text.replace(/\s+/g, ' ').trim().toLowerCase();
        if (!/\bsus\b/.test(n)) return false;
        if (/aceita\s*(cart[aã]o\s*)?sus|cart[aã]o\s*sus/i.test(n)) return true;
        if (/n[aã]o\s*atende\s*sus|n[aã]o\s*atende\s*ao\s*sus/i.test(n)) return true;
        return false;
    }
    
    displayHospitals(hospitals, nearbyConfirmed) {
        if (!this.hospitalsList) return;

        const mainList = Array.isArray(hospitals) ? hospitals : [];
        const nearbyList = Array.isArray(nearbyConfirmed) ? nearbyConfirmed : [];
        if (mainList.length === 0 && nearbyList.length === 0) {
            this.showEmptyState();
            return;
        }

        // CRÍTICO: Flag para identificar busca de maternidades (não exibir bloco amarelo)
        const _isMaternitySearch = true;

        // Filtro: nome + coordenadas
        const completeHospitals = mainList.filter(h => {
            const hasName = h.name && h.name.trim() !== '' && h.name !== 'Unidade de Saúde';
            const hasCoordinates = h.lat && h.lon;
            return hasName && hasCoordinates;
        });
        const sortedHospitals = [...completeHospitals].sort((a, b) => (a.distance || 0) - (b.distance || 0));

        const completeNearby = nearbyList.filter(h => {
            const hasName = h.name && h.name.trim() !== '' && h.name !== 'Unidade de Saúde';
            const hasCoordinates = h.lat && h.lon;
            return hasName && hasCoordinates;
        });
        const sortedNearby = [...completeNearby].sort((a, b) => (a.distance_km || 0) - (b.distance_km || 0));

        if (sortedHospitals.length === 0 && sortedNearby.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Renderização otimizada: cria fragmento para melhor performance
        const fragment = document.createDocumentFragment();
        const container = document.createElement('div');
        
        // Banner 192 quando API retorna banner_192 (fallback camada C)
        const banner192Html = this.lastBanner192
            ? '<div class="banner-192" style="margin-bottom: 12px; padding: 10px 14px; background: #fef2f2; border-left: 4px solid #dc2626; color: #991b1b; font-weight: 600; border-radius: 6px;"><i class="fas fa-phone-alt" style="margin-right: 6px;"></i>Sintomas graves? Ligue 192 (SAMU) agora.</div>'
            : '';

        // Chip "raio expandido" quando debug.expanded e radius_used (transparência)
        const radiusUsed = this.lastDebug && this.lastDebug.radius_used != null ? Number(this.lastDebug.radius_used) : null;
        const expandedChipHtml = (this.lastDebug && this.lastDebug.expanded && radiusUsed != null)
            ? '<div class="hospitals-radius-chip" style="margin-bottom: 10px; padding: 8px 12px; background: #f0f9ff; border-left: 4px solid #0284c7; color: #0369a1; font-size: 0.85rem; border-radius: 6px;"><i class="fas fa-map-marker-alt" style="margin-right: 6px;"></i>Resultados em raio expandido para ' + Math.round(radiusUsed) + ' km</div>'
            : '';

        // FASE 2: Mensagem específica para maternidades
        const messageText = sortedHospitals.length === 1
            ? 'Encontrado 1 hospital materno próximo:'
            : (sortedHospitals.length === 0 ? 'Nenhum confirmado no raio solicitado.' : `Encontrados ${sortedHospitals.length} hospitais maternos próximos:`);

        let topHtml = banner192Html + expandedChipHtml;
        if (sortedNearby.length > 0) {
            topHtml += '<p style="margin-bottom: 6px; margin-top: 4px; font-weight: 600; color: #0369a1; font-size: 0.95rem;"><i class="fas fa-map-marker-alt" style="margin-right: 6px;"></i>Confirmados mais próximos (até 100 km)</p>';
            topHtml += '<p style="margin-bottom: 10px;"><button type="button" class="btn-sophia btn-sophia-compact hospitals-ver-tudo-100" style="font-size: 0.85rem; padding: 6px 12px; background: #0369a1; color: white; border: none; border-radius: 6px; cursor: pointer;"><i class="fas fa-expand-alt" style="margin-right: 4px;"></i>Ver tudo (100 km)</button></p>';
        }
        if (sortedHospitals.length > 0) {
            topHtml += `
            <p style="margin-bottom: var(--sophia-spacing-md); color: var(--sophia-text-secondary);">
                ${messageText}
            </p>
            <p style="margin-bottom: var(--sophia-spacing-md); font-size: 0.85rem; color: #059669; background: #d1fae5; padding: 0.75rem; border-radius: 6px; border-left: 4px solid #059669;">
                <i class="fas fa-baby" style="margin-right: 0.5rem;"></i>
                <strong>Foco em Maternidades:</strong> Estes hospitais possuem infraestrutura para atendimento obstétrico e realização de partos.
            </p>
            `;
        } else if (sortedNearby.length > 0) {
            topHtml += '<p style="margin-bottom: 10px; color: var(--sophia-text-secondary); font-size: 0.9rem;">Abaixo, unidades com <strong>Ala de Maternidade</strong> confirmada (até 100 km).</p>';
        }
        container.innerHTML = topHtml;

        const fragmentNearby = document.createDocumentFragment();
        sortedNearby.forEach((hospital) => {
            const name = (hospital.name || 'Hospital').trim();
            
            // Formata endereço completo para nearby também
            const sanitizedPhone = hospital.phone ? this.sanitizePhone(hospital.phone) : '';
            const sanitizedAddress = hospital.address ? this.sanitizeString(hospital.address) : '';
            const sanitizedStreet = hospital.street ? this.sanitizeString(hospital.street) : '';
            const sanitizedHouseNumber = hospital.houseNumber ? this.sanitizeString(hospital.houseNumber) : '';
            
            // Monta endereço formatado (mesma lógica dos hospitais principais)
            const addressParts = [];
            if (sanitizedStreet) addressParts.push(sanitizedStreet);
            if (sanitizedHouseNumber && sanitizedStreet) {
                addressParts[addressParts.length - 1] += `, ${sanitizedHouseNumber}`;
            }
            if (hospital.neighborhood) addressParts.push(this.escapeHtml(hospital.neighborhood));
            if (hospital.city) addressParts.push(this.escapeHtml(hospital.city));
            if (hospital.state) addressParts.push(this.escapeHtml(hospital.state));
            
            const formattedAddress = addressParts.length > 0 
                ? addressParts.join(' - ') 
                : (sanitizedAddress || 'Endereço não disponível');
            
            // Esfera e SUS badge para nearby
            const nome = hospital.display_name || hospital.name;
            let displayEsfera = this.mapEsfera(hospital.esfera, nome);
            if (displayEsfera == null && (hospital.atende_sus === 'Sim' || hospital.accepts_sus === true)) {
                displayEsfera = 'Público';
            }
            const esferaValida = ['Público', 'Privado', 'Filantrópico'];
            const esferaOk = displayEsfera && esferaValida.includes(displayEsfera);
            const susFinal = this.mapSusBadge(hospital.sus_badge, hospital.atende_sus, esferaOk ? displayEsfera : null);
            
            // Tags Público/Privado e SUS ocultas por decisão de produto (retorno em versão futura)
            const publicPrivateTag = '';

            // Convênios/SUS/Público/Privado: removidos por decisão de produto (não exibir nos cards)
            const conveniosLineNearby = '';
            
            const dest = (hospital.lat != null && hospital.lon != null) ? `${hospital.lat},${hospital.lon}` : encodeURIComponent(formattedAddress || name);
            const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${dest}`;
            const excludeBadgesNearby = new Set(['Público', 'Privado', 'Filantrópico', 'Aceita Cartão SUS', 'Aceita SUS']);
            const badgesFilteredNearby = (hospital.badges && Array.isArray(hospital.badges))
                ? hospital.badges.filter(b => {
                    const t = String(b).trim();
                    return t && !excludeBadgesNearby.has(t) && !this.isSusBadge(t);
                })
                : [];
            const badgesHtml = badgesFilteredNearby.length > 0
                ? badgesFilteredNearby.slice(0, 3).map(b => `<span class="hospital-badge" style="display:inline-block;background:#dbeafe;color:#1e40af;padding:0.2rem 0.5rem;border-radius:4px;font-size:0.75rem;margin-right:4px;">${this.escapeHtml(String(b))}</span>`).join('') : '';
            
            const card = document.createElement('div');
            card.className = 'hospital-card';
            // Não adiciona data-index para evitar renderização incorreta
            card.innerHTML = `
                <div class="hospital-header">
                    <h4 class="hospital-name">${this.escapeHtml(name)}</h4>
                    ${publicPrivateTag ? `<div class="hospital-header-tags" style="margin-top: 6px;">${publicPrivateTag}</div>` : ''}
                </div>
                ${badgesHtml ? `<div class="hospital-badges" style="margin:6px 0;">${badgesHtml}</div>` : ''}
                ${conveniosLineNearby}
                ${formattedAddress && formattedAddress !== 'Endereço não disponível' ? `<p class="hospital-address" style="font-size:0.85rem;color:#6b7280;margin-top:8px;"><i class="fas fa-map-marker-alt" aria-hidden="true"></i> ${this.escapeHtml(formattedAddress)}</p>` : ''}
                ${sanitizedPhone ? `<p class="hospital-phone" style="font-size:0.85rem;color:#6b7280;margin-top:4px;"><i class="fas fa-phone" aria-hidden="true"></i> <a href="tel:${sanitizedPhone}" class="hospital-phone-link">${this.escapeHtml(hospital.phone || sanitizedPhone)}</a></p>` : ''}
                <div class="hospital-actions" style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">
                    ${sanitizedPhone ? `<a href="tel:${sanitizedPhone}" class="btn-sophia btn-sophia-compact" style="background: var(--sophia-emergency); color: white; font-weight: 700; flex: 1; min-width: 120px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;"><i class="fas fa-phone" aria-hidden="true"></i> Ligar</a>` : ''}
                    <a href="${mapsUrl}" target="_blank" rel="noopener" class="btn-sophia btn-sophia-compact" style="flex: 1; min-width: 120px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;"><i class="fas fa-route" aria-hidden="true"></i> Rota</a>
                    <a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(name + ' ' + formattedAddress)}" target="_blank" rel="noopener" class="btn-sophia btn-sophia-compact" style="flex: 1; min-width: 120px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;"><i class="fas fa-map-marked-alt" aria-hidden="true" style="font-size: 1em; width: 1em; display: inline-block;"></i> Ver no Mapa</a>
                </div>
            `;
            fragmentNearby.appendChild(card);
        });
        if (fragmentNearby.childNodes.length) {
            container.appendChild(fragmentNearby);
        }

        sortedHospitals.forEach((hospital, index) => {
            const badges = [];
            
            // Badges da nossa API (se disponíveis) — sem duplicatas; SUS só no header
            // Normalização na origem: filtra SUS, Público/Privado/Filantrópico e inválidos (não exibir nos cards)
            const excludeFromBadges = new Set(['Público', 'Privado', 'Filantrópico', 'Aceita Cartão SUS', 'Aceita SUS']);
            const badgeList = (hospital.badges && Array.isArray(hospital.badges))
                ? hospital.badges.filter(b => {
                    const t = String(b).trim();
                    if (!t || String(t).toUpperCase() === 'DESCONHECIDO') return false;
                    if (t === 'Hospital') return false;
                    if (excludeFromBadges.has(t) || this.isSusBadge(t)) return false;
                    return true;
                })
                : [];
            let hasEmergencyBadge = false;
            badgeList.forEach(badgeText => {
                const badgeUpper = String(badgeText).toUpperCase();
                // Badge de Emergência (apenas um)
                if ((badgeUpper.includes('EMERGÊNCIA') || badgeUpper.includes('EMERGENCIA')) && !hasEmergencyBadge) {
                    badges.push(this.createBadge('emergency', 'EMERGÊNCIA', 'fas fa-ambulance'));
                    hasEmergencyBadge = true;
                }
                // Badge de Maternidade (Ala de Maternidade ou Provável maternidade)
                else if (badgeUpper.includes('MATERNIDADE')) {
                    badges.push(this.createBadge('maternity', badgeText, 'fas fa-baby'));
                }
                // Outros badges – não exibir "NÃO REALIZA PARTO"
                else if (!badgeUpper.includes('NÃO REALIZA PARTO') && !badgeUpper.includes('NAO REALIZA PARTO')) {
                    badges.push(this.createBadge('info', badgeText, 'fas fa-info-circle'));
                }
            });
            
            // Sanitiza dados
            const hospitalName = hospital.name || 'Hospital';
            const sanitizedPhone = hospital.phone ? this.sanitizePhone(hospital.phone) : '';
            const sanitizedAddress = hospital.address ? this.sanitizeString(hospital.address) : '';
            const sanitizedStreet = hospital.street ? this.sanitizeString(hospital.street) : '';
            const sanitizedHouseNumber = hospital.houseNumber ? this.sanitizeString(hospital.houseNumber) : '';
            
            // Ownership: cálculo explícito, NUNCA default "Privado" quando dado ausente (mapEsfera retorna null)
            const nome = hospital.display_name || hospital.name;
            let displayEsfera = this.mapEsfera(hospital.esfera, nome);
            if (displayEsfera == null && (hospital.atende_sus === 'Sim' || hospital.accepts_sus === true)) {
                displayEsfera = 'Público';
            }
            // Guard: só considera valores canônicos; evita fallback "Privado" indevido
            try {
                const __allowedEsfera = new Set(['Público', 'Privado', 'Filantrópico']);
                if (!displayEsfera || !__allowedEsfera.has(displayEsfera)) {
                    displayEsfera = null;
                }
            } catch (_) { /* no-op */ }
            const esferaValida = ['Público', 'Privado', 'Filantrópico'];
            const esferaOk = displayEsfera && esferaValida.includes(displayEsfera);
            
            // sus_badge vem da API; mapSusBadge só ajusta formato se necessário
            const susFinal = this.mapSusBadge(hospital.sus_badge, hospital.atende_sus, esferaOk ? displayEsfera : null);
            
            // Debug: origem e ownership (uma sessão)
            if (index < 3 && this.isDevelopment) {
                console.debug('[CARD]', hospital.cnes_id || hospital.id || index, 'ownership=', displayEsfera || '—', 'raw=', { public_private: hospital.public_private, esfera: hospital.esfera, accepts_sus: hospital.accepts_sus });
            }
            
            const cardId = hospital.cnes_id || hospital.id || 'idx-' + index;
            const cardSource = hospital._source || 'api';
            
            // Classes CSS baseadas no valor calculado (nunca fallback para Privado)
            const sphereClassMap = {
                'Público': 'hospital-tag-public',
                'Filantrópico': 'hospital-tag-philanthropic',
                'Privado': 'hospital-tag-private'
            };
            
            // Tags Público/Privado e SUS ocultas por decisão de produto (retorno em versão futura)
            let publicPrivateTag = '';

            // Aviso de segurança - usa warning_message da API se disponível (UX Expert)
            // CRÍTICO: NÃO exibir bloco amarelo em busca de maternidades (apenas hospitais aparecem, não precisa avisar)
            let safetyWarning = '';
            // Esta função (displayHospitals) é chamada APENAS para busca de maternidades
            // Portanto, NÃO exibir bloco amarelo (safetyWarning fica vazio)
            // Se no futuro houver outras buscas, adicionar flag para identificar tipo de busca
            
            // Monta endereço formatado (rua e número separados) - PRIORIDADE: endereço completo
            // Formato: Rua, Número - Bairro, Cidade - Estado
            let formattedAddress = '';
            const addressParts = [];
            
            // 1. Logradouro (rua)
            if (sanitizedStreet) {
                addressParts.push(sanitizedStreet);
            }
            
            // 2. Número (se disponível)
            if (sanitizedHouseNumber) {
                if (addressParts.length > 0) {
                    addressParts[addressParts.length - 1] += `, ${sanitizedHouseNumber}`;
                } else {
                    addressParts.push(sanitizedHouseNumber);
                }
            }
            
            // 3. Bairro
            if (hospital.neighborhood) {
                addressParts.push(this.escapeHtml(hospital.neighborhood));
            }
            
            // 4. Cidade
            if (hospital.city) {
                addressParts.push(this.escapeHtml(hospital.city));
            }
            
            // 5. Estado
            if (hospital.state) {
                addressParts.push(this.escapeHtml(hospital.state));
            }
            
            // Se não conseguiu montar com campos separados, usar address completo
            if (addressParts.length === 0 && sanitizedAddress) {
                formattedAddress = sanitizedAddress;
                // Adiciona cidade/estado se não estiverem no endereço
                if (hospital.city && !formattedAddress.toLowerCase().includes(hospital.city.toLowerCase())) {
                    formattedAddress += `, ${this.escapeHtml(hospital.city)}`;
                }
                if (hospital.state && !formattedAddress.toLowerCase().includes(hospital.state.toLowerCase())) {
                    formattedAddress += ` - ${this.escapeHtml(hospital.state)}`;
                }
            } else if (addressParts.length > 0) {
                // Formata: "Rua, Número - Bairro, Cidade - Estado"
                formattedAddress = addressParts.join(' - ');
            } else {
                // Fallback: usar apenas cidade/estado se disponíveis
                const fallbackParts = [];
                if (hospital.city) fallbackParts.push(this.escapeHtml(hospital.city));
                if (hospital.state) fallbackParts.push(this.escapeHtml(hospital.state));
                formattedAddress = fallbackParts.join(' - ') || 'Endereço não disponível';
            }
            
            // Monta endereço completo para Google Maps (rua exata, não lat/long)
            // CRÍTICO: Garantir que sempre tenha nome do hospital + endereço completo (rua, número, cidade, estado)
            let mapQueryParts = [hospitalName];
            
            // Prioridade 1: Endereço completo formatado (rua, número, bairro, cidade, estado)
            if (formattedAddress && formattedAddress !== 'Endereço não disponível') {
                mapQueryParts.push(formattedAddress);
            } 
            // Prioridade 2: Address completo da API + cidade/estado
            else if (sanitizedAddress) {
                mapQueryParts.push(sanitizedAddress);
                if (hospital.city && !sanitizedAddress.includes(hospital.city)) {
                    mapQueryParts.push(hospital.city);
                }
                if (hospital.state && !sanitizedAddress.includes(hospital.state)) {
                    mapQueryParts.push(hospital.state);
                }
            }
            // Prioridade 3: Street + número + cidade/estado
            else if (sanitizedStreet) {
                mapQueryParts.push(sanitizedStreet);
                if (sanitizedHouseNumber) {
                    mapQueryParts.push(sanitizedHouseNumber);
                }
                if (hospital.city) mapQueryParts.push(hospital.city);
                if (hospital.state) mapQueryParts.push(hospital.state);
            }
            // Fallback: Cidade/estado apenas
            else {
                if (hospital.city) mapQueryParts.push(hospital.city);
                if (hospital.state) mapQueryParts.push(hospital.state);
            }
            
            const mapQuery = encodeURIComponent(mapQueryParts.join(' ').trim());
            
            // Linha de convênios/SUS/Público/Privado: removida por decisão de produto (não exibir nos cards)
            const conveniosLine = '';
            
            // FASE 2: Exibir subtítulo se disponível (nome do profissional)
            const subtitleHtml = hospital.subtitle ? 
                `<p class="hospital-subtitle" style="font-size: 0.85rem; color: #6b7280; margin-top: 0.25rem; font-style: italic;">
                    ${this.escapeHtml(hospital.subtitle)}
                </p>` : '';
            
            const cardHtml = `
                <div class="hospital-card" data-index="${index}" data-id="${this.escapeHtml(String(cardId))}" data-ownership="${displayEsfera || ''}" data-source="${cardSource}" data-lat="${hospital.lat != null ? this.escapeHtml(String(hospital.lat)) : ''}" data-lon="${hospital.lon != null ? this.escapeHtml(String(hospital.lon)) : ''}" data-cnes="${hospital.cnes ? this.escapeHtml(String(hospital.cnes)) : ''}">
                    <div class="hospital-header">
                        <div class="hospital-header-top">
                            <h4 class="hospital-name">${this.escapeHtml(hospitalName)}</h4>
                            ${subtitleHtml}
                        </div>
                        ${publicPrivateTag ? `<div class="hospital-header-bottom"><div class="hospital-header-tags">${publicPrivateTag}</div></div>` : ''}
                    </div>
                    ${badges.length > 0 ? `<div class="hospital-badges hospital-selo-row">${badges.join('')}</div>` : ''}
                    ${conveniosLine}
                    ${safetyWarning}
                    <div class="hospital-info">
                        ${formattedAddress ? `
                            <p class="hospital-address" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                <i class="fas fa-map-marker-alt" aria-hidden="true"></i> 
                                <span>${this.escapeHtml(formattedAddress)}</span>
                                <button class="hospital-copy-btn" 
                                        data-copy="${this.escapeHtml(formattedAddress)}" 
                                        aria-label="Copiar endereço"
                                        title="Copiar endereço"
                                        style="background: transparent; border: 1px solid #d1d5db; border-radius: 4px; padding: 4px 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;">
                                    <i class="fas fa-copy" aria-hidden="true"></i>
                                </button>
                            </p>
                        ` : ''}
                        ${sanitizedPhone ? `
                            <p class="hospital-phone" style="display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-phone" aria-hidden="true"></i> 
                                <a href="tel:${sanitizedPhone}" 
                                   class="hospital-phone-link" 
                                   data-phone="${sanitizedPhone}">${this.escapeHtml(hospital.phone || sanitizedPhone)}</a>
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
                               style="background: var(--sophia-emergency); color: white; font-weight: 700; flex: 1; min-width: 120px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;">
                                <i class="fas fa-phone" aria-hidden="true"></i> Ligar
                            </a>
                        ` : ''}
                        <a href="https://www.google.com/maps/dir/?api=1&destination=${mapQuery}" 
                           target="_blank" 
                           class="btn-sophia btn-sophia-compact hospital-route-btn"
                           title="Rota até o endereço exato (rua)"
                           style="display: inline-flex; align-items: center; justify-content: center; gap: 6px;">
                            <i class="fas fa-route" aria-hidden="true"></i> Rota
                        </a>
                        <a href="https://www.google.com/maps/search/?api=1&query=${mapQuery}" 
                           target="_blank" 
                           class="btn-sophia btn-sophia-compact hospital-map-btn"
                           title="Ver hospital no mapa: ${this.escapeHtml(formattedAddress)}"
                           style="display: inline-flex; align-items: center; justify-content: center; gap: 6px;">
                            <i class="fas fa-map-marked-alt" aria-hidden="true" style="font-size: 1em; width: 1em; display: inline-block;"></i> Ver no Mapa
                        </a>
                    </div>
                    <!-- FASE 3: Avisos de Dados Incompletos -->
                    ${(function () {
                        if (!hospital.data_validation || hospital.data_validation.is_complete) return '';
                        const warnings = hospital.data_validation.warnings || [];
                        const listHtml = warnings.length > 0
                            ? '<ul style="margin-top: 0.5rem; margin-left: 1.5rem; list-style: disc;">' +
                                warnings.map(w => '<li>' + this.escapeHtml(w) + '</li>').join('') + '</ul>'
                            : '';
                        return '<div style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 6px; padding: 0.75rem; margin-top: 1rem; font-size: 0.75rem; color: #92400e;">' +
                            '<i class="fas fa-exclamation-triangle" style="margin-right: 0.5rem;"></i>' +
                            '<strong>⚠️ Algumas informações podem estar desatualizadas</strong>' + listHtml +
                            '<p style="margin-top: 0.5rem; font-style: italic;">Recomendamos confirmar diretamente com a unidade antes de se deslocar.</p></div>';
                    }.call(this))}
                    <!-- Disclaimer Jurídico - CRÍTICO para Responsabilidade (FASE 1) -->
                    <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 0.75rem; margin-top: 1rem; font-size: 0.75rem; color: #1e40af;">
                        <i class="fas fa-info-circle" style="margin-right: 0.5rem;"></i>
                        <strong>ℹ️ Informações baseadas em dados oficiais do CNES/DataSUS.</strong> 
                        Sempre confirme telefone, horário de atendimento e disponibilidade diretamente com a unidade antes de se deslocar.
                    </div>
                    </div>
                `;
            
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = cardHtml;
            const cardEl = tempDiv.firstElementChild;
            container.appendChild(cardEl);
            
            // Dedupe run-once: card.dataset.susDeduped = "1" para não revarrer cards re-renderizados/lazy
            if (cardEl.dataset.susDeduped === '1') return;
            cardEl.dataset.susDeduped = '1';
            
            // Remover Público/Privado/Filantrópico/SUS/Convênios de todos os cards (decisão de produto)
            cardEl.querySelectorAll('.hospital-tag-public, .hospital-tag-private, .hospital-tag-philanthropic, [data-badge="esfera"], .hospital-badge-info').forEach(el => {
                const t = (el.textContent || '').trim();
                if (!t || t === 'Público' || t === 'Privado' || t === 'Filantrópico' || this.isSusBadge(t)) el.remove();
            });
            cardEl.querySelectorAll('.hospital-tag-sus-yes, .hospital-tag-sus-no, [data-badge="sus"]').forEach(el => el.remove());
            cardEl.querySelectorAll('.hospital-convenios-info, .hospital-convenios').forEach(el => el.remove());
            cardEl.querySelectorAll('.hospital-selo-row').forEach(row => {
                [...row.childNodes].forEach(n => {
                    if (n.nodeType === Node.TEXT_NODE && this.isSusBadge(n.textContent || '')) n.remove();
                });
            });
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
        // "Ver tudo (100 km)" — reconsulta com radius_km=100
        const verTudo100 = this.hospitalsList.querySelector('.hospitals-ver-tudo-100');
        if (verTudo100) {
            verTudo100.addEventListener('click', async () => {
                if (this.lastSearchLat == null || this.lastSearchLon == null) return;
                if (this.hospitalsLoading) this.hospitalsLoading.style.display = 'block';
                try {
                    const out = await this.searchHospitalsNearby(this.lastSearchLat, this.lastSearchLon, 100);
                    const list = Array.isArray(out) ? out : (out && out.list) || [];
                    this.displayHospitals(list, []);
                } catch (err) {
                    console.error('[MAPS DEBUG] Erro ao buscar 100 km:', err);
                    if (this.hospitalsLoading) this.hospitalsLoading.style.display = 'none';
                }
            });
        }

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
            btn.addEventListener('click', (_e) => {
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
// Flag global para evitar execução múltipla
if (window.__chatAppInitialized) {
    console.log('⚠️ [INIT] ChatApp já inicializado, ignorando...');
} else {
    window.__chatAppInitialized = true;
    
    function initializeChatApp() {
        // Verifica novamente dentro da função para garantir
        if (window.chatApp) {
            console.log('⚠️ [INIT] chatApp já existe, ignorando nova inicialização...');
            return;
        }
        
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
        window.__chatAppInitialized = false; // Permite tentar novamente em caso de erro
    }
    }
    
    // Tenta inicializar imediatamente se DOM já está pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeChatApp, { once: true });
    } else {
        // DOM já está pronto, inicializa imediatamente
        // Usa setTimeout para garantir que todos os scripts foram carregados
        setTimeout(initializeChatApp, 0);
    }
    
    // Garante que chatApp está disponível após um pequeno delay
    // Isso ajuda quando há código inline que precisa acessar window.chatApp
    setTimeout(() => {
        if (!window.chatApp && !window.__chatAppInitialized) {
            console.warn('⚠️ [INIT] chatApp não inicializado após timeout, tentando novamente...');
            initializeChatApp();
        }
    }, 100);
    
    // Expõe função de inicialização manual para código inline
    window.initializeChatApp = initializeChatApp;
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

// ADMIN BADGE COMBINADO: PERF + GEO + QUICK-CHECK (?admin=1)
(function () {
    var qs = new URLSearchParams(location.search);
    var isAdmin = (window.SOPHIA_ADMIN === true) || (qs.get('admin') === '1');
    if (!isAdmin) return;

    var TH = {
        startup: Number(window.PERF_T_STARTUP || 2500),
        boot: Number(window.PERF_T_BOOT || 2000),
        first: Number(window.PERF_T_FIRST || 1500),
        coords: Number(window.GEO_T_COORDS || 0.85),
        phone: Number(window.GEO_T_PHONE || 0.85)
    };
    var FBACK = {
        lat: window.QC_LAT != null ? Number(window.QC_LAT) : null,
        lon: window.QC_LON != null ? Number(window.QC_LON) : null,
        radius: window.QC_RADIUS != null ? Number(window.QC_RADIUS) : 25
    };
    var ADMIN_TOKEN = window.ADMIN_TOKEN;

    function ms(v) {
        return v == null ? '?' : Math.round(Number(v)) + ' ms';
    }
    function pct(v) {
        return v == null ? '?' : Math.round(Number(v) * 100) + '%';
    }
    function okWarnPerf(p) {
        var warn = false;
        if (p && p.startup_ms != null && p.startup_ms > TH.startup) warn = true;
        var ob = p && p.overrides && p.overrides.boot_ms;
        if (ob != null && ob > TH.boot) warn = true;
        if (p && p.first_request_ms != null && p.first_request_ms > TH.first) warn = true;
        return warn ? 'warn' : 'ok';
    }
    function okWarnGeo(g) {
        var warn = false;
        if (g && g.coord_coverage_pct != null && g.coord_coverage_pct < TH.coords) warn = true;
        if (g && g.phone_coverage_pct != null && g.phone_coverage_pct < TH.phone) warn = true;
        return warn ? 'warn' : 'ok';
    }

    function getHealth() {
        return fetch('/api/v1/health', { headers: { Accept: 'application/json' }, cache: 'no-store' })
            .then(function (r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .catch(function () { return null; });
    }
    function getQuickCheck(lat, lon, radiusKm) {
        if (lat == null || lon == null) return Promise.resolve(null);
        var u = '/api/v1/debug/overrides/quick_check?lat=' + encodeURIComponent(lat) + '&lon=' + encodeURIComponent(lon) + '&radius_km=' + encodeURIComponent(radiusKm || 25);
        var headers = { Accept: 'application/json' };
        if (ADMIN_TOKEN) headers['X-Admin-Token'] = ADMIN_TOKEN;
        return fetch(u, { headers: headers, cache: 'no-store' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .catch(function () { return null; });
    }
    function refreshOverrides() {
        var headers = ADMIN_TOKEN ? { 'X-Admin-Token': ADMIN_TOKEN } : {};
        return fetch('/api/v1/debug/overrides/refresh', { method: 'POST', headers: headers })
            .then(function (r) { return r.ok; })
            .catch(function () { return false; });
    }
    function fetchQAList() {
        var headers = { Accept: 'application/json' };
        if (ADMIN_TOKEN) headers['X-Admin-Token'] = ADMIN_TOKEN;
        return fetch('/api/v1/debug/qa/list', { headers: headers, cache: 'no-store' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .catch(function () { return null; });
    }

    function render(healthData, qcData) {
        var root = document.getElementById('sophia-admin-badge');
        if (root) root.remove();

        var perf = (healthData && healthData.perf) || {};
        var geo = (healthData && healthData.geo_health) || {};
        var ovr = perf.overrides || {};
        var cls = (okWarnGeo(geo) === 'warn' || okWarnPerf(perf) === 'warn') ? 'warn' : 'ok';

        var badge = document.createElement('div');
        badge.id = 'sophia-admin-badge';
        badge.className = 'sophia-badge ' + cls;

        var l1 = document.createElement('div');
        l1.textContent = '[perf] start ' + ms(perf.startup_ms) + ' • boot ' + ms(ovr && ovr.boot_ms) + ' (' + (ovr && ovr.mode || 'lazy') + ') • first ' + ms(perf.first_request_ms);
        badge.appendChild(l1);

        var l2 = document.createElement('div');
        l2.textContent = '[geo] coords ' + pct(geo.coord_coverage_pct) + ' • tel ' + pct(geo.phone_coverage_pct) + ' • conf ' + (geo.confirmados != null ? geo.confirmados : '?');
        badge.appendChild(l2);

        var l3 = document.createElement('div');
        if (qcData && qcData.ok) {
            var cov = qcData.coverage_pct == null ? '?' : Math.round(qcData.coverage_pct * 100) + '%';
            l3.textContent = '[qc] overrides ' + qcData.override_hits + '/' + qcData.total + ' (' + cov + ') em ' + (FBACK.radius || 25) + 'km';
        } else {
            l3.textContent = '[qc] overrides n/d';
        }
        badge.appendChild(l3);

        var sub = document.createElement('div');
        sub.style.opacity = '0.9';
        sub.textContent = ovr.snapshot ? 'snapshot ' + ovr.snapshot + ' • overrides ' + (ovr.count != null ? ovr.count : '?') : '';
        badge.appendChild(sub);

        var actions = document.createElement('div');
        actions.style.position = 'absolute';
        actions.style.right = '6px';
        actions.style.top = '6px';
        actions.style.display = 'flex';
        actions.style.gap = '6px';

        var btnRefresh = document.createElement('button');
        btnRefresh.className = 'sophia-badge-close';
        btnRefresh.textContent = '\u21BB';
        btnRefresh.title = 'Recarregar overrides do CNES e refazer quick-check';
        btnRefresh.onclick = function () {
            btnRefresh.disabled = true;
            btnRefresh.textContent = '\u2026';
            refreshOverrides().then(function () {
                return getHealth();
            }).then(function (h) {
                var pos = window.__sophia_last_pos || (FBACK.lat != null && FBACK.lon != null ? { lat: FBACK.lat, lon: FBACK.lon } : null);
                return pos ? getQuickCheck(pos.lat, pos.lon, FBACK.radius).then(function (qc) { render(h || healthData, qc || qcData); }) : (h ? render(h, null) : null);
            }).finally(function () {
                btnRefresh.disabled = false;
                btnRefresh.textContent = '\u21BB';
            });
        };
        actions.appendChild(btnRefresh);

        var qaBox = document.createElement('div');
        qaBox.id = 'spb-qa';
        qaBox.style.position = 'absolute';
        qaBox.style.right = '6px';
        qaBox.style.top = '34px';
        qaBox.style.background = 'rgba(255,255,255,0.98)';
        qaBox.style.border = '1px solid rgba(0,0,0,0.08)';
        qaBox.style.borderRadius = '6px';
        qaBox.style.boxShadow = '0 6px 18px rgba(0,0,0,.12)';
        qaBox.style.padding = '8px';
        qaBox.style.minWidth = '240px';
        qaBox.style.display = 'none';
        badge.appendChild(qaBox);

        var btnQA = document.createElement('button');
        btnQA.className = 'sophia-badge-close';
        btnQA.textContent = 'QA';
        btnQA.title = 'Baixar relatórios de QA (CSV)';
        btnQA.onclick = function () {
            btnQA.disabled = true;
            btnQA.textContent = '\u2026';
            fetchQAList().then(function (data) {
                btnQA.disabled = false;
                btnQA.textContent = 'QA';
                qaBox.innerHTML = '';
                if (!data || !data.ok || !data.files || data.files.length === 0) {
                    qaBox.textContent = 'Sem CSVs de QA no reports/';
                } else {
                    var ul = document.createElement('ul');
                    ul.style.listStyle = 'none';
                    ul.style.margin = '0';
                    ul.style.padding = '0';
                    data.files.forEach(function (f) {
                        var li = document.createElement('li');
                        var a = document.createElement('a');
                        a.href = f.url + (ADMIN_TOKEN ? '&admin_token=' + encodeURIComponent(ADMIN_TOKEN) : '');
                        a.textContent = f.name + ' (' + Math.round(f.size / 1024) + ' KB)';
                        a.target = '_blank';
                        a.rel = 'noreferrer';
                        li.appendChild(a);
                        ul.appendChild(li);
                    });
                    qaBox.appendChild(ul);
                }
                qaBox.style.display = qaBox.style.display === 'none' ? 'block' : 'none';
            });
        };
        actions.appendChild(btnQA);

        var btnClose = document.createElement('button');
        btnClose.className = 'sophia-badge-close';
        btnClose.textContent = '\u00D7';
        btnClose.title = 'Fechar';
        btnClose.onclick = function () { badge.remove(); };
        actions.appendChild(btnClose);

        badge.appendChild(actions);
        document.body.appendChild(badge);
    }

    (function init() {
        getHealth().then(function (h) {
            var pos = window.__sophia_last_pos || (FBACK.lat != null && FBACK.lon != null ? { lat: FBACK.lat, lon: FBACK.lon } : null);
            var qcPromise = pos ? getQuickCheck(pos.lat, pos.lon, FBACK.radius) : Promise.resolve(null);
            qcPromise.then(function (qc) {
                if (h) render(h, qc);
            });
        });
    })();

    window.sophiaAdminBadgeUpdatePos = function (lat, lon) {
        try {
            window.__sophia_last_pos = { lat: lat, lon: lon };
            getHealth().then(function (h) {
                return getQuickCheck(lat, lon, FBACK.radius).then(function (qc) {
                    if (h) render(h, qc);
                });
            });
        } catch (e) {}
    };
})();

