/**
 * Login/registro mínimo para página data-page="login".
 * Não depende de chat.js — parse error em chat.js não quebra login.
 * Form tem action="/auth/login" method="POST" para fallback sem JS.
 */
(function () {
    'use strict';

    var loginForm = document.getElementById('initial-login-form');
    var registerForm = document.getElementById('initial-register-form');
    var loginTabs = document.querySelectorAll('.login-tab');

    function switchTab(tab) {
        if (!loginTabs.length || !loginForm || !registerForm) return;
        loginTabs.forEach(function (t) { t.classList.remove('active'); });
        loginForm.classList.remove('active');
        registerForm.classList.remove('active');
        if (tab === 'login') {
            var el = document.querySelector('[data-tab="login"]');
            if (el) el.classList.add('active');
            loginForm.classList.add('active');
        } else if (tab === 'register') {
            var el2 = document.querySelector('[data-tab="register"]');
            if (el2) el2.classList.add('active');
            registerForm.classList.add('active');
        }
    }

    function loadRememberedEmail() {
        var emailInput = document.getElementById('initial-login-email');
        if (!emailInput) return;
        var remembered = localStorage.getItem('remembered_email');
        if (remembered) {
            emailInput.value = remembered;
            var cb = document.getElementById('initial-remember-me');
            if (cb) cb.checked = true;
        }
    }

    function doLogin() {
        var emailInput = document.getElementById('initial-login-email');
        var passwordInput = document.getElementById('initial-login-password');
        var rememberMe = document.getElementById('initial-remember-me');
        if (!emailInput || !passwordInput) {
            alert('Campos de login não encontrados. Recarregue a página.');
            return;
        }
        var email = emailInput.value.trim().toLowerCase();
        var password = passwordInput.value.trim();
        if (!email || !password) {
            alert('Por favor, preencha todos os campos! 💕');
            return;
        }
        var remember = rememberMe ? rememberMe.checked : false;
        if (remember) localStorage.setItem('remembered_email', email);
        else localStorage.removeItem('remembered_email');

        fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email: email, password: password, remember_me: remember })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.sucesso === true || data.user) {
                    window.location.reload();
                } else {
                    alert('⚠️ ' + (data.erro || data.mensagem || 'Erro ao fazer login'));
                }
            })
            .catch(function () {
                alert('❌ Erro ao fazer login. Tente novamente.');
            });
    }

    function doRegister() {
        var nameEl = document.getElementById('initial-register-name');
        var emailEl = document.getElementById('initial-register-email');
        var passwordEl = document.getElementById('initial-register-password');
        var babyEl = document.getElementById('initial-register-baby');
        if (!nameEl || !emailEl || !passwordEl) {
            alert('Campos de cadastro não encontrados.');
            return;
        }
        var name = nameEl.value.trim();
        var email = emailEl.value.trim().toLowerCase();
        var password = passwordEl.value;
        var babyName = babyEl ? babyEl.value.trim() : '';
        if (!name || !email || !password) {
            alert('Por favor, preencha os campos obrigatórios! 💕');
            return;
        }
        if (password.length < 6) {
            alert('A senha deve ter no mínimo 6 caracteres! 💕');
            return;
        }
        fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, email: email, password: password, baby_name: babyName })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.sucesso || data.id) {
                    alert('Cadastro realizado! 🎉 ' + (data.mensagem || 'Faça login com seu email.'));
                    switchTab('login');
                    var loginEmail = document.getElementById('initial-login-email');
                    if (loginEmail) loginEmail.value = email;
                } else {
                    alert('⚠️ ' + (data.erro || data.mensagem || 'Erro ao cadastrar'));
                }
            })
            .catch(function () {
                alert('❌ Erro ao cadastrar. Tente novamente.');
            });
    }

    if (loginTabs.length) {
        loginTabs.forEach(function (tab) {
            tab.addEventListener('click', function () { switchTab(tab.dataset.tab); });
        });
    }
    loadRememberedEmail();

    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();
            doLogin();
            return false;
        });
        var loginBtn = document.getElementById('initial-login-submit');
        if (loginBtn) {
            loginBtn.onclick = null;
            loginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                doLogin();
                return false;
            });
        }
    }

    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
            e.preventDefault();
            doRegister();
            return false;
        });
        var regBtn = document.getElementById('initial-register-submit');
        if (regBtn) {
            regBtn.addEventListener('click', function (e) {
                e.preventDefault();
                doRegister();
                return false;
            });
        }
    }

    window.handleLoginClick = function () {
        doLogin();
    };
})();
