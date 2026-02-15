// -*- coding: utf-8 -*-
// Injeta botão "Esqueci minha senha" no formulário de login e chama /api/forgot-password.
(function () {
  'use strict';

  function findLoginForm() {
    return document.querySelector('form#login, form[name="login"], form[data-login], .login form') ||
      document.querySelector('form');
  }

  function attachForgot() {
    var form = findLoginForm();
    if (!form || form.__forgotWired) return;
    form.__forgotWired = true;
    var email = form.querySelector('input[type="email"], input[name="email"], input[name="usuario"]');
    var pwdRow = form.querySelector('input[type="password"]');
    if (pwdRow && pwdRow.closest) pwdRow = pwdRow.closest('.row, .field, .form-group');
    if (!pwdRow) pwdRow = form;
    var link = document.createElement('button');
    link.type = 'button';
    link.className = 'btn btn-soft';
    link.style.marginTop = '6px';
    link.textContent = 'Esqueci minha senha';
    link.addEventListener('click', async function () {
      var addr = (email && email.value) || '';
      if (!addr) addr = (window.prompt('Qual é o seu e-mail de cadastro?') || '').trim();
      else addr = (addr || '').trim();
      if (!addr) return;
      try {
        var r = await fetch('/api/forgot-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email: addr })
        });
        if (r.ok) alert('Se o e-mail existir, enviamos um link para redefinir a senha.');
        else alert('Não foi possível enviar agora. Tente novamente em instantes.');
      } catch (_) {
        alert('Não foi possível enviar agora. Tente novamente em instantes.');
      }
    });
    pwdRow.appendChild(link);
  }

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }
  ready(attachForgot);
})();
