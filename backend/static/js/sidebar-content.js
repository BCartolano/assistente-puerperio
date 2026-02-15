/**
 * Sidebar Content Manager
 * Gerencia conteúdo das sidebars: Orientação, Afirmações e Vídeos
 */

(function() {
    'use strict';

    let orientacoes = [];
    let afirmacoes = [];

    async function loadOrientacoes() {
        try {
            const r = await fetch('/static/data/orientacoes.json');
            if (r.ok) {
                const data = await r.json();
                orientacoes = data.items || [];
            }
        } catch (e) {
            console.warn('[SidebarContent] Erro ao carregar orientacoes.json:', e);
        }
        if (orientacoes.length === 0) {
            orientacoes = ['Manter hidratação adequada ajuda na recuperação pós-parto.', 'O descanso fragmentado é normal, aproveite os cochilos do bebê.'];
        }
        return orientacoes;
    }

    async function loadAfirmacoes() {
        try {
            const r = await fetch('/static/data/afirmacoes.json');
            if (r.ok) {
                const data = await r.json();
                afirmacoes = data.items || [];
            }
        } catch (e) {
            console.warn('[SidebarContent] Erro ao carregar afirmacoes.json:', e);
        }
        if (afirmacoes.length === 0) {
            afirmacoes = ['Você é luz, confie no universo.', 'O amor de mãe é capaz de me dar força para superar qualquer dificuldade.'];
        }
        return afirmacoes;
    }

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

    function getRandomOrientacao() {
        if (orientacoes.length === 0) return 'Manter hidratação adequada ajuda na recuperação pós-parto.';
        return orientacoes[Math.floor(Math.random() * orientacoes.length)];
    }

    function getRandomAffirmation() {
        if (afirmacoes.length === 0) return 'Você é luz, confie no universo.';
        return afirmacoes[Math.floor(Math.random() * afirmacoes.length)];
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
     * Inicializa card Orientação (sorteia frase no carregamento e no clique)
     */
    function initOrientacao() {
        const card = document.getElementById('orientacao-card');
        const textEl = document.getElementById('orientacao-text');
        if (!card || !textEl) return;
        function refresh() {
            textEl.textContent = getRandomOrientacao();
        }
        refresh();
        card.addEventListener('click', refresh);
        card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); refresh(); } });
    }

    /**
     * Inicializa card Afirmação (sorteia frase no carregamento e no clique)
     */
    function initAffirmation() {
        const card = document.getElementById('affirmation-card');
        const textEl = document.getElementById('affirmation-text');
        if (!card || !textEl) return;
        function refresh() {
            textEl.textContent = getRandomAffirmation();
        }
        refresh();
        card.addEventListener('click', refresh);
        card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); refresh(); } });
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
    async function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => init());
            return;
        }
        await Promise.all([loadOrientacoes(), loadAfirmacoes()]);
        if (window.innerWidth >= 1024) {
            initOrientacao();
            initAffirmation();
            renderVideos();
            initVideoModal();
        } else {
            initOrientacao();
            initAffirmation();
        }
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (window.innerWidth >= 1024) {
                    initOrientacao();
                    initAffirmation();
                    renderVideos();
                }
            }, 250);
        });
    }

    window.sidebarContent = {
        updateVideos: function(newVideos) {
            if (Array.isArray(newVideos) && newVideos.length > 0) {
                videos.splice(0, videos.length, ...newVideos);
                renderVideos();
            }
        },
        refreshAffirmation: initAffirmation,
        refreshOrientacao: initOrientacao
    };

    // Inicializa
    init();

})();
