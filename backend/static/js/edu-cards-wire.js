// -*- coding: utf-8 -*-
// Liga os cards "Câncer de Mama" e "Doação de Leite" aos links oficiais,
// injeta CSS de layout e desenha ícones SVG (fita rosa e duas mamadeiras).
// Badge "Leitura X min" e link "Ver todos" ao lado do título.
(function () {
  'use strict';

  var OFFICIAL_IDS = new Set(['card-cancer-mama-welcome', 'card-doacao-leite-welcome', 'card-aleitamento']);
  var __eduSkStart = 0;
  var EDU_MIN_SKELETON_MS = 600;
  var __eduWired = false; // Flag para evitar execução múltipla

  function injectCSS(href) {
    try {
      var link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      document.head.appendChild(link);
    } catch (_) {}
  }

  function addSkeleton(card) {
    if (!card || card.classList.contains('is-loading')) return;
    card.classList.add('is-loading');
    card.setAttribute('aria-busy', 'true');
    var w = document.createElement('div');
    w.className = 'skeleton-wrap';
    ['figure', 'title', 'subtitle', 'badge', 'button'].forEach(function (kind) {
      var d = document.createElement('div');
      d.className = 'skeleton-' + kind + ' skeleton-shimmer';
      w.appendChild(d);
    });
    card.appendChild(w);
  }

  function removeSkeleton(card) {
    if (!card || !card.classList.contains('is-loading')) return;
    var w = card.querySelector('.skeleton-wrap');
    if (w) w.remove();
    card.classList.remove('is-loading');
    card.removeAttribute('aria-busy');
  }

  function startSkeleton() {
    __eduSkStart = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    document.querySelectorAll('.conteudo-card-carousel').forEach(addSkeleton);
  }

  function clearSkeleton() {
    var now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    var elapsed = now - (__eduSkStart || 0);
    var delay = Math.max(0, EDU_MIN_SKELETON_MS - elapsed);
    setTimeout(function () {
      document.querySelectorAll('.conteudo-card-carousel.is-loading').forEach(removeSkeleton);
    }, delay);
  }

  function _norm(s) {
    return (s || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
  }

  function setTitles(it, card) {
    try {
      var t = card.querySelector('.conteudo-card-title');
      var s = card.querySelector('.conteudo-card-subtitle');
      if (it.id === 'card-cancer-mama-welcome') { if (t) t.textContent = 'Câncer de Mama'; if (s) s.textContent = ''; }
      if (it.id === 'card-doacao-leite-welcome') { if (t) t.textContent = 'Doação de Leite'; if (s) s.textContent = ''; }
      if (it.id === 'card-aleitamento') { if (t) t.textContent = 'Amamentação'; if (s) s.textContent = 'Aleitamento materno'; }
    } catch (_) {}
  }

  /* 0102: pré-carrega imagens para evitar "pulo" */
  function preloadEduImages(srcs) {
    try {
      (srcs || []).forEach(function (src) {
        if (src) {
          var im = new Image();
          im.src = src;
        }
      });
    } catch (_) {}
  }

  /* Sem card clicável — só o botão leva ao site */

  var IMG_MAP = {
    'card-cancer-mama-welcome': '/static/img/edu/cancer-mama.png',
    'card-doacao-leite-welcome': '/static/img/edu/doacao-leite-materno.png',
    'card-aleitamento': '/static/img/edu/aleitamento.png'
  };

  function candidatesFor(it) {
    var id = it.id || '';
    var cand = [];
    var exts = ['png', 'jpg', 'jpeg', 'webp'];
    function pushSet(arr) {
      exts.forEach(function (ext) {
        arr.forEach(function (base) { cand.push(base + '.' + ext); });
      });
    }
    if (id && IMG_MAP[id]) cand.push(IMG_MAP[id]);
    if (id === 'card-cancer-mama-welcome') {
      pushSet(['/static/img/edu/cancer-mama', '/static/img/edu/Câncer de Mama', '/static/img/edu/Cancer de Mama']);
    } else if (id === 'card-doacao-leite-welcome') {
      pushSet(['/static/img/edu/doacao-leite-materno', '/static/img/edu/doacao-de-leite', '/static/img/edu/Doação de Leite Materno', '/static/img/edu/Doacao de Leite Materno']);
    } else if (id === 'card-aleitamento') {
      pushSet(['/static/img/edu/aleitamento', '/static/img/edu/aleitamento-materno', '/static/img/edu/Aleitamento Materno', '/static/img/edu/Amamentação', '/static/img/edu/breastfeeding']);
    }
    if (it.image) cand.unshift(it.image);
    return cand.filter(Boolean);
  }

  function loadFirstAvailable(fig, cand) {
    if (!fig || !cand || !cand.length || fig.getAttribute('data-edu-processed') === 'true') {
      return;
    }
    
    // Verifica se já existe uma imagem válida
    var existingImg = fig.querySelector('img.edu-img');
    if (existingImg && existingImg.src && 
        existingImg.src.trim() !== '' &&
        !existingImg.src.includes('data:image/svg') &&
        !existingImg.src.includes('placeholder') &&
        existingImg.src !== window.location.href) {
      fig.setAttribute('data-edu-processed', 'true');
      return; // Não substitui imagem válida existente
    }
    
    // Tenta carregar primeira imagem disponível
    var img = new Image();
    var i = 0;
    var maxAttempts = cand.length;
    
    function tryNext() {
      if (i >= maxAttempts || fig.getAttribute('data-edu-processed') === 'true') {
        fig.setAttribute('data-edu-processed', 'true');
        return;
      }
      img.src = cand[i++];
    }
    
    img.onload = function () {
      if (fig.getAttribute('data-edu-processed') === 'true') return;
      var currentImg = fig.querySelector('img.edu-img');
      // Só substitui se não há imagem válida
      if (!currentImg || !currentImg.src || 
          currentImg.src.includes('data:image/svg') || 
          currentImg.src.includes('placeholder')) {
        fig.innerHTML = '<img class="edu-img" src="' + img.src + '" alt="" loading="lazy">';
      }
      fig.setAttribute('data-edu-processed', 'true');
    };
    
    img.onerror = tryNext;
    tryNext();
  }

  async function fetchJSON(url) {
    try {
      var res = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } });
      if (!res.ok) return null;
      return await res.json();
    } catch (_) { return null; }
  }

  function _addReadBadge(card, mins) {
    if (!card || !mins) return;
    try {
      var meta = card.querySelector('.edu-meta');
      if (!meta) {
        meta = document.createElement('div');
        meta.className = 'edu-meta';
      }
      var cta = card.querySelector('.conteudo-card-cta');
      if (cta && cta.parentNode) {
        cta.parentNode.insertBefore(meta, cta);
      } else {
        card.appendChild(meta);
      }
      var badge = meta.querySelector('.badge-read');
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'badge-read';
        meta.appendChild(badge);
      }
      badge.textContent = 'Leitura ' + mins + ' min';
    } catch (_) {}
  }

  var RibbonSVG =
    '<svg viewBox="0 0 64 64" class="edu-icon edu-icon--ribbon" aria-hidden="true">' +
    '<path d="M32 6c-10 0-18 8-18 18 0 12 18 28 18 28s18-16 18-28c0-10-8-18-18-18z" fill="none" stroke="#ff7ab8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>' +
    '<path d="M32 30 L18 56" stroke="#ff7ab8" stroke-width="4" stroke-linecap="round"/>' +
    '<path d="M32 30 L46 56" stroke="#ff7ab8" stroke-width="4" stroke-linecap="round"/>' +
    '</svg>';

  var BottlesSVG =
    '<svg viewBox="0 0 96 64" class="edu-icon edu-icon--bottles" aria-hidden="true">' +
    '<g fill="none" stroke="#6aa8ff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">' +
    '<rect x="12" y="20" width="24" height="36" rx="6"/>' +
    '<rect x="60" y="14" width="24" height="42" rx="6"/>' +
    '<rect x="16" y="12" width="16" height="8" rx="3"/>' +
    '<rect x="64" y="8" width="16" height="8" rx="3"/>' +
    '</g>' +
    '<g fill="#d8ebff">' +
    '<rect x="12" y="38" width="24" height="18" rx="6"/>' +
    '<rect x="60" y="34" width="24" height="22" rx="6"/>' +
    '</g>' +
    '</svg>';

  function setFigureByIcon(figEl, icon) {
    if (!figEl) return;
    figEl.innerHTML = (icon === 'bottles') ? BottlesSVG : RibbonSVG;
  }

  /* Compatível com lista vertical: usa .conteudos-carousel-track ou .conteudos-carousel (display: block no container não quebra) */
  function _createCard(id) {
    var track = document.querySelector('.conteudos-carousel-track') || document.querySelector('.conteudos-carousel');
    if (!track) return null;
    var card = document.createElement('div');
    card.id = id;
    card.className = 'conteudo-card-carousel';
    card.innerHTML = [
      '<div class="conteudo-card-figure"></div>',
      '<div class="conteudo-card-title"></div>',
      '<div class="conteudo-card-subtitle"></div>',
      '<div class="edu-meta"></div>',
      '<a class="conteudo-card-cta btn-soft" target="_blank" rel="noopener">Ministério da Saúde</a>'
    ].join('');
    track.appendChild(card);
    return card;
  }

  function wire() {
    // Evita execução múltipla - CRÍTICO para evitar loops
    if (__eduWired) {
      return;
    }
    __eduWired = true;
    
    injectCSS('/static/css/educational-cards.css');
    injectCSS('/static/css/skeleton.css');
    try {
      preloadEduImages(['/static/img/edu/cancer-mama.png', '/static/img/edu/doacao-leite-materno.png', '/static/img/edu/aleitamento.png']);
    } catch (_) {}
    document.querySelectorAll('.conteudo-card-carousel[id]').forEach(function (c) {
      if (c.id && !OFFICIAL_IDS.has(c.id)) c.remove();
    });
    startSkeleton();

    // Processa cards de forma síncrona para evitar loops
    OFFICIAL_IDS.forEach(function (cardId) {
      var card = document.getElementById(cardId);
      if (!card) return;
      
      var fig = card.querySelector('.conteudo-card-figure');
      if (fig && !fig.getAttribute('data-edu-processed')) {
        var existingImg = fig.querySelector('img.edu-img');
        // Se já existe imagem válida no HTML, apenas marca como processada
        if (existingImg && existingImg.src && 
            existingImg.src.trim() !== '' &&
            !existingImg.src.includes('data:image/svg') &&
            !existingImg.src.includes('placeholder') &&
            existingImg.src !== window.location.href) {
          fig.setAttribute('data-edu-processed', 'true');
        } else {
          // Só tenta carregar se não há imagem válida
          var cand = candidatesFor({ id: cardId });
          if (cand.length) {
            loadFirstAvailable(fig, cand);
          } else {
            if (cardId.indexOf('cancer') !== -1) setFigureByIcon(fig, 'ribbon');
            else if (cardId.indexOf('doacao') !== -1) setFigureByIcon(fig, 'bottles');
            else setFigureByIcon(fig, 'bottles');
          }
          fig.setAttribute('data-edu-processed', 'true');
        }
      }
    });
    
    clearSkeleton();
    
    // Tenta buscar dados do JSON apenas uma vez (deduped: evita duplicata em 2s com perf-prefetch)
    var fetchEdu = (window.dedupedFetchJSON && window.dedupedFetchJSON('/api/educational', { credentials: 'same-origin' })) || fetchJSON('/api/educational');
    fetchEdu.then(function(data) {
      if (data && Array.isArray(data.items)) {
        data.items.forEach(function (it) {
          if (!OFFICIAL_IDS.has(it.id)) return;
          var card = document.getElementById(it.id);
          if (!card) return;
          
          // Atualiza apenas textos e links, não mexe nas imagens já processadas
          var t = card.querySelector('.conteudo-card-title');
          if (t && it.title) t.textContent = it.title;
          var s = card.querySelector('.conteudo-card-subtitle');
          if (s && it.subtitle) s.textContent = it.subtitle;
          setTitles(it, card);
          
          var url = it.url;
          var cta = card.querySelector('.conteudo-card-cta');
          if (cta && url) {
            cta.href = url;
            if (!cta.onclick) {
              cta.onclick = function (e) { 
                e.preventDefault(); 
                e.stopPropagation(); 
                window.open(url, '_blank', 'noopener'); 
              };
            }
          }
        });
      }
    }).catch(function() {
      // Ignora erros silenciosamente
    });
  }

  // Executa apenas uma vez quando o DOM estiver pronto
  if (!__eduWired) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        if (!__eduWired) wire();
      }, { once: true });
    } else {
      // Se já está carregado, executa imediatamente
      wire();
    }
  }
})();
