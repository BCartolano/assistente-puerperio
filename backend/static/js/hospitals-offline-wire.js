// -*- coding: utf-8 -*-
// Banner de offline/timeout (0092): mostra aviso e botão "Tentar novamente"
(function(){
  'use strict';
  function pickHost(){
    return document.querySelector('#hospitals-modal .modal-body') ||
           document.querySelector('#hospitals-modal') ||
           document.querySelector('.hospitals-list, [data-role="hospitals-list"]') ||
           document.body;
  }
  function ensureBanner(host){
    var b = host.querySelector('.hosp-offline');
    if (!b){
      b = document.createElement('div');
      b.className = 'hosp-offline';
      b.innerHTML = '<span>Serviço temporariamente indisponível.</span> '+
                    '<span class="help">Tente novamente em instantes. Em emergência, ligue <strong>192</strong>.</span>'+
                    '<button class="btn-retry" type="button">Tentar novamente</button>';
      if (host.firstChild) host.insertBefore(b, host.firstChild); else host.appendChild(b);
      b.querySelector('.btn-retry').addEventListener('click', async function(){
        try{
          var fn = (window.__EMERGENCY_HEADERS && window.__EMERGENCY_HEADERS.url) ? window.refreshEmergencyHeaders : window.refreshNearbyHeaders;
          var ok = fn ? await fn() : null;
          if (ok){ b.remove(); } else if (!window.refreshEmergencyHeaders && !window.refreshNearbyHeaders){ location.reload(); }
        }catch(_){}
      });
    }
    return b;
  }
  function ready(fn){ if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }
  ready(function(){
    window.addEventListener('emergency:fetch-error', function(){
      var host = pickHost(); ensureBanner(host);
    });
    window.addEventListener('nearby:fetch-error', function(){
      var host = pickHost(); ensureBanner(host);
    });
    window.addEventListener('emergency:search-result', function(){
      var host = pickHost(); var b = host.querySelector('.hosp-offline'); if (b) b.remove();
    });
    window.addEventListener('nearby:search-result', function(){
      var host = pickHost(); var b = host.querySelector('.hosp-offline'); if (b) b.remove();
    });
  });
})();
