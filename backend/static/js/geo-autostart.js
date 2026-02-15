// -*- coding: utf-8 -*-
// Geolocalização automática: pergunta ao entrar e mantém posição em tempo real.
(function(){
  'use strict';
  if (!('geolocation' in navigator)) return;
  var WATCH_ID = null;
  var opts = { enableHighAccuracy: true, maximumAge: 0, timeout: 20000 };
  function save(lat, lon, acc){
    try{
      window.__GEO_LAST = { lat: Number(lat), lon: Number(lon), accuracy: Number(acc)||null, ts: Date.now() };
      localStorage.setItem('geo:lat', String(lat));
      localStorage.setItem('geo:lon', String(lon));
    }catch(_){}
  }
  function emit(lat, lon, acc){
    try{
      window.dispatchEvent(new CustomEvent('geo:position', { detail: { lat: Number(lat), lon: Number(lon), accuracy: Number(acc)||null, ts: Date.now() } }));
    }catch(_){}
  }
  function onPos(pos){
    try{
      var lat = pos.coords.latitude, lon = pos.coords.longitude, acc = pos.coords.accuracy;
      save(lat, lon, acc); emit(lat, lon, acc);
    }catch(_){}
  }
  function onErr(err){
    try{ console.warn('[GEO] erro', err && (err.code+': '+err.message)); }catch(_){}
  }
  function boot(){
    try{
      navigator.geolocation.getCurrentPosition(onPos, onErr, opts);
      try{ if (WATCH_ID!=null) navigator.geolocation.clearWatch(WATCH_ID); }catch(_){}
      WATCH_ID = navigator.geolocation.watchPosition(onPos, onErr, opts);
      try{
        var lastLat = localStorage.getItem('geo:lat'), lastLon = localStorage.getItem('geo:lon');
        if (lastLat && lastLon) emit(Number(lastLat), Number(lastLon), null);
      }catch(_){}
    }catch(_){}
  }
  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
