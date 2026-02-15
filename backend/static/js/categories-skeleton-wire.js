// -*- coding: utf-8 -*-
// Skeleton para a seção de categorias (Guias / Gestação / Pós‑Parto / Vacinação).
// Não altera o HTML: injeta shimmer enquanto os cards não estiverem prontos.
(function () {
  'use strict';

  var DEFAULT_MIN_MS = 700;

  function injectCSS(href) {
    try {
      var l = document.createElement('link');
      l.rel = 'stylesheet';
      l.href = href;
      document.head.appendChild(l);
    } catch (_) {}
  }

  function startCatsSkeleton(grid) {
    if (!grid || grid.__skCatsOn) return;
    grid.__skCatsOn = true;
    grid.__skCatsStart = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    grid.classList.add('is-loading');
    var wrap = document.createElement('div');
    wrap.className = 'skeleton-cats';
    var count = Math.max(4, Math.min(8, grid.children.length || 4));
    for (var i = 0; i < count; i++) {
      var card = document.createElement('div');
      card.className = 'skeleton-cat-card';
      var blk = document.createElement('div');
      blk.className = 'sk-block skeleton-shimmer';
      card.appendChild(blk);
      wrap.appendChild(card);
    }
    grid.prepend(wrap);
  }

  function clearCatsSkeleton(grid) {
    if (!grid || !grid.__skCatsOn) return;
    var minMs = Number(grid && grid.dataset && grid.dataset.skeletonMin) || DEFAULT_MIN_MS;
    var now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    var start = grid.__skCatsStart || now;
    var elapsed = now - start;
    var doClear = function () {
      var wrap = grid.querySelector('.skeleton-cats');
      if (wrap) wrap.remove();
      grid.classList.remove('is-loading');
      grid.__skCatsOn = false;
    };
    if (elapsed < minMs) {
      setTimeout(doClear, minMs - elapsed);
    } else {
      doClear();
    }
  }

  function findGrid() {
    return document.querySelector('.categories-grid');
  }

  function watchForCards(grid) {
    try {
      var mo = new MutationObserver(function () {
        var visibleCard = Array.from(grid.querySelectorAll('.category-card')).find(function (el) {
          return el.offsetParent !== null && getComputedStyle(el).display !== 'none';
        });
        if (visibleCard) {
          clearCatsSkeleton(grid);
          mo.disconnect();
        }
      });
      mo.observe(grid, { childList: true, subtree: true });
      setTimeout(function () { clearCatsSkeleton(grid); }, 2500);
    } catch (_) {}
  }

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    injectCSS('/static/css/skeleton.css');
    var grid = findGrid();
    if (!grid) {
      try {
        var mo = new MutationObserver(function () {
          var g = findGrid();
          if (g) {
            startCatsSkeleton(g);
            watchForCards(g);
            mo.disconnect();
          }
        });
        mo.observe(document.documentElement, { childList: true, subtree: true });
      } catch (_) {}
      return;
    }
    if (!grid.querySelector('.category-card')) {
      startCatsSkeleton(grid);
      watchForCards(grid);
    }
  });
})();
