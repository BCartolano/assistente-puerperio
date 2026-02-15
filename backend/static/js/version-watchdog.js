/**
 * Version watchdog: consulta /version.json; se mudar, atualiza SW, limpa caches de assets e recarrega.
 */
(function () {
  'use strict';
  var CHECK_MS = 5 * 60 * 1000; // 5 min

  function getLocal() {
    try {
      return localStorage.getItem('app_version') || '';
    } catch (_) {
      return '';
    }
  }

  function setLocal(v) {
    try {
      localStorage.setItem('app_version', v || '');
    } catch (_) {}
  }

  async function fetchVersion() {
    try {
      var r = await fetch('/version.json', {
        cache: 'no-store',
        credentials: 'include',
        headers: { 'Cache-Control': 'no-store', Accept: 'application/json' }
      });
      if (!r.ok) return null;
      var j = await r.json().catch(function () { return null; });
      return (j && j.version) ? String(j.version) : null;
    } catch (_) {
      return null;
    }
  }

  async function updateSW() {
    try {
      if (navigator.serviceWorker) {
        var reg = await navigator.serviceWorker.getRegistration();
        if (reg) await reg.update();
      }
    } catch (_) {}
  }

  async function purgeAssetCaches() {
    if (!('caches' in window)) return;
    try {
      var keys = await caches.keys();
      for (var i = 0; i < keys.length; i++) {
        var cache = await caches.open(keys[i]);
        var reqs = await cache.keys();
        for (var j = 0; j < reqs.length; j++) {
          var u = new URL(reqs[j].url);
          if (/\.(js|css)$/i.test(u.pathname) || u.searchParams.has('v')) {
            await cache.delete(reqs[j]);
          }
        }
      }
    } catch (_) {}
  }

  var _lastReloadAt = 0;
  var MIN_RELOAD_INTERVAL_MS = 60000; // Evita loop: não recarrega se último reload foi < 1 min

  async function check() {
    var remote = await fetchVersion();
    if (!remote) return;
    var local = getLocal();
    if (!local) {
      setLocal(remote);
      return;
    }
    if (remote !== local) {
      var now = Date.now();
      if (now - _lastReloadAt < MIN_RELOAD_INTERVAL_MS) {
        try { console.warn('[VERSION] Bloqueado reload em loop - aguarde 1 min'); } catch (_) {}
        setLocal(remote);
        return;
      }
      try {
        console.info('[VERSION] mudou', local, '->', remote);
      } catch (_) {}
      _lastReloadAt = now;
      await updateSW();
      await purgeAssetCaches();
      setLocal(remote);
      location.reload();
    }
  }

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  function triggerAppRefresh() {
    updateSW().then(purgeAssetCaches).then(function () { location.reload(); });
  }
  try {
    window.triggerAppRefresh = triggerAppRefresh;
    window.getAppVersion = fetchVersion;
  } catch (_) {}

  ready(function () {
    try {
      var qs = new URLSearchParams(location.search);
      if (qs.get('refresh') === '1') {
        triggerAppRefresh();
        return;
      }
    } catch (_) {}
    check().then(function () {
      var v = getLocal();
      if (v) try { console.info('[APP] Build:', v); } catch (_) {}
    });
    setInterval(check, CHECK_MS);
  });
})();
