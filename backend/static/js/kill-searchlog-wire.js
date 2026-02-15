// -*- coding: utf-8 -*-
// Remove "Detalhes da busca" (painel hosp-log) se existir em algum HTML antigo.
(function(){
  'use strict';
  function nuke(){
    try{
      document.querySelectorAll('.hosp-log, .hosp-log-toggle').forEach(function(n){ n.remove(); });
    }catch(_){}
  }
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', nuke); else nuke();
})();
