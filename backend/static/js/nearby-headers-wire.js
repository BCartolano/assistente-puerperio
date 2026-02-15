// -*- coding: utf-8 -*-
// Captura headers do /api/nearby e publica eventos para painel/tooltip (0095)
(function(){
  'use strict';
  if (!('fetch' in window)) return;
  var _orig = window.fetch;

  window.refreshNearbyHeaders = async function(){
    try{
      var h = window.__NEARBY_HEADERS;
      if (!h || !h.url) return null;
      var r = await _orig(h.url, { cache:'no-store' });
      if (!r.ok) return null;
      var hdr = {
        url: h.url,
        x_data_source: r.headers.get('x-data-source') || null,
        x_data_mtime: (function(x){ return (x && !isNaN(Number(x))) ? Number(x) : (x||null); })(r.headers.get('x-data-mtime')),
        x_data_count: (function(x){ return (x && !isNaN(Number(x))) ? Number(x) : (x||null); })(r.headers.get('x-data-count')),
        q_lat: r.headers.get('x-query-lat') || null,
        q_lon: r.headers.get('x-query-lon') || null,
        q_radius_km: r.headers.get('x-query-radius') || null,
        fetched_at: Date.now()
      };
      window.__NEARBY_HEADERS = hdr;
      try{
        var base = (hdr.x_data_source||'').split(/[\\/]/).pop();
        var mIso = (typeof hdr.x_data_mtime==='number')
          ? new Date(hdr.x_data_mtime>1e12? hdr.x_data_mtime : hdr.x_data_mtime*1000).toISOString() : '';
        window.dispatchEvent(new CustomEvent('nearby:search-done', { detail: {
          url: hdr.url, count: hdr.x_data_count, source: base, x_data_source: hdr.x_data_source, x_data_mtime: hdr.x_data_mtime, mtime_iso: mIso,
          lat: hdr.q_lat, lon: hdr.q_lon, radius_km: hdr.q_radius_km, fetched_at: hdr.fetched_at, type: 'nearby'
        }}));
      }catch(_){}
      return hdr;
    }catch(_){ return null; }
  };

  window.fetch = function(input, init){
    var url = null;
    try{
      url = (typeof input === 'string') ? new URL(input, location.origin)
        : (input && input.url) ? new URL(input.url) : null;
    }catch(_){}
    var isNearby = url && /\/api\/nearby/i.test(url.pathname);
    return _orig.apply(this, arguments).then(function(res){
      try{
        if (isNearby){
          var hdr = {
            url: url ? url.toString() : '',
            x_data_source: res.headers.get('x-data-source') || null,
            x_data_mtime: (function(x){ return (x && !isNaN(Number(x))) ? Number(x) : (x||null); })(res.headers.get('x-data-mtime')),
            x_data_count: (function(x){ return (x && !isNaN(Number(x))) ? Number(x) : (x||null); })(res.headers.get('x-data-count')),
            q_lat: res.headers.get('x-query-lat') || null,
            q_lon: res.headers.get('x-query-lon') || null,
            q_radius_km: res.headers.get('x-query-radius') || null,
            fetched_at: Date.now()
          };
          window.__NEARBY_HEADERS = hdr;
          try{
            var count = hdr.x_data_count; var src = hdr.x_data_source; var mt = hdr.x_data_mtime;
            console.info('[NEARBY] busca: count=%s fonte=%s mtime=%s lat=%s lon=%s radius_km=%s',
              (count!=null?count:'(n/d)'), (src||'(n/d)'), (mt||'(n/d)'), hdr.q_lat||'', hdr.q_lon||'', hdr.q_radius_km||'');
          }catch(_){}
          try{
            window.dispatchEvent(new CustomEvent('nearby:search-result', { detail: hdr }));
            var base = (hdr.x_data_source||'').split(/[\\/]/).pop();
            var mIso = (typeof hdr.x_data_mtime==='number')
              ? new Date(hdr.x_data_mtime>1e12? hdr.x_data_mtime : hdr.x_data_mtime*1000).toISOString() : '';
            window.dispatchEvent(new CustomEvent('nearby:search-done', { detail: {
              url: hdr.url, count: hdr.x_data_count, source: base, x_data_source: hdr.x_data_source, x_data_mtime: hdr.x_data_mtime, mtime_iso: mIso,
              lat: hdr.q_lat, lon: hdr.q_lon, radius_km: hdr.q_radius_km, fetched_at: hdr.fetched_at, type: 'nearby'
            }}));
          }catch(_){}
        }
      }catch(_){}
      return res;
    }).catch(function(err){
      try{
        if (isNearby){
          window.dispatchEvent(new CustomEvent('nearby:fetch-error', { detail: { error: String(err) } }));
        }
      }catch(_){}
      throw err;
    });
  };
})();
