/**
 * Device Detector - Sistema de Detecção e Adaptação Dinâmica de Dispositivos
 * Detecta tamanho da tela, orientação (portrait/landscape) e ajusta automaticamente
 * a página de cadastro e menu inicial para cada tipo de dispositivo
 */

(function() {
    'use strict';

    // Classe principal para detecção de dispositivo
    class DeviceDetector {
        constructor() {
            this.width = window.innerWidth;
            this.height = window.innerHeight;
            this.orientation = this.getOrientation();
            this.deviceType = this.getDeviceType();
            this.screenSize = this.getScreenSize();
            
            // Bind methods
            this.handleResize = this.handleResize.bind(this);
            this.handleOrientationChange = this.handleOrientationChange.bind(this);
            
            // Inicializa a detecção
            this.init();
        }

        /**
         * Detecta a orientação da tela
         * @returns {string} 'portrait' ou 'landscape'
         */
        getOrientation() {
            // Verifica primeiro pela API de orientação se disponível
            if (window.screen && window.screen.orientation) {
                const angle = window.screen.orientation.angle || window.screen.orientation;
                return (angle === 90 || angle === -90 || angle === 270) ? 'landscape' : 'portrait';
            }
            
            // Fallback: usa largura vs altura
            return this.width > this.height ? 'landscape' : 'portrait';
        }

                /**
         * Detecta o tipo de dispositivo
         * @returns {string} 'mobile', 'tablet' ou 'desktop'
         */
        getDeviceType() {
            const width = this.width;

            if (width > 1024) {
                return 'desktop';
            } else if (width > 768) {
                return 'tablet';
            } else {
                return 'mobile';
            }
        }

        /**
         * Detecta o tamanho da tela (categorias específicas)
         * @returns {string} Categoria do tamanho da tela
         */
        getScreenSize() {
            const width = this.width;
            const deviceType = this.getDeviceType();

            if (width > 1024) {
                return 'desktop-md';
            } else if (width > 768) {
                return this.orientation === 'portrait' ? 'tablet-portrait' : 'tablet-landscape';
            } else {
                return 'mobile';
            }
        }

        /**
         * Aplica classes dinâmicas ao body e elementos principais
         */
        applyDeviceClasses() {
            const body = document.body;
            const loginScreen = document.getElementById('login-screen');
            const mainContainer = document.getElementById('main-container');

            // Remove classes antigas de dispositivo
            body.className = body.className.replace(/\b(device-|orientation-|screen-)[^\s]*/g, '').trim();

            // Aplica novas classes
            body.classList.add(`device-${this.deviceType}`);
            body.classList.add(`orientation-${this.orientation}`);
            body.classList.add(`screen-${this.screenSize}`);

            // Aplica classes específicas aos containers
            if (loginScreen) {
                loginScreen.classList.remove('device-mobile', 'device-tablet', 'device-desktop', 
                                           'orientation-portrait', 'orientation-landscape');
                loginScreen.classList.add(`device-${this.deviceType}`, `orientation-${this.orientation}`);
            }

            if (mainContainer) {
                mainContainer.classList.remove('device-mobile', 'device-tablet', 'device-desktop',
                                             'orientation-portrait', 'orientation-landscape');
                mainContainer.classList.add(`device-${this.deviceType}`, `orientation-${this.orientation}`);
            }

            // Log para debug removido em produção para melhorar score do Lighthouse
            // const deviceInfo = {
            //     width: this.width,
            //     height: this.height,
            //     orientation: this.orientation,
            //     deviceType: this.deviceType,
            //     screenSize: this.screenSize
            // };
            // console.log("📱 [Device Detector]", JSON.stringify(deviceInfo, null, 2));
        }

        /**
         * Ajusta estilos específicos baseado na detecção
         */
        adjustLayout() {
            const loginContainer = document.querySelector('.login-container');
            const welcomeContent = document.querySelector('.welcome-content');
            const quickQuestions = document.querySelector('.quick-questions');

            // Ajustes para tela de login
            if (loginContainer) {
                // Mobile portrait - reduz padding e font sizes
                if (this.orientation === 'portrait' && this.deviceType === 'mobile') {
                    loginContainer.style.padding = '1.5rem 1rem';
                }
                // Mobile landscape - ajusta para aproveitar largura
                else if (this.orientation === 'landscape' && this.deviceType === 'mobile') {
                    loginContainer.style.padding = '1rem 1.5rem';
                    loginContainer.style.maxWidth = '90%';
                }
                // Desktop - volta ao padrão
                else {
                    loginContainer.style.padding = '';
                    loginContainer.style.maxWidth = '';
                }
            }

            // Ajustes para welcome content
            if (welcomeContent) {
                if (this.orientation === 'portrait' && this.deviceType === 'mobile') {
                    welcomeContent.style.padding = '1rem 0.8rem';
                } else if (this.orientation === 'landscape' && this.deviceType === 'mobile') {
                    welcomeContent.style.padding = '0.8rem 1rem';
                } else {
                    welcomeContent.style.padding = '';
                }
            }

            // Ajustes para quick questions
            if (quickQuestions) {
                if (this.orientation === 'landscape' && this.deviceType === 'mobile') {
                    // Em landscape, pode usar 2 colunas em telas maiores
                    const maxWidth = Math.max(this.width, this.height);
                    if (maxWidth > 667) {
                        quickQuestions.style.gridTemplateColumns = 'repeat(2, 1fr)';
                    } else {
                        quickQuestions.style.gridTemplateColumns = '1fr';
                    }
                } else {
                    quickQuestions.style.gridTemplateColumns = '';
                }
            }
        }

        /**
         * Handler para redimensionamento da janela
         */
        handleResize() {
            // Debounce para evitar muitas execuções
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.width = window.innerWidth;
                this.height = window.innerHeight;
                const newOrientation = this.getOrientation();
                const newDeviceType = this.getDeviceType();
                const newScreenSize = this.getScreenSize();

                // Verifica se houve mudança significativa
                if (newOrientation !== this.orientation || 
                    newDeviceType !== this.deviceType || 
                    newScreenSize !== this.screenSize) {
                    
                    this.orientation = newOrientation;
                    this.deviceType = newDeviceType;
                    this.screenSize = newScreenSize;
                    
                    this.applyDeviceClasses();
                    this.adjustLayout();
                }
            }, 150);
        }

        /**
         * Handler para mudança de orientação
         */
        handleOrientationChange() {
            // Delay para garantir que as dimensões foram atualizadas
            setTimeout(() => {
                this.width = window.innerWidth;
                this.height = window.innerHeight;
                this.orientation = this.getOrientation();
                this.deviceType = this.getDeviceType();
                this.screenSize = this.getScreenSize();
                
                this.applyDeviceClasses();
                this.adjustLayout();
            }, 100);
        }

        /**
         * Inicializa o detector de dispositivo
         */
        init() {
            // Aplica classes iniciais
            this.applyDeviceClasses();
            this.adjustLayout();

            // Adiciona listeners
            window.addEventListener('resize', this.handleResize);
            window.addEventListener('orientationchange', this.handleOrientationChange);
            
            // Para dispositivos que suportam screen.orientation
            if (window.screen && window.screen.orientation) {
                window.screen.orientation.addEventListener('change', this.handleOrientationChange);
            }

            // Verifica novamente após um pequeno delay para garantir que tudo está carregado
            setTimeout(() => {
                this.handleResize();
            }, 300);
        }

        /**
         * Retorna informações atuais do dispositivo
         * @returns {Object} Informações do dispositivo
         */
        getInfo() {
            return {
                width: this.width,
                height: this.height,
                orientation: this.orientation,
                deviceType: this.deviceType,
                screenSize: this.screenSize
            };
        }
    }

    // Inicializa o detector imediatamente e também quando o DOM estiver pronto
    // Isso garante que funcione mesmo em dispositivos mais lentos
    function initDetector() {
        if (!window.deviceDetector) {
            window.deviceDetector = new DeviceDetector();
        } else {
            // Se já existe, apenas atualiza
            window.deviceDetector.applyDeviceClasses();
            window.deviceDetector.adjustLayout();
        }
    }

    // Tenta inicializar imediatamente
    if (document.body) {
        initDetector();
    }

    // E também quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDetector);
    } else {
        // DOM já está pronto, mas vamos garantir que foi inicializado
        initDetector();
    }

    // E também após um pequeno delay para garantir que tudo está carregado
    setTimeout(initDetector, 100);

})();
