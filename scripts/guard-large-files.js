#!/usr/bin/env node
/**
 * Bloqueia arquivo gigante em commit. Padrão: 10MB (LARGE_FILE_LIMIT_MB).
 */
const { execSync } = require('node:child_process');
const fs = require('node:fs');

const LIMIT_MB = parseInt(process.env.LARGE_FILE_LIMIT_MB || '10', 10);
const LIMIT = LIMIT_MB * 1024 * 1024;

function stagedFiles() {
  const out = execSync('git diff --cached --name-only -z', { encoding: 'utf8' });
  return out.split('\0').filter(Boolean);
}

const EXEMPT = [/^vendor\//i, /^third[_-]?party\//i, /^node_modules\//i];

let blocked = false;
const msgs = [];
for (const f of stagedFiles()) {
  try {
    if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) continue;
    if (EXEMPT.some((re) => re.test(f))) continue;
    const size = fs.statSync(f).size;
    if (size > LIMIT) {
      blocked = true;
      msgs.push(`- ${f}: ${(size / (1024 * 1024)).toFixed(2)} MB > ${LIMIT_MB} MB`);
    }
  } catch (e) {
    // ignora arquivos deletados/renomeados
  }
}

if (blocked) {
  console.error(`\n[guard-large-files] Arquivos muito grandes no commit (limite ${LIMIT_MB}MB):\n` + msgs.join('\n'));
  console.error('\nSugestões: comprima, mova para storage externo, ou use Git LFS.');
  process.exit(1);
}
process.exit(0);
