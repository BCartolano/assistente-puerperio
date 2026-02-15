// -*- coding: utf-8 -*-
// Chips de filtro e "Ver todos" para as categorias da home.
// - Não altera o HTML original; injeta toolbar e filtra por texto/dados heurísticos.
(function () {
  'use strict';

  function injectCSS(href) {
    try {
      var l = document.createElement('link');
      l.rel = 'stylesheet';
      l.href = href;
      document.head.appendChild(l);
    } catch (_) {}
  }

  function norm(s) {
    return (s || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
  }

  var LABELS = ['guias praticos', 'gestacao', 'pos-parto', 'pos parto', 'vacinacao'];

  function looksLikeCategory(el) {
    var t = norm(el.textContent || '');
    return LABELS.some(function (l) { return t.indexOf(l) !== -1; });
  }

  function findSection() {
    var candidates = Array.from(document.querySelectorAll('section, .section, .home-categories, .categories, .cards, .grid, #categories'));
    for (var i = 0; i < candidates.length; i++) {
      var c = candidates[i];
      var hits = 0;
      c.querySelectorAll('*').forEach(function (n) {
        if (n.children && n.children.length > 6) return;
        if (looksLikeCategory(n)) hits++;
      });
      if (hits >= 3) return c;
    }
    return null;
  }

  function tagsForItem(el) {
    try {
      if (el.dataset && el.dataset.tags) {
        return el.dataset.tags.split(',').map(function (s) { return norm(s); }).filter(Boolean);
      }
      var t = norm(el.textContent || '');
      var tags = [];
      if (/(gesta|mae|matern)/.test(t)) tags.push('mae');
      if (/(puerper|pos parto|pos-parto)/.test(t)) tags.push('mae');
      if (/(bebe|bebê|crianc|recemnasc)/.test(t)) tags.push('bebe');
      if (/vacin/.test(t)) tags.push('bebe');
      if (/guia/.test(t)) { tags.push('mae'); tags.push('bebe'); }
      if (/(0[\s\-–—]*6|ate 6)/.test(t)) tags.push('0-6');
      if (/(6[\s\-–—]*12|6 a 12)/.test(t)) tags.push('6-12');
      return Array.from(new Set(tags));
    } catch (_) { return []; }
  }

  function buildToolbar() {
    var bar = document.createElement('div');
    bar.className = 'categories-toolbar';
    bar.innerHTML =
      '<div class="filter-chips">' +
      '  <button class="chip" data-tag="mae" type="button">Para a mãe</button>' +
      '  <button class="chip" data-tag="bebe" type="button">Para o bebê</button>' +
      '  <button class="chip" data-tag="0-6" type="button">Até 6 meses</button>' +
      '  <button class="chip" data-tag="6-12" type="button">6–12 meses</button>' +
      '</div>' +
      '<a class="view-all" href="#" data-reset>Ver todos</a>';
    return bar;
  }

  function applyFilter(grid, items, activeTags) {
    var any = activeTags && activeTags.length > 0;
    items.forEach(function (el) {
      if (!any) { el.style.display = ''; return; }
      var itags = tagsForItem(el);
      var match = itags.some(function (t) { return activeTags.indexOf(t) >= 0; });
      el.style.display = match ? '' : 'none';
    });
  }

  function persist(tags) {
    try { sessionStorage.setItem('categories.activeTags', JSON.stringify(tags || [])); } catch (_) {}
  }

  function restore() {
    try {
      var s = sessionStorage.getItem('categories.activeTags');
      if (!s) return [];
      var a = JSON.parse(s);
      return Array.isArray(a) ? a : [];
    } catch (_) { return []; }
  }

  function wire() {
    injectCSS('/static/css/categories-filters.css');
    var section = findSection();
    if (!section) return;
    var grid = section.classList.contains('categories-grid') ? section : (section.querySelector('.categories-grid') || section);
    var items = Array.from(grid.children);
    if (items.length === 0) {
      items = Array.from(grid.querySelectorAll(':scope > * > *'));
    }
    var bar = buildToolbar();
    grid.parentNode.insertBefore(bar, grid);
    var chips = Array.from(bar.querySelectorAll('.chip'));
    var active = restore();
    chips.forEach(function (ch) {
      var t = ch.dataset.tag;
      if (active.indexOf(t) >= 0) ch.classList.add('active');
    });
    applyFilter(grid, items, active);

    function currentActive() {
      return chips.filter(function (ch) { return ch.classList.contains('active'); })
        .map(function (ch) { return ch.dataset.tag; });
    }

    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        ch.classList.toggle('active');
        var act = currentActive();
        applyFilter(grid, items, act);
        persist(act);
      });
    });

    var viewAll = bar.querySelector('[data-reset]');
    if (viewAll) {
      viewAll.addEventListener('click', function (e) {
        e.preventDefault();
        chips.forEach(function (ch) { ch.classList.remove('active'); });
        applyFilter(grid, items, []);
        persist([]);
        var href = grid.getAttribute('data-viewall-href');
        if (href) { try { window.location.assign(href); } catch (_) {} }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }
})();
