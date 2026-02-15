/**
 * SW básico com guardas de login/auth: não intercepta /login nem /auth.
 * Assets versionados (JS/CSS com ?v=) em network-first para evitar build velho.
 */
importScripts('/static/js/sw-auth-bypass.js');
importScripts('/static/js/sw-assets-bypass.js');
importScripts('/static/js/sw-api-bypass.js');

var CACHE_VERSION = 'v17';
var STATIC_CACHE = 'static-' + CACHE_VERSION;

self.addEventListener('install', function (_event) {
    self.skipWaiting();
});

self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(
                keys.filter(function (k) { return k !== STATIC_CACHE; }).map(function (k) { return caches.delete(k); })
            );
        }).then(function () {
            return self.clients.claim();
        })
    );
});

self.addEventListener('fetch', function (event) {
    var req = event.request;
    var url = new URL(req.url);

    if (url.origin !== self.location.origin) return;
    if (/^\/(login|auth)(\/|$)/i.test(url.pathname)) return;
    if (req.method !== 'GET') return;
    if (/\/api\//i.test(url.pathname)) return;

    event.respondWith(
        caches.open(STATIC_CACHE).then(function (cache) {
            return cache.match(req).then(function (cached) {
                if (cached) return cached;
                return fetch(req).then(function (resp) {
                    if (resp && resp.ok) cache.put(req, resp.clone());
                    return resp;
                });
            });
        })
    );
});
