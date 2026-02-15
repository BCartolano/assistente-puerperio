/**
 * /api/* sempre da rede (no-store), com fallback de cache só se offline.
 */
(function () {
  'use strict';
  self.addEventListener('fetch', function (event) {
    try {
      var req = event.request;
      if (req.method !== 'GET' && req.method !== 'HEAD') return;
      var url = new URL(req.url);
      if (url.origin !== self.location.origin) return;
      if (!/^\/api\//i.test(url.pathname)) return;
      event.respondWith(
        fetch(req, { cache: 'no-store' }).catch(function () {
          return caches.match(req);
        })
      );
    } catch (_) {}
  });
})();
