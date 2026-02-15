// -*- coding: utf-8 -*-
// Skeleton para a seção "Perto de você" (geolocalização).
// Trabalha em cima do container criado pelo nearby-wire.js.
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

  function findNearbyList() {
    return document.querySelector('[data-nearby-results] .nearby-list') ||
      document.querySelector('.nearby-section .nearby-list') ||
      document.querySelector('.nearby-list');
  }

  function startNearbySkeleton(list) {
    if (!list || list.__skNearbyOn) return;
    list.__skNearbyOn = true;
    list.__skNearbyStart = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    list.classList.add('is-loading');
    var wrap = document.createElement('div');
    wrap.className = 'skeleton-nearby';
    var count = 4;
    for (var i = 0; i < count; i++) {
      var c = document.createElement('div');
      c.className = 'skeleton-hosp-card';
      var t = document.createElement('div');
      t.className = 'skeleton-hosp-title skeleton-shimmer';
      var s = document.createElement('div');
      s.className = 'skeleton-hosp-sub skeleton-shimmer';
      var badges = document.createElement('div');
      badges.className = 'skeleton-hosp-badges';
      var b1 = document.createElement('div');
      b1.className = 'skeleton-hosp-badge skeleton-shimmer';
      var b2 = document.createElement('div');
      b2.className = 'skeleton-hosp-badge skeleton-shimmer';
      var b3 = document.createElement('div');
      b3.className = 'skeleton-hosp-badge skeleton-shimmer';
      badges.appendChild(b1);
      badges.appendChild(b2);
      badges.appendChild(b3);
      var ln = document.createElement('div');
      ln.className = 'skeleton-hosp-line skeleton-shimmer';
      c.appendChild(t);
      c.appendChild(s);
      c.appendChild(badges);
      c.appendChild(ln);
      wrap.appendChild(c);
    }
    list.appendChild(wrap);
  }

  function clearNearbySkeleton(list) {
    if (!list || !list.__skNearbyOn) return;
    var minMs = Number(list && list.dataset && list.dataset.skeletonMin) || DEFAULT_MIN_MS;
    var now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    var start = list.__skNearbyStart || now;
    var elapsed = now - start;
    var doClear = function () {
      var wrap = list.querySelector('.skeleton-nearby');
      if (wrap) wrap.remove();
      list.classList.remove('is-loading');
      list.__skNearbyOn = false;
    };
    if (elapsed < minMs) {
      setTimeout(doClear, minMs - elapsed);
    } else {
      doClear();
    }
  }

  function watchNearby(list) {
    try {
      var mo = new MutationObserver(function () {
        if (list.querySelector('.hospital-card')) {
          clearNearbySkeleton(list);
          mo.disconnect();
        }
      });
      mo.observe(list, { childList: true, subtree: true });
      setTimeout(function () { clearNearbySkeleton(list); }, 4000);
    } catch (_) {}
  }

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    injectCSS('/static/css/skeleton.css');
    var list = findNearbyList();
    if (!list) {
      try {
        var mo = new MutationObserver(function () {
          var l = findNearbyList();
          if (l) {
            startNearbySkeleton(l);
            watchNearby(l);
            mo.disconnect();
          }
        });
        mo.observe(document.documentElement, { childList: true, subtree: true });
      } catch (_) {}
      return;
    }
    startNearbySkeleton(list);
    watchNearby(list);
  });
})();
