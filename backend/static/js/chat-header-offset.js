// Define --chat-header-offset conforme a barra superior real (responsivo).
// Adiciona .is-stuck no header quando "grudado" no topo (sombra suave).
(function () {
  'use strict';

  function computeOffset() {
    try {
      var navbar = document.querySelector('.topbar, .app-header, header, .navbar, .site-header');
      var h = navbar ? Math.ceil(navbar.getBoundingClientRect().height) : 0;
      var offset = Math.max(0, h + 8);
      document.documentElement.style.setProperty('--chat-header-offset', offset + 'px');
    } catch (_) {}
  }

  function observeStuck() {
    var hdr = document.getElementById('chat-header-fixed');
    if (!hdr) return;
    var obs = new IntersectionObserver(
      function (entries) {
        var e = entries[0];
        if (e) hdr.classList.toggle('is-stuck', e.intersectionRatio < 1);
      },
      { threshold: [1] }
    );
    obs.observe(hdr);
  }

  document.addEventListener('DOMContentLoaded', function () {
    computeOffset();
    observeStuck();
  });
  window.addEventListener('resize', computeOffset);
})();
