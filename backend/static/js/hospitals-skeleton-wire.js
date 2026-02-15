// -*- coding: utf-8 -*-
// Skeleton para a lista geral de hospitais (não "Perto de você").
// Reutiliza o CSS do 0025 (skeleton.css – classes skeleton-hosp-* e skeleton-nearby).
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

  function findHospitalsList() {
    return document.querySelector('[data-hospitals-list]') ||
      document.getElementById('results') ||
      document.querySelector('.results') ||
      document.querySelector('.hospital-list') ||
      document.querySelector('.hospitals-list');
  }

  function startHospSkeleton(list) {
    if (!list || list.__skHospOn) return;
    list.__skHospOn = true;
    list.__skHospStart = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    var wrap = document.createElement('div');
    wrap.className = 'skeleton-nearby';
    var count = Math.max(4, Math.min(8, (list.children && list.children.length) || 6));
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
    list.prepend(wrap);
  }

  function clearHospSkeleton(list) {
    if (!list || !list.__skHospOn) return;
    var minMs = Number(list && list.dataset && list.dataset.skeletonMin) || DEFAULT_MIN_MS;
    var now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    var start = list.__skHospStart || now;
    var elapsed = now - start;
    var doClear = function () {
      var wrap = list.querySelector('.skeleton-nearby');
      if (wrap) wrap.remove();
      list.__skHospOn = false;
    };
    if (elapsed < minMs) {
      setTimeout(doClear, minMs - elapsed);
    } else {
      doClear();
    }
  }

  function watchHospitals(list) {
    try {
      var mo = new MutationObserver(function () {
        if (list.querySelector('.hospital-card')) {
          clearHospSkeleton(list);
          mo.disconnect();
        }
      });
      mo.observe(list, { childList: true, subtree: true });
      setTimeout(function () { clearHospSkeleton(list); }, 5000);
    } catch (_) {}
  }

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    injectCSS('/static/css/skeleton.css');
    var list = findHospitalsList();
    if (!list) {
      try {
        var mo = new MutationObserver(function () {
          var l = findHospitalsList();
          if (l) {
            startHospSkeleton(l);
            watchHospitals(l);
            mo.disconnect();
          }
        });
        mo.observe(document.documentElement, { childList: true, subtree: true });
      } catch (_) {}
      return;
    }
    startHospSkeleton(list);
    watchHospitals(list);
  });
})();
