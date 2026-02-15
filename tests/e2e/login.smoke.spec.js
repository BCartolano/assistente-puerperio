/**
 * E2E smoke: login carrega sem chat.js e é utilizável.
 * Rode: BASE_URL=http://localhost:5000 npm run test:e2e (ajuste porta se necessário)
 */
const { test, expect } = require('@playwright/test');

const BASE = process.env.BASE_URL || process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:5000';

test('login carrega sem chat.js e é utilizável', async ({ page }) => {
  await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' });

  // Se redirecionou para /login ou já está na tela de login (form visível)
  const form = page.locator('form[action*="auth"][method="post"], form[action*="login"][method="post"], #initial-login-form');
  await expect(form.first()).toBeVisible({ timeout: 10000 });

  // Form tem fallback sem JS (action + method)
  const action = await page.getAttribute('form#initial-login-form', 'action') || await page.getAttribute('form[method="POST"]', 'action');
  expect(action).toBeTruthy();

  // chat.js não é carregado nesta rota (page=login só carrega boot.js + auth/login.js)
  const chatScriptCount = await page.locator('script[src*="chat"]').count();
  expect(chatScriptCount).toBe(0);

  // Campos e botão visíveis
  await expect(page.locator('input[type="email"]').first()).toBeVisible();
  await expect(page.locator('input[type="password"]').first()).toBeVisible();
  await expect(page.getByRole('button', { name: /entrar/i }).first()).toBeVisible();

  // Preenche (sem submeter de verdade)
  await page.fill('input[type="email"]', 'user@example.com');
  await page.fill('input[type="password"]', '12345678');
});
