// -*- coding: utf-8 -*-
// Desliga skeletons em DEV: use ?noskel=1 ou localStorage.skeletonOff='1'
(function () {
  'use strict';
  try {
    var qs = new URLSearchParams(window.location.search || '');
    var off = qs.has('noskel') || (localStorage.getItem('skeletonOff') === '1');
    if (!off) return;
    document.documentElement.setAttribute('data-skeleton-off', '1');
    var st = document.createElement('style');
    st.textContent = [
      '[data-skeleton-off="1"] .skeleton-wrap,',
      '[data-skeleton-off="1"] .skeleton-cats,',
      '[data-skeleton-off="1"] .skeleton-nearby { display:none !important; }',
      '[data-skeleton-off="1"] .conteudo-card-carousel.is-loading > * { visibility: visible !important; }',
      '[data-skeleton-off="1"] .conteudo-card-carousel.is-loading { pointer-events: auto !important; }',
      '[data-skeleton-off="1"] .categories-grid.is-loading,',
      '[data-skeleton-off="1"] .nearby-list.is-loading { pointer-events: auto !important; }'
    ].join(' ');
    document.head.appendChild(st);
    var nuke = function () {
      document.querySelectorAll('.skeleton-wrap,.skeleton-cats,.skeleton-nearby').forEach(function (el) { el.remove(); });
      document.querySelectorAll('.conteudo-card-carousel.is-loading, .categories-grid.is-loading, .nearby-list.is-loading')
        .forEach(function (el) { el.classList.remove('is-loading'); el.removeAttribute('aria-busy'); });
    };
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', nuke);
    } else {
      nuke();
    }
    console.info('[SKELETON] desativado (noskel/localStorage.skeletonOff=1)');
  } catch (e) { /* no-op */ }
})();
