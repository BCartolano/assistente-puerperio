/**
 * Sidebar Content Manager
 * Gerencia conteúdo das sidebars: Dicas do Dia, Afirmações e Vídeos
 */

(function() {
    'use strict';

    // Dicas do Dia (baseadas em evidências)
    const tips = [
        {
            icon: '🌙',
            text: 'Descanse sempre que puder. Estudos mostram que mães que descansam adequadamente nos primeiros 15 dias têm melhor recuperação física e emocional. O sono fragmentado é normal - aproveite os cochilos do bebê para descansar também.',
            id: 'tip-1'
        },
        {
            icon: '💧',
            text: 'Mantenha-se hidratada e alimente-se bem. Se estiver amamentando, seu corpo precisa de 500-600 calorias extras por dia. Beba água sempre que amamentar e priorize alimentos nutritivos para sua recuperação.',
            id: 'tip-2'
        },
        {
            icon: '🤝',
            text: 'Pedir ajuda não é sinal de fraqueza - é sabedoria. Pesquisas mostram que mães com rede de apoio adequada têm menor risco de depressão pós-parto. Aceite ajuda com tarefas domésticas, cuidados com o bebê e seu próprio descanso.',
            id: 'tip-3'
        },
        {
            icon: '💙',
            text: 'Fique atenta aos seus sentimentos. Baby blues (tristeza leve) é comum nas primeiras 2 semanas. Se a tristeza persistir, for intensa ou vier acompanhada de pensamentos negativos sobre você ou o bebê, procure ajuda profissional.',
            id: 'tip-4'
        },
        {
            icon: '🚶‍♀️',
            text: 'Movimente-se gradualmente conforme se sentir confortável. Caminhadas leves após liberação médica ajudam na recuperação física e bem-estar emocional. Evite exercícios intensos nas primeiras 6 semanas.',
            id: 'tip-5'
        }
    ];

    // Frases de Afirmação Positiva
    const affirmations = [
        "Eu sou a melhor mãe para o meu filho.",
        "Estou fazendo o melhor que posso, e isso é suficiente.",
        "Aprendo e me torno uma mãe melhor a cada dia que passa.",
        "Acredito em mim mesma e aceito que sou suficiente.",
        "Sou uma mãe suficientemente boa.",
        "Ao cuidar de mim, ensino aos meus filhos o valor do autocuidado.",
        "Não só não há problema em pedir ajuda, como eu mereço ajuda.",
        "Eu mereço descanso e momentos de paz.",
        "Cuidar de mim não é egoísmo, é necessidade.",
        "Meu bem-estar importa tanto quanto o do meu bebê.",
        "Sou forte e resiliente diante dos desafios.",
        "Ser mãe é superar desafios diários e se reinventar a cada momento.",
        "Cada dia é uma nova oportunidade para aprender e crescer.",
        "Eu confio no meu potencial para cuidar do meu bebê.",
        "Estou fazendo o melhor que posso com as informações que tenho.",
        "Estou grata pelos meus filhos, pelo meu companheiro e pela minha família.",
        "Vivo uma vida repleta de amor.",
        "Apesar dos desafios, meus filhos se sentem amados e seguros.",
        "Hoje é um novo dia para a nossa família.",
        "O amor de mãe é capaz de me dar força para superar qualquer dificuldade.",
        "É normal sentir cansaço, dúvidas e emoções intensas.",
        "Não preciso ser perfeita, apenas presente.",
        "Cada mãe tem sua própria jornada, e a minha é única.",
        "Está tudo bem não saber tudo - estou aprendendo.",
        "Minhas emoções são válidas e merecem ser acolhidas."
    ];

    // Vídeos (IDs reais do YouTube)
    // ⚠️ IMPORTANTE: Substitua os IDs abaixo pelos IDs reais encontrados no YouTube
    // Verifique se cada vídeo permite embedding antes de usar
    // Consulte docs/videos-youtube-ids.md para instruções detalhadas
    const videos = [
        {
            id: 'VIDEO_ID_1', // TODO: Substituir por ID real - Cuidados Primeiros Dias
            title: 'Primeiros Dias do Puerpério: Guia Completo de Cuidados',
            description: 'Orientações essenciais sobre recuperação física, cuidados com a episiotomia/cesárea, higiene, alimentação e descanso nos primeiros dias após o parto.',
            embeddingAllowed: false, // TODO: Verificar após encontrar vídeo real
            channel: 'A definir'
        },
        {
            id: 'VIDEO_ID_2', // TODO: Substituir por ID real - Amamentação
            title: 'Amamentação nos Primeiros Dias: Dicas Práticas e Acolhimento',
            description: 'Dicas práticas sobre posicionamento correto, pega adequada, sinais de fome e cuidados com as mamas para uma amamentação bem-sucedida.',
            embeddingAllowed: false, // TODO: Verificar após encontrar vídeo real
            channel: 'A definir'
        },
        {
            id: 'VIDEO_ID_3', // TODO: Substituir por ID real - Saúde Mental
            title: 'Saúde Mental Materna: Entendendo o Baby Blues e Cuidando de Você',
            description: 'Entenda a diferença entre baby blues e depressão pós-parto, reconheça sinais de alerta e aprenda estratégias de autocuidado emocional.',
            embeddingAllowed: false, // TODO: Verificar após encontrar vídeo real
            channel: 'A definir'
        },
        {
            id: 'VIDEO_ID_4', // TODO: Substituir por ID real - Rede de Apoio
            title: 'Rede de Apoio no Puerpério: Você Não Precisa Fazer Tudo Sozinha',
            description: 'Aprenda a construir sua rede de apoio, pedir ajuda sem culpa e entender que cuidar de si mesma é essencial para cuidar do bebê.',
            embeddingAllowed: false, // TODO: Verificar após encontrar vídeo real
            channel: 'A definir'
        }
    ];

    /**
     * Obtém uma dica aleatória baseada na data do dia
     * (garante que a mesma dica seja exibida durante o dia)
     */
    function getDailyTip() {
        const today = new Date();
        const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
        const tipIndex = dayOfYear % tips.length;
        return tips[tipIndex];
    }

    /**
     * Obtém uma afirmação aleatória
     */
    function getRandomAffirmation() {
        const randomIndex = Math.floor(Math.random() * affirmations.length);
        return affirmations[randomIndex];
    }

    /**
     * Gera URL da thumbnail do YouTube
     */
    function getYouTubeThumbnail(videoId) {
        if (!videoId || videoId.startsWith('VIDEO_ID')) {
            // Placeholder enquanto não temos IDs reais
            return 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180" viewBox="0 0 320 180"><rect width="320" height="180" fill="%23ff8fa3"/><text x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="white" font-family="Arial" font-size="16">Vídeo em breve</text></svg>';
        }
        return `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
    }

    /**
     * Gera URL de embed do YouTube (usando youtube-nocookie.com para privacidade)
     */
    function getYouTubeEmbedUrl(videoId) {
        if (!videoId || videoId.startsWith('VIDEO_ID')) {
            return null;
        }
        // Usa youtube-nocookie.com para privacidade aprimorada (não armazena cookies até interação)
        return `https://www.youtube-nocookie.com/embed/${videoId}?rel=0&modestbranding=1`;
    }

    /**
     * Inicializa Dica do Dia
     */
    function initTipOfTheDay() {
        const tipCard = document.getElementById('tip-of-the-day-card');
        const tipText = document.getElementById('tip-text');
        
        if (!tipCard || !tipText) return;

        const tip = getDailyTip();
        tipText.textContent = tip.text;
        
        // Atualiza ícone se necessário
        const cardIcon = tipCard.querySelector('.card-icon');
        if (cardIcon) {
            cardIcon.textContent = tip.icon;
        }
    }

    /**
     * Inicializa Afirmação Positiva
     */
    function initAffirmation() {
        const affirmationCard = document.getElementById('affirmation-card');
        const affirmationText = document.getElementById('affirmation-text');
        
        if (!affirmationCard || !affirmationText) return;

        const affirmation = getRandomAffirmation();
        affirmationText.textContent = affirmation;
    }

    /**
     * Renderiza lista de vídeos
     */
    function renderVideos() {
        const videosList = document.getElementById('videos-list');
        if (!videosList) return;

        videosList.innerHTML = '';

        videos.forEach((video, index) => {
            const videoItem = document.createElement('div');
            videoItem.className = 'video-item';
            videoItem.setAttribute('data-video-index', index);
            videoItem.setAttribute('role', 'button');
            videoItem.setAttribute('tabindex', '0');
            videoItem.setAttribute('aria-label', `Assistir: ${video.title}`);

            const thumbnail = document.createElement('div');
            thumbnail.className = 'video-thumbnail';
            
            const img = document.createElement('img');
            img.src = getYouTubeThumbnail(video.id);
            img.alt = video.title;
            img.loading = 'lazy';
            thumbnail.appendChild(img);

            const info = document.createElement('div');
            info.className = 'video-info';
            
            const title = document.createElement('h4');
            title.className = 'video-title';
            title.textContent = video.title;
            
            const description = document.createElement('p');
            description.className = 'video-description';
            description.textContent = video.description;

            info.appendChild(title);
            info.appendChild(description);

            videoItem.appendChild(thumbnail);
            videoItem.appendChild(info);

            // Event listeners
            videoItem.addEventListener('click', () => openVideoModal(video));
            videoItem.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    openVideoModal(video);
                }
            });

            videosList.appendChild(videoItem);
        });
    }

    /**
     * Abre modal de vídeo
     */
    function openVideoModal(video) {
        const modal = document.getElementById('video-modal');
        const player = document.getElementById('video-modal-player');
        const title = document.getElementById('video-modal-title');
        const description = document.getElementById('video-modal-description');
        const embedUrl = getYouTubeEmbedUrl(video.id);

        if (!modal || !player || !title || !description) return;

        if (!embedUrl || video.id.startsWith('VIDEO_ID')) {
            // Usa toast notification se disponível, senão usa alert
            if (window.toast && typeof window.toast.warning === 'function') {
                window.toast.warning('Vídeo ainda não disponível. Os IDs dos vídeos estão sendo configurados.', 5000);
            } else {
                alert('Vídeo ainda não disponível. Os IDs dos vídeos estão sendo configurados. Por favor, consulte a equipe técnica.');
            }
            console.warn('[SidebarContent] Vídeo não configurado:', video.id);
            return;
        }

        // Atualiza informações
        title.textContent = video.title;
        description.textContent = video.description;

        // Cria iframe com tratamento de erro
        const iframe = document.createElement('iframe');
        iframe.src = embedUrl;
        iframe.setAttribute('frameborder', '0');
        iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
        iframe.setAttribute('allowfullscreen', '');
        
        // Adiciona listener de erro para o iframe
        iframe.addEventListener('error', () => {
            if (window.toast && typeof window.toast.error === 'function') {
                window.toast.error('Erro ao carregar vídeo. Verifique sua conexão ou tente novamente.', 5000);
            }
        });

        // Monitora carregamento do iframe
        iframe.addEventListener('load', () => {
            // Se iframe carregou com sucesso, não faz nada
            console.log('[SidebarContent] Vídeo carregado com sucesso');
        });

        // Timeout: se vídeo não carregar em 10 segundos, mostra erro
        const loadTimeout = setTimeout(() => {
            if (iframe.contentDocument === null || iframe.contentWindow === null) {
                // Se ainda não carregou, pode ser erro de rede ou permissão
                if (window.toast && typeof window.toast.error === 'function') {
                    window.toast.error('Vídeo demorou para carregar. Verifique sua conexão.', 5000);
                }
            }
        }, 10000);

        // Limpa timeout quando iframe carregar
        iframe.addEventListener('load', () => {
            clearTimeout(loadTimeout);
        }, { once: true });

        // Insere player
        player.innerHTML = '';
        player.appendChild(iframe);

        // Mostra modal
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Foca no modal para acessibilidade
        const closeBtn = document.getElementById('video-modal-close');
        if (closeBtn) {
            setTimeout(() => closeBtn.focus(), 100);
        }
    }

    /**
     * Fecha modal de vídeo
     */
    function closeVideoModal() {
        const modal = document.getElementById('video-modal');
        const player = document.getElementById('video-modal-player');

        if (!modal) return;

        // Salva posição de scroll antes de fechar (para restaurar após)
        const scrollPosition = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
        const dicasContainer = document.getElementById('mobile-dicas-container');
        const dicasScrollPosition = dicasContainer ? dicasContainer.scrollTop : 0;

        // Para o vídeo imediatamente limpando o src do iframe
        if (player) {
            const iframe = player.querySelector('iframe');
            if (iframe) {
                // Remove o src para parar o áudio/vídeo imediatamente
                iframe.src = '';
                iframe.src = 'about:blank'; // Garante que o iframe está vazio
            }
            // Limpa o conteúdo do player
            player.innerHTML = '';
        }

        modal.style.display = 'none';
        document.body.style.overflow = '';

        // Restaura posição de scroll após um pequeno delay (permite que DOM atualize)
        setTimeout(() => {
            // Se estamos em mobile e na aba Dicas, restaura scroll do container
            if (window.innerWidth <= 1023 && dicasContainer && dicasContainer.style.display !== 'none') {
                dicasContainer.scrollTop = dicasScrollPosition;
            } else {
                // Caso contrário, restaura scroll da página
                window.scrollTo({
                    top: scrollPosition,
                    behavior: 'auto' // Instantâneo, não animado
                });
            }
        }, 100);
    }

    /**
     * Inicializa event listeners do modal
     */
    function initVideoModal() {
        const modal = document.getElementById('video-modal');
        const overlay = document.getElementById('video-modal-overlay');
        const closeBtn = document.getElementById('video-modal-close');

        if (!modal) return;

        // Fecha ao clicar no overlay
        if (overlay) {
            overlay.addEventListener('click', closeVideoModal);
        }

        // Fecha ao clicar no botão de fechar
        if (closeBtn) {
            closeBtn.addEventListener('click', closeVideoModal);
        }

        // Fecha com ESC (listener único para todo o documento)
        function handleEscapeKey(e) {
            const modal = document.getElementById('video-modal');
            if (e.key === 'Escape' && modal && modal.style.display === 'flex') {
                closeVideoModal();
            }
        }
        
        // Remove listener anterior se existir (evita duplicação)
        document.removeEventListener('keydown', handleEscapeKey);
        document.addEventListener('keydown', handleEscapeKey);
    }

    /**
     * Inicializa tudo quando DOM estiver pronto
     */
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Só inicializa se estiver em desktop (≥1024px)
        if (window.innerWidth >= 1024) {
            initTipOfTheDay();
            initAffirmation();
            renderVideos();
            initVideoModal();
        }

        // Re-inicializa se redimensionar para desktop
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (window.innerWidth >= 1024) {
                    initTipOfTheDay();
                    initAffirmation();
                    renderVideos();
                }
            }, 250);
        });
    }

    // Exporta funções para uso externo (se necessário)
    window.sidebarContent = {
        updateVideos: function(newVideos) {
            if (Array.isArray(newVideos) && newVideos.length > 0) {
                videos.splice(0, videos.length, ...newVideos);
                renderVideos();
            }
        },
        refreshAffirmation: initAffirmation,
        refreshTip: initTipOfTheDay
    };

    // Inicializa
    init();

})();
