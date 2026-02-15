/**
 * Mobile Navigation - Sistema de Abas Inferiores
 * Gerencia a navegação entre Chat, Vacinas e Dicas no mobile
 */

class MobileNavigation {
    constructor() {
        this.currentSection = 'chat'; // Seção inicial
        this.sections = {
            chat: {
                element: null,
                init: () => this.initChatSection()
            },
            vacinas: {
                element: null,
                init: () => this.initVacinasSection()
            },
            dicas: {
                element: null,
                init: () => this.initDicasSection()
            }
        };
        
        this.init();
    }
    
    init() {
        // Só inicializa em mobile
        if (window.innerWidth > 1023) {
            return;
        }
        
        // Configura elementos das seções
        this.sections.chat.element = document.querySelector('.chat-area, .welcome-message');
        this.sections.vacinas.element = document.getElementById('vaccination-timeline-container') || document.querySelector('#vaccination-timeline');
        this.sections.dicas.element = document.getElementById('mobile-dicas-container');
        
        // Bind eventos dos botões de navegação (se existirem)
        const navItems = document.querySelectorAll('.bottom-nav-item');
        if (navItems.length > 0) {
            navItems.forEach(item => {
                item.addEventListener('click', (e) => {
                    const section = e.currentTarget.dataset.section;
                    this.switchSection(section);
                });
            });
        }
        
        // Inicializa seção atual
        this.switchSection('chat');
        
        // Listener para resize (caso usuário rotacione tela)
        window.addEventListener('resize', () => {
            const bottomNav = document.querySelector('.bottom-nav');
            if (window.innerWidth <= 1023 && bottomNav && !bottomNav.style.display) {
                // Força re-inicialização se voltar para mobile
                this.switchSection(this.currentSection);
            }
        });
    }
    
    switchSection(sectionName) {
        if (this.currentSection === sectionName) {
            return; // Já está na seção
        }
        
        // Se estava em Chat e está mudando, cancela requisições ativas
        // Isso libera memória e previne requisições desnecessárias
        if (this.currentSection === 'chat' && sectionName !== 'chat') {
            if (window.apiClient && typeof window.apiClient.cancelAll === 'function') {
                window.apiClient.cancelAll(); // Cancela todas as requisições ativas
                if (window.console && typeof window.console.log === 'function') {
                    console.log('[MobileNav] Requisições canceladas ao trocar de aba');
                }
            }
        }
        
        // Atualiza seção atual
        this.currentSection = sectionName;
        
        // Oculta todas as seções
        this.hideAllSections();
        
        // Mostra seção selecionada
        this.showSection(sectionName);
        
        // Atualiza navegação visual
        this.updateNavButtons(sectionName);
        
        // Inicializa seção se necessário
        if (this.sections[sectionName] && this.sections[sectionName].init) {
            this.sections[sectionName].init();
        }
        
        // Preserva estado do chat se necessário
        this.preserveChatState();
    }
    
    hideAllSections() {
        // Oculta welcome-message e chat-area (desktop)
        const chatArea = document.querySelector('.chat-area');
        const welcomeMessage = document.querySelector('.welcome-message');
        const chatMessages = document.getElementById('chat-messages');
        const timelineContainer = document.getElementById('vaccination-timeline-container');
        const dicasContainer = document.getElementById('mobile-dicas-container');
        
        // Remove classes active
        if (chatArea) chatArea.classList.remove('mobile-section', 'active');
        if (welcomeMessage) welcomeMessage.classList.remove('mobile-section', 'active');
        if (timelineContainer) timelineContainer.classList.remove('mobile-section', 'active');
        if (dicasContainer) {
            dicasContainer.classList.remove('active', 'mobile-section');
            dicasContainer.style.display = 'none';
        }
        
        // Oculta seções em mobile
        if (window.innerWidth <= 1023) {
            if (chatArea) chatArea.style.display = 'none';
            if (welcomeMessage) welcomeMessage.style.display = 'none';
            if (chatMessages) chatMessages.style.display = 'none';
            if (timelineContainer) timelineContainer.style.display = 'none';
        }
    }
    
    showSection(sectionName) {
        if (sectionName === 'chat') {
            // Mostra chat-area ou welcome-message
            const chatArea = document.querySelector('.chat-area');
            const welcomeMessage = document.querySelector('.welcome-message');
            const chatMessages = document.getElementById('chat-messages');
            
            // Se chat já está ativo, mostra mensagens
            if (chatMessages && chatMessages.children.length > 0) {
                if (chatArea) chatArea.style.display = 'flex';
                if (chatMessages) chatMessages.style.display = 'flex';
            } else {
                // Caso contrário, mostra welcome message
                if (welcomeMessage) welcomeMessage.style.display = 'block';
            }
        } else if (sectionName === 'vacinas') {
            // Mostra timeline de vacinação
            const timelineContainer = document.getElementById('vaccination-timeline-container');
            if (timelineContainer) {
                timelineContainer.style.display = 'block';
                // Se timeline ainda não foi inicializada, inicializa agora
                if (window.vaccinationTimeline && typeof window.vaccinationTimeline.init === 'function') {
                    window.vaccinationTimeline.init();
                }
            }
        } else if (sectionName === 'dicas') {
            // Mostra container de dicas
            const dicasContainer = document.getElementById('mobile-dicas-container');
            if (dicasContainer) {
                dicasContainer.classList.add('active');
                // Carrega conteúdo se ainda não foi carregado
                if (!dicasContainer.hasAttribute('data-loaded')) {
                    this.loadDicasContent();
                }
            }
        }
    }
    
    updateNavButtons(activeSection) {
        const navItems = document.querySelectorAll('.bottom-nav-item');
        if (navItems.length > 0) {
            navItems.forEach(item => {
                if (item.dataset.section === activeSection) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }
    }
    
    initChatSection() {
        // Chat já está inicializado, apenas garante que está visível
        // Preserva histórico de mensagens
    }
    
    initVacinasSection() {
        // Inicializa timeline se necessário
        if (window.vaccinationTimeline && typeof window.vaccinationTimeline.init === 'function') {
            window.vaccinationTimeline.init();
        } else if (window.chatApp && typeof window.chatApp.showVacinas === 'function') {
            // Fallback: usa método do chatApp
            window.chatApp.showVacinas();
        }
    }
    
    initDicasSection() {
        // Carrega conteúdo de dicas
        this.loadDicasContent();
    }
    
    loadDicasContent() {
        const dicasContainer = document.getElementById('mobile-dicas-container');
        if (!dicasContainer || dicasContainer.hasAttribute('data-loaded')) {
            return;
        }
        
        // Busca conteúdo das sidebars desktop (que já foram carregadas)
        const orientacaoCard = document.getElementById('orientacao-card');
        const affirmationCard = document.getElementById('affirmation-card');
        const agendaCard = document.getElementById('agenda-de-vacinacao-card');
        
        // Container principal com margens de 15px
        let html = '<div class="mobile-dicas-section"><h2 style="color: var(--color-primary-warm); margin-bottom: 1.5rem; text-align: center; padding: 0 15px;">💡 Orientações e Recursos</h2>';
        
        // Orientação
        if (orientacaoCard) {
            const orientacaoText = orientacaoCard.querySelector('.orientacao-text')?.textContent || 'Carregando orientação...';
            html += `
                <div class="mobile-dica-card">
                    <h3><span class="card-icon"><i class="fas fa-tint"></i></span>Orientação</h3>
                    <p>${this.escapeHtml(orientacaoText)}</p>
                </div>
            `;
        }
        
        // Afirmação
        if (affirmationCard) {
            const affirmationText = affirmationCard.querySelector('.affirmation-text')?.textContent || 'Carregando afirmação...';
            html += `
                <div class="mobile-dica-card">
                    <h3><span class="card-icon"><i class="fas fa-sun"></i></span>Afirmação</h3>
                    <p>${this.escapeHtml(affirmationText)}</p>
                </div>
            `;
        }
        
        // Agenda de Saúde
        if (agendaCard) {
            const agendaContent = agendaCard.querySelector('.agenda-content')?.innerHTML || '';
            html += `
                <div class="mobile-dica-card">
                    <h3><span class="card-icon"><i class="fas fa-calendar-check"></i></span>Agenda de Vacinação</h3>
                    <div class="agenda-mobile-content">${agendaContent}</div>
                </div>
            `;
        }
        
        // Card de Feedback (ao final da lista)
        html += `
            <div class="mobile-dica-card feedback-card" id="feedback-card" style="cursor: pointer; opacity: 0.95;">
                <h3><span class="card-icon">💬</span>Como está sua experiência?</h3>
                <p style="margin-top: 0.5rem; color: var(--text-warm-medium, #888);">Sua opinião nos ajuda a cuidar melhor de você 💕</p>
            </div>
        `;
        
        html += '</div>';
        
        dicasContainer.innerHTML = html;
        dicasContainer.setAttribute('data-loaded', 'true');
        
        // Bind do card de feedback
        const feedbackCard = document.getElementById('feedback-card');
        if (feedbackCard) {
            feedbackCard.addEventListener('click', () => {
                this.openFeedbackModal();
            });
        }
        
        // Lazy loading: Vídeos do YouTube só carregam quando aba Dicas é ativada pela primeira vez
        // Isso economiza dados no 4G (iframes só carregam quando necessário)
        this.loadVideosLazy();
    }
    
    loadVideosLazy() {
        const dicasContainer = document.getElementById('mobile-dicas-container') || document.querySelector('[data-dicas-container]');
        // Verifica se a sidebar direita (desktop) tem vídeos renderizados
        const desktopVideosList = document.getElementById('videos-list');
        if (!desktopVideosList) {
            // Se não existe sidebar desktop, vídeos não foram inicializados ainda
            // Aguarda um pouco e tenta novamente
            setTimeout(() => {
                if (!dicasContainer || !dicasContainer.hasAttribute('data-videos-loaded')) {
                    this.loadVideosLazy();
                }
            }, 500);
            return;
        }
        
        const videosCard = document.getElementById('mobile-videos-card');
        if (!videosCard) {
            // Cria card de vídeos se não existe
            if (!dicasContainer) return;
            const section = dicasContainer.querySelector('.mobile-dicas-section');
            if (section) {
                const videoCardHtml = `
                    <div class="mobile-dica-card" id="mobile-videos-card">
                        <h3><span class="card-icon">📺</span>Vídeos Educativos</h3>
                        <div id="mobile-videos-list"></div>
                    </div>
                `;
                section.insertAdjacentHTML('beforeend', videoCardHtml);
            }
        }
        
        const videosList = document.getElementById('mobile-videos-list');
        if (!videosList || videosList.hasAttribute('data-loaded')) {
            return; // Já foi carregado
        }
        
        // Copia apenas thumbnails dos vídeos (iframes serão criados apenas ao clicar)
        const videoItems = desktopVideosList.querySelectorAll('.video-item');
        if (videoItems.length > 0) {
            videoItems.forEach(item => {
                const clonedItem = item.cloneNode(true);
                // Remove event listeners antigos e adiciona novo para lazy load
                const newItem = clonedItem.cloneNode(true);
                // Garante que o clique abrirá o modal corretamente
                newItem.addEventListener('click', () => {
                    const videoIndex = parseInt(newItem.dataset.videoIndex);
                    // Abre modal usando função do sidebar-content.js
                    if (typeof window.openVideoModal === 'function') {
                        // window.openVideoModal está disponível globalmente se necessário
                    } else {
                        // Tenta usar renderVideos novamente para garantir que está disponível
                        const desktopVideoItem = desktopVideosList.querySelector(`[data-video-index="${videoIndex}"]`);
                        if (desktopVideoItem) {
                            desktopVideoItem.click(); // Simula clique no item desktop
                        }
                    }
                });
                videosList.appendChild(newItem);
            });
        }
        
        videosList.setAttribute('data-loaded', 'true');
        if (videosCard && videoItems.length === 0) {
            videosCard.style.display = 'none'; // Oculta se não há vídeos
        }
    }
    
    preserveChatState() {
        // Garante que o estado do chat não é perdido ao trocar de aba
        // O histórico já está salvo no localStorage e no backend
        
        // Se chatApp existe, garante que histórico está preservado
        if (window.chatApp && typeof window.chatApp.loadChatHistory === 'function') {
            // Histórico já é carregado automaticamente no initMainApp
            // Apenas garante que está preservado
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    openFeedbackModal() {
        // Cria modal se não existe
        let modal = document.getElementById('feedback-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'feedback-modal';
            modal.className = 'feedback-modal';
            modal.innerHTML = `
                <div class="feedback-modal-backdrop" id="feedback-modal-backdrop"></div>
                <div class="feedback-modal-content">
                    <button class="feedback-modal-close" id="feedback-modal-close" aria-label="Fechar">&times;</button>
                    <h2>💬 Como está sua experiência?</h2>
                    <p style="color: #888; margin-bottom: 1.5rem;">Sua opinião é muito importante para nós!</p>
                    
                    <!-- Pergunta 1 aparece PRIMEIRO (validação da Mary) -->
                    <div class="feedback-questions" id="feedback-questions-initial">
                        <div class="feedback-question">
                            <label id="feedback-question1-label-initial" style="display: block; margin-bottom: 0.75rem; font-weight: 600; color: #555;">
                                A Sophia te ajudou a se sentir mais calma hoje?
                            </label>
                            <input type="text" id="feedback-question1-initial" placeholder="Sua resposta..." maxlength="200">
                        </div>
                    </div>
                    
                    <div class="feedback-rating" style="margin-top: 1.5rem;">
                        <p style="margin-bottom: 0.75rem; font-weight: 600;">Como você está se sentindo?</p>
                        <div class="feedback-emoji-buttons">
                            <button class="feedback-emoji-btn" data-rating="😊" aria-label="Feliz">
                                😊
                            </button>
                            <button class="feedback-emoji-btn" data-rating="😌" aria-label="Calma">
                                😌
                            </button>
                            <button class="feedback-emoji-btn" data-rating="😔" aria-label="Triste">
                                😔
                            </button>
                        </div>
                    </div>
                    
                    <div class="feedback-questions" id="feedback-questions" style="display: none;">
                        <div class="feedback-question" style="margin-top: 1rem;">
                            <label id="feedback-question2-label"></label>
                            <input type="text" id="feedback-question2" placeholder="Sua resposta..." maxlength="200">
                        </div>
                    </div>
                    
                    <div class="feedback-comment">
                        <label for="feedback-comment-text">Gostaria de compartilhar algo mais?</label>
                        <textarea id="feedback-comment-text" placeholder="Seu comentário (opcional)..." maxlength="500" rows="3"></textarea>
                    </div>
                    
                    <button class="feedback-submit-btn" id="feedback-submit-btn" disabled>
                        Enviar Feedback 💕
                    </button>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Bind eventos
            const backdrop = document.getElementById('feedback-modal-backdrop');
            const closeBtn = document.getElementById('feedback-modal-close');
            const emojiButtons = modal.querySelectorAll('.feedback-emoji-btn');
            const submitBtn = document.getElementById('feedback-submit-btn');
            
            // Fecha ao clicar no backdrop ou botão fechar
            backdrop.addEventListener('click', () => this.closeFeedbackModal());
            closeBtn.addEventListener('click', () => this.closeFeedbackModal());
            
            // Seleção de emoji - usa data attribute para armazenar rating selecionado
            emojiButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    emojiButtons.forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                    // Armazena rating no modal para acesso posterior
                    modal.dataset.selectedRating = btn.dataset.rating;
                    
                    // Mostra segunda pergunta após selecionar emoji
                    const questionsDiv = document.getElementById('feedback-questions');
                    if (questionsDiv) {
                        questionsDiv.style.display = 'block';
                        // Carrega pergunta 2 (definida pela Mary - ver docs/PERGUNTAS_FEEDBACK_MARY.md)
                        this.loadFeedbackQuestion2();
                    }
                    
                    // Habilita botão após selecionar emoji E preencher pergunta 1 (ou deixar vazio)
                    this.updateSubmitButton();
                });
            });
            
            // Habilita/desabilita botão baseado em preenchimento
            const question1Input = document.getElementById('feedback-question1-initial');
            if (question1Input) {
                question1Input.addEventListener('input', () => this.updateSubmitButton());
            }
            
            // Envia feedback
            submitBtn.addEventListener('click', () => {
                const selectedRating = modal.dataset.selectedRating || '';
                this.submitFeedback(selectedRating);
            });
        }
        
        // Mostra modal
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Fecha ao pressionar ESC
        this.feedbackModalEscHandler = (e) => {
            if (e.key === 'Escape') {
                this.closeFeedbackModal();
            }
        };
        document.addEventListener('keydown', this.feedbackModalEscHandler);
    }
    
    loadFeedbackQuestion2() {
        // Pergunta 2 aparece após selecionar emoji (definida pela Mary)
        // Ver docs/PERGUNTAS_FEEDBACK_MARY.md
        const question2Label = document.getElementById('feedback-question2-label');
        
        if (question2Label) {
            question2Label.textContent = 'O que mais você gostaria de ver aqui?';
        }
    }
    
    updateSubmitButton() {
        // Habilita botão se emoji foi selecionado
        const submitBtn = document.getElementById('feedback-submit-btn');
        const selectedRating = document.getElementById('feedback-modal')?.dataset.selectedRating;
        
        if (submitBtn && selectedRating) {
            submitBtn.disabled = false;
        }
    }
    
    closeFeedbackModal() {
        const modal = document.getElementById('feedback-modal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
            
            // Remove handler ESC
            if (this.feedbackModalEscHandler) {
                document.removeEventListener('keydown', this.feedbackModalEscHandler);
            }
        }
    }
    
    async submitFeedback(rating) {
        // Pega pergunta 1 (aparece primeiro, antes dos emojis)
        const question1 = document.getElementById('feedback-question1-initial')?.value || '';
        // Pega pergunta 2 (aparece após selecionar emoji)
        const question2 = document.getElementById('feedback-question2')?.value || '';
        const comment = document.getElementById('feedback-comment-text')?.value || '';
        
        const submitBtn = document.getElementById('feedback-submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';
        
        try {
            const response = await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    rating: rating,
                    question1: question1,
                    question2: question2,
                    comment: comment
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Fecha modal
                this.closeFeedbackModal();
                
                // Mostra toast de agradecimento (mensagem definida pela Mary - ver docs/PERGUNTAS_FEEDBACK_MARY.md)
                const thankYouMessage = data.message || 'Obrigada por nos ajudar a cuidar melhor de você! 💕';
                if (window.toast && typeof window.toast.success === 'function') {
                    window.toast.success(thankYouMessage, 5000);
                } else if (window.showToast) {
                    window.showToast(thankYouMessage, 'success', 5000);
                }
            } else {
                throw new Error(data.error || 'Erro ao enviar feedback');
            }
        } catch (error) {
            console.error('Erro ao enviar feedback:', error);
            if (window.toast && typeof window.toast.error === 'function') {
                window.toast.error('Não foi possível enviar seu feedback. Tente novamente mais tarde.', 5000);
            } else if (window.showToast) {
                window.showToast('Não foi possível enviar seu feedback. Tente novamente mais tarde.', 'error', 5000);
            }
            submitBtn.disabled = false;
            submitBtn.textContent = 'Enviar Feedback 💕';
        }
    }
}

// Inicializa quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.mobileNav = new MobileNavigation();
    });
} else {
    window.mobileNav = new MobileNavigation();
}
