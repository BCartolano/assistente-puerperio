#!/usr/bin/env node
/**
 * Lista e (opcionalmente) move para docs/archive/ arquivos "sobrando".
 * Uso: node scripts/triage-extraneous.js (só lista) | node scripts/triage-extraneous.js --archive (move com git mv)
 */
const fs = require('node:fs');
const path = require('node:path');
const fsp = require('node:fs/promises');
const { spawnSync } = require('node:child_process');

const ROOT = process.cwd();
const ARCHIVE_DIR = path.join(ROOT, 'docs', 'archive');
const DO_ARCHIVE = process.argv.includes('--archive');

const IGNORE = [
  '/node_modules/',
  '/dist/',
  '/build/',
  '/.cache/',
  '/.parcel-cache/',
  '/.turbo/',
  '/.next/',
  '/.nuxt/',
  '/vendor/',
  '/coverage/',
  '/.git/',
  '/.purge/'
];

const DOC_EXT = ['md', 'mdx', 'txt', 'rtf', 'doc', 'docx', 'pdf'];
const KEYWORDS = /(guia|resumo|como[-_ ]?usar|como[-_ ]?instalar|instala(c|ç)ao|solu(c|ç)ao|resolver|instru(c|ç)oes|how[-_ ]?to|tutorial|ideia|ideas?|cursor|bmad|agente|draft|old|deprecated|desabilitad[oa]|desativad[oa]|backup)/i;

function isDocCandidate(p) {
  const ext = p.split('.').pop()?.toLowerCase();
  const looksDoc = DOC_EXT.includes(ext) || KEYWORDS.test(p);
  const inDocs = /^docs\//i.test(p.replace(/\\/g, '/'));
  return looksDoc && !inDocs;
}

function isDisabledDir(p) {
  return /(\/|^)(old|backup|deprecated|disabled|desabilitado|desativado|zz_|_old)(\/|$)/i.test(p);
}

function sizeOf(p) {
  try {
    return fs.statSync(p).size;
  } catch {
    return 0;
  }
}

async function ensureDir(p) {
  await fsp.mkdir(p, { recursive: true });
}

function gitMv(from, to) {
  const res = spawnSync('git', ['mv', '--force', from, to], { stdio: 'inherit' });
  if (res.status !== 0) throw new Error(`git mv falhou: ${from} -> ${to}`);
}

async function main() {
  const patterns = ['**/*.md', '**/*.mdx', '**/*.txt', '**/*.rtf', '**/*.doc', '**/*.docx', '**/*.pdf'];
  let files = [];
  try {
    const fg = require('fast-glob');
    files = await fg(patterns, {
      ignore: IGNORE.map((d) => d.replace(/^\//, '**/')),
      onlyFiles: true,
      dot: true,
      cwd: ROOT
    });
  } catch (e) {
    console.warn('[triage] fast-glob não encontrado; use npm i fast-glob');
    process.exit(1);
  }

  const candidates = [];
  for (const file of files) {
    const unixPath = file.replace(/\\/g, '/');
    const dir = path.dirname(file);
    if (isDocCandidate(unixPath) || isDisabledDir(dir)) {
      candidates.push(unixPath);
    }
  }

  if (!candidates.length) {
    console.log('[triage] Nenhum candidato encontrado');
    return;
  }

  candidates.sort((a, b) => sizeOf(b) - sizeOf(a));
  console.log('[triage]', candidates.length, 'candidatos encontrados:\n');
  for (const p of candidates.slice(0, 200)) {
    const kb = Math.round(sizeOf(p) / 1024);
    console.log(p, '—', kb, 'KB');
  }

  if (!DO_ARCHIVE) {
    console.log('\nTIP: rode com --archive para mover para docs/archive/ (git mv).');
    return;
  }

  console.log('\n[triage] Movendo para docs/archive/ ...');
  await ensureDir(ARCHIVE_DIR);
  for (const rel of candidates) {
    const target = path.join('docs', 'archive', rel);
    await ensureDir(path.dirname(target));
    try {
      gitMv(rel, target);
    } catch (e) {
      try {
        await ensureDir(path.dirname(target));
        await fsp.rename(rel, target);
        console.warn('[triage] (untracked) movido:', rel, '->', target);
      } catch (err) {
        console.error('[triage] falha ao mover', rel, err.message);
      }
    }
  }
  console.log('[triage] Concluído. Atualize docs/INDEX.md conforme necessário.');
}

main().catch((e) => {
  console.error('[triage] erro:', e);
  process.exit(1);
});
