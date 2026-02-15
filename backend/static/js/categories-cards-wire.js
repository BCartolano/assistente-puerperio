// -*- coding: utf-8 -*-
// Polimento dos cards de categorias da home:
// - aplica grid responsivo no container
// - aplica classe visual nos 4 cards (Guias Práticos, Gestação, Pós‑Parto, Vacinação)
// - não altera seu HTML; usa heurísticas pelos textos dos cards
(function () {
  'use strict';

  function injectCSS(href) {
    try {
      var link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      document.head.appendChild(link);
    } catch (_) {}
  }

  function normText(s) {
    return (s || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
  }

  var LABELS = [
    'guias praticos',
    'gestacao',
    'pos-parto',
    'pos parto',
    'vacinacao'
  ];

  function looksLikeCategory(el) {
    var t = normText(el.textContent || '');
    return LABELS.some(function (l) { return t.indexOf(l) !== -1; });
  }

  function findSection() {
    var candidates = Array.from(document.querySelectorAll('section, .section, .home-categories, .categories, .cards, .grid, #categories'));
    for (var i = 0; i < candidates.length; i++) {
      var c = candidates[i];
      var hits = 0;
      c.querySelectorAll('*').forEach(function (n) {
        if (n.children && n.children.length > 6) return;
        if (looksLikeCategory(n)) hits++;
      });
      if (hits >= 3) return c;
    }
    return null;
  }

  function wire() {
    injectCSS('/static/css/categories-cards.css');
    var section = findSection();
    if (!section) return;
    section.classList.add('categories-grid');
    var items = Array.from(section.children);
    if (items.length === 0) {
      items = Array.from(section.querySelectorAll(':scope > * > *'));
    }
    items.forEach(function (el) {
      if (!looksLikeCategory(el)) return;
      el.classList.add('category-card');
      var h = el.querySelector('h3, h4, strong, span');
      if (h && looksLikeCategory(h)) {
        h.classList.add('category-title');
      } else {
        var txt = (el.textContent || '').trim();
        if (txt && normText(txt).length < 40) {
          var wrap = document.createElement('span');
          wrap.className = 'category-title';
          wrap.textContent = txt;
          el.innerHTML = '';
          el.appendChild(wrap);
        }
      }
    });

    try {
      Array.from(section.querySelectorAll('.category-card')).forEach(function (card) {
        var link = card.querySelector('a[href]');
        if (!link) return;
        link.style.display = 'inline-flex';
        link.style.width = '100%';
        link.style.height = '100%';
        var label = (link.textContent || card.textContent || 'Abrir categoria').trim();
        card.setAttribute('role', 'link');
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', label);
        card.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            try { link.click(); } catch (_) { window.location.assign(link.href); }
          }
        });
      });
    } catch (_) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }
})();
