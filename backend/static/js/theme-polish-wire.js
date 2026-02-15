// -*- coding: utf-8 -*-
// Injeta o CSS de polimento visual e aplica classes em alguns botões comuns.
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

  function upgradeButtons() {
    var selectors = [
      '.btn-primary', '.btn-secondary', '.btn-soft',
      '.btn', 'a.button', 'button.primary', '[data-role="btn"]',
      '.conteudo-card-cta'
    ];
    var seen = new Set();
    selectors.forEach(function (sel) {
      try {
        document.querySelectorAll(sel).forEach(function (el) {
          if (seen.has(el)) return;
          seen.add(el);
          if (!el.classList.contains('btn')) {
            el.classList.add('btn');
          }
          var t = (el.innerText || '').toLowerCase();
          if (!el.classList.contains('btn-primary') &&
              (t.indexOf('começar') !== -1 || t.indexOf('entrar') !== -1 || t.indexOf('confirmar') !== -1 || t.indexOf('enviar') !== -1)) {
            el.classList.add('btn-primary');
          }
        });
      } catch (_) {}
    });
  }

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  ready(function () {
    // fontes primeiro (swap), depois tema e a11y (ordem correta, sem repetição)
    injectCSS('/static/css/fonts.css');
    injectCSS('/static/css/theme-polish.css');
    injectCSS('/static/css/a11y-polish.css');
    upgradeButtons();
    try {
      var mo = new MutationObserver(function (muts) {
        for (var i = 0; i < muts.length; i++) {
          var m = muts[i];
          if (m.addedNodes && m.addedNodes.length) {
            upgradeButtons();
            break;
          }
        }
      });
      mo.observe(document.documentElement, { childList: true, subtree: true });
    } catch (_) {}
  });
})();
