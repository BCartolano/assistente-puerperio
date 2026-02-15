// -*- coding: utf-8 -*-
// Captura os headers do /api/v1/emergency/search e guarda em window.__EMERGENCY_HEADERS
(function(){
'use strict';
if (!('fetch' in window)) return;
var _orig = window.fetch;
window.refreshEmergencyHeaders = async function(){ try{ var h=window.__EMERGENCY_HEADERS; if (!h||!h.url) return null; var r=await _orig(h.url, { cache:'no-store' }); if(!r.ok) return null; var xds=r.headers.get('x-data-source'); var xdm=r.headers.get('x-data-mtime'); var xcnt=r.headers.get('x-data-count'); var qlat=r.headers.get('x-query-lat'); var qlon=r.headers.get('x-query-lon'); var qrad=r.headers.get('x-query-radius'); window.__EMERGENCY_HEADERS={ url:h.url, x_data_source:xds||null, x_data_mtime:(xdm&&!isNaN(Number(xdm)))?Number(xdm):(xdm||null), x_data_count:(xcnt&&!isNaN(Number(xcnt)))?Number(xcnt):(xcnt||null), q_lat:qlat||null, q_lon:qlon||null, q_radius_km:qrad||null, fetched_at:Date.now() }; return window.__EMERGENCY_HEADERS; }catch(_){ return null; }};
window.fetch = function(input, init){
  var url = null;
  try{
    url = (typeof input === 'string')
      ? new URL(input, location.origin)
      : (input && input.url) ? new URL(input.url) : null;
  }catch(_){}
  var isEmergency = url && /\/api\/v1\/emergency\/search/i.test(url.pathname);
  return _orig.apply(this, arguments).then(function(res){
    try{
      if (isEmergency){
        var xds = res.headers.get('x-data-source');
        var xdm = res.headers.get('x-data-mtime');
        var xcnt = res.headers.get('x-data-count');
        var qlat = res.headers.get('x-query-lat'), qlon = res.headers.get('x-query-lon'), qrad = res.headers.get('x-query-radius');
        window.__EMERGENCY_HEADERS = {
          url: url ? url.toString() : '',
          x_data_source: xds || null,
          x_data_mtime: (xdm && !isNaN(Number(xdm))) ? Number(xdm) : (xdm || null),
          x_data_count: (xcnt && !isNaN(Number(xcnt))) ? Number(xcnt) : (xcnt || null),
          q_lat: qlat || null, q_lon: qlon || null, q_radius_km: qrad || null,
          fetched_at: Date.now()
        };
        try{
            window.dispatchEvent(new CustomEvent('emergency:search-result', { detail: window.__EMERGENCY_HEADERS }));
            var d = window.__EMERGENCY_HEADERS;
            var base = (d.x_data_source||'').split(/[\\/]/).pop();
            var mIso = (typeof d.x_data_mtime==='number')
              ? new Date(d.x_data_mtime>1e12? d.x_data_mtime : d.x_data_mtime*1000).toISOString() : '';
            window.dispatchEvent(new CustomEvent('emergency:search-done', { detail: { url: d.url, count: d.x_data_count, source: base, x_data_source: d.x_data_source, x_data_mtime: d.x_data_mtime, mtime_iso: mIso, lat: d.q_lat, lon: d.q_lon, radius_km: d.q_radius_km, fetched_at: d.fetched_at } }));
          }catch(_){}
        try{
          var count = window.__EMERGENCY_HEADERS.x_data_count;
          console.info('[EMERGENCY] busca: count=%s fonte=%s mtime=%s lat=%s lon=%s radius_km=%s',
            (count!=null?count:'(n/d)'), (xds||'(n/d)'), (xdm||'(n/d)'), (qlat||''), (qlon||''), (qrad||''));
        }catch(_){}
        if (xds || xdm){
          try{ console.info('[EMERGENCY] headers capturados:', window.__EMERGENCY_HEADERS); }catch(_){}
        }
      }
    }catch(_){}
    return res;
  }).catch(function(err){
    try{
      if (isEmergency){
        window.dispatchEvent(new CustomEvent('emergency:fetch-error', { detail: { error: String(err) } }));
      }
    }catch(_){}
    throw err;
  });
};
})();
