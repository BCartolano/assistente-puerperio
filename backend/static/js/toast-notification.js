/**
 * Toast Notification System
 * Sistema simples de notificações toast para feedback de erros e sucessos
 */

class ToastNotification {
    constructor() {
        this.toastContainer = null;
        this.init();
    }

    init() {
        // Cria container de toasts se não existe
        if (!document.getElementById('toast-container')) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toast-container';
            this.updatePosition();
            document.body.appendChild(this.toastContainer);
        } else {
            this.toastContainer = document.getElementById('toast-container');
            this.updatePosition();
        }
        
        // Atualiza posição ao redimensionar (mobile/desktop)
        window.addEventListener('resize', () => {
            this.updatePosition();
        });
    }
    
    updatePosition() {
        if (!this.toastContainer) return;
        
        // Detecta se é mobile para ajustar posição
        const isMobile = window.innerWidth <= 1023;
        
        this.toastContainer.style.cssText = `
            position: fixed;
            ${isMobile ? 'top: 1rem;' : 'top: 1rem;'}
            ${isMobile ? 'left: 50%;' : 'right: 1rem;'}
            ${isMobile ? 'transform: translateX(-50%);' : 'transform: none;'}
            z-index: 10001;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            max-width: ${isMobile ? '90%' : '320px'};
            width: auto;
            pointer-events: none;
        `;
    }

    /**
     * Mostra uma notificação toast
     * @param {string} message - Mensagem a ser exibida
     * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duração em ms (padrão: 4000)
     */
    show(message, type = 'info', duration = 4000) {
        if (!this.toastContainer) {
            this.init();
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        // Ícone baseado no tipo
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        // Cores baseadas no tipo
        const colors = {
            success: {
                bg: 'rgba(76, 175, 80, 0.95)',
                border: 'rgba(76, 175, 80, 1)'
            },
            error: {
                bg: 'rgba(244, 67, 54, 0.95)',
                border: 'rgba(244, 67, 54, 1)'
            },
            warning: {
                bg: 'rgba(255, 152, 0, 0.95)',
                border: 'rgba(255, 152, 0, 1)'
            },
            info: {
                bg: 'rgba(33, 150, 243, 0.95)',
                border: 'rgba(33, 150, 243, 1)'
            }
        };

        const color = colors[type] || colors.info;
        const isMobileToast = window.innerWidth <= 1023;

        toast.style.cssText = `
            background: ${color.bg};
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border-left: 4px solid ${color.border};
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: ${isMobileToast ? '0.85rem' : '0.9rem'};
            font-weight: 500;
            pointer-events: auto;
            animation: toastSlideIn 0.3s ease-out;
            max-width: ${isMobileToast ? '90%' : '320px'};
            word-wrap: break-word;
        `;

        toast.innerHTML = `
            <span style="font-size: 1.2rem; flex-shrink: 0;">${icons[type] || icons.info}</span>
            <span style="flex: 1;">${this.escapeHtml(message)}</span>
            <button class="toast-close" style="
                background: none;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                padding: 0;
                margin-left: 0.5rem;
                flex-shrink: 0;
                opacity: 0.8;
                transition: opacity 0.2s;
            " aria-label="Fechar">&times;</button>
        `;

        // Adiciona CSS de animação se não existe
        if (!document.getElementById('toast-animations')) {
            const style = document.createElement('style');
            style.id = 'toast-animations';
            const isMobileAnim = window.innerWidth <= 1023;
            style.textContent = `
                @keyframes toastSlideIn {
                    from {
                        transform: ${isMobileAnim ? 'translateY(-100%)' : 'translateX(100%)'};
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0) translateY(0);
                        opacity: 1;
                    }
                }
                @keyframes toastSlideOut {
                    from {
                        transform: translateX(0) translateY(0);
                        opacity: 1;
                    }
                    to {
                        transform: ${isMobileAnim ? 'translateY(-100%)' : 'translateX(100%)'};
                        opacity: 0;
                    }
                }
                .toast-closing {
                    animation: toastSlideOut 0.3s ease-in forwards;
                }
            `;
            document.head.appendChild(style);
        }

        // Botão de fechar
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.remove(toast));
        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.opacity = '1';
        });
        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.opacity = '0.8';
        });

        this.toastContainer.appendChild(toast);

        // Remove automaticamente após duração
        if (duration > 0) {
            setTimeout(() => {
                this.remove(toast);
            }, duration);
        }

        return toast;
    }

    /**
     * Remove toast
     */
    remove(toast) {
        if (!toast || !toast.parentNode) return;

        toast.classList.add('toast-closing');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    /**
     * Métodos de conveniência
     */
    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    /**
     * Escapa HTML para prevenir XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Exporta instância global
window.ToastNotification = ToastNotification;
window.toast = new ToastNotification();
