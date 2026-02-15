// -*- coding: utf-8 -*-
// Remove o botão "Atualizar localização (GPS)" de qualquer modal/área.
(function(){
  'use strict';
  function kill(){
    try{
      document.querySelectorAll('[data-action="gps-refresh"]').forEach(function(b){ b.remove(); });
      Array.from(document.querySelectorAll('button, a')).forEach(function(el){
        var t = (el.textContent||'').trim().toLowerCase();
        if (t.includes('atualizar') && (t.includes('gps') || t.includes('localiza'))) el.remove();
      });
    }catch(_){}
  }
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', kill); else kill();
})();
