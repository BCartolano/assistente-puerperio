#!/usr/bin/env node
/**
 * Impede docs/rascunhos fora de docs/ e binários grandes em commits.
 * Pre-commit: bloqueia arquivos que devem estar em docs/ ou que excedem tamanho.
 */
const { execSync } = require('node:child_process');
const fs = require('node:fs');

function getStaged() {
  const out = execSync('git diff --cached --name-only -z', { encoding: 'utf8' });
  return out.split('\0').filter(Boolean);
}

const DOC_EXT = /\.(md|mdx|txt|rtf|docx?|pdf)$/i;
const KEYWORDS = /(guia|resumo|como[-_ ]?usar|como[-_ ]?instalar|instala(c|ç)ao|solu(c|ç)ao|resolver|instru(c|ç)oes|how[-_ ]?to|tutorial|ideia|ideas?|cursor|bmad|agente|draft|old|deprecated|desabilitad[oa]|desativad[oa]|backup)/i;
const ALLOWED_DOC_PATH = /^docs\//i;
const MAX_DOC_SIZE = 1 * 1024 * 1024; // 1 MB

const staged = getStaged();
let blocked = false;
const msgs = [];

for (const file of staged) {
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) continue;
  const p = file.replace(/\\/g, '/');
  const isDocLike = DOC_EXT.test(p) || KEYWORDS.test(p);
  if (isDocLike && !ALLOWED_DOC_PATH.test(p)) {
    blocked = true;
    msgs.push(`- ${p}: documentos devem ficar em docs/ (mova com 'git mv ${p} docs/')`);
  }
  const size = fs.statSync(file).size;
  if ((DOC_EXT.test(p) || /\/assets\//i.test(p)) && size > MAX_DOC_SIZE) {
    blocked = true;
    msgs.push(`- ${p}: ${Math.round(size / 1024)} KB — muito grande. Comprima (WebP/AVIF) ou mova para storage externo.`);
  }
}

if (blocked) {
  console.error('\n[guard-docs] Commit bloqueado:\n' + msgs.join('\n'));
  console.error('\nDica: use npm run docs:triage para identificar/arquivar arquivos suspeitos.\n');
  process.exit(1);
}
process.exit(0);
