#!/usr/bin/env node
/**
 * Gera lista de candidatos à remoção do HISTÓRICO e um template de paths.txt.
 * NÃO altera o repo. Só escreve na pasta .purge/
 * Edite .purge/paths.txt e rode npm run purge:run para executar a purga.
 */
const fs = require('node:fs');
const path = require('node:path');
const fsp = require('node:fs/promises');

const ROOT = process.cwd();
const PURGE_DIR = path.join(ROOT, '.purge');
const CANDIDATES = path.join(PURGE_DIR, 'candidates.txt');
const LARGE = path.join(PURGE_DIR, 'large-blobs.txt');
const PATHS = path.join(PURGE_DIR, 'paths.txt');

const IGNORE = [
  '/node_modules/',
  '/dist/',
  '/build/',
  '/.cache/',
  '/.purge/',
  '/.git/'
];

const SAFE_DIRS = [
  'ai-sandbox/',
  'ideas/',
  'notes/',
  'drafts/',
  'tmp/',
  '**/old/',
  '**/backup/',
  '**/deprecated/',
  '**/disabled/'
];

const HEAVY_EXT = ['psd', 'ai', 'sketch', 'zip', '7z', 'rar', 'iso', 'mp4', 'mov', 'avi', 'mkv', 'wmv', 'mp3', 'wav', 'ogg', 'webm', 'apk', 'ipa', 'exe', 'dmg'];
const LARGE_FILE_LIMIT = 5 * 1024 * 1024; // 5MB

async function ensureDir(p) {
  await fsp.mkdir(p, { recursive: true });
}

function size(filePath) {
  try {
    return fs.statSync(filePath).size;
  } catch {
    return 0;
  }
}

async function main() {
  await ensureDir(PURGE_DIR);

  let dirFiles = [];
  let heavy = [];
  let all = [];
  try {
    const fg = require('fast-glob');
    dirFiles = await fg(SAFE_DIRS.map((d) => d + '**/*'), { ignore: IGNORE, onlyFiles: true, dot: true, cwd: ROOT });
    heavy = await fg([`**/*.{${HEAVY_EXT.join(',')}}`], { ignore: IGNORE, onlyFiles: true, dot: true, cwd: ROOT });
    all = await fg('**/*', { ignore: IGNORE, onlyFiles: true, dot: true, cwd: ROOT });
  } catch (e) {
    console.warn('[purge:plan] fast-glob necessário: npm i fast-glob');
    process.exit(1);
  }

  const dirRoots = new Set(dirFiles.map((f) => f.split(/[/\\]/)[0] + '/'));
  const large = all.filter((f) => size(f) > LARGE_FILE_LIMIT);

  const lines = [];
  lines.push('# Diretórios candidatos (remover inteiros do histórico):');
  if (dirRoots.size) {
    [...dirRoots].sort().forEach((d) => lines.push(d));
  } else {
    lines.push('# (nenhum diretório típico encontrado)');
  }
  lines.push('');
  lines.push('# Binários pesados por extensão:');
  heavy
    .sort((a, b) => size(b) - size(a))
    .slice(0, 500)
    .forEach((f) => lines.push(`${f} # ${Math.round(size(f) / 1024)} KB`));
  lines.push('');
  lines.push('# Arquivos grandes (qualquer extensão) > 5MB:');
  large
    .sort((a, b) => size(b) - size(a))
    .slice(0, 500)
    .forEach((f) => lines.push(`${f} # ${Math.round(size(f) / 1024)} KB`));

  await fsp.writeFile(CANDIDATES, lines.join('\n'), 'utf8');

  const template = [
    '# Coloque aqui caminhos LITERAIS a remover do histórico (diretórios com / no final).',
    '# Ex.:',
    '# ai-sandbox/',
    '# ideas/',
    '# drafts/',
    '# tmp/'
  ];
  await fsp.writeFile(PATHS, template.join('\n'), 'utf8');

  const largeLines = large
    .sort((a, b) => size(b) - size(a))
    .map((f) => `${Math.round(size(f) / 1024)} KB\t${f}`);
  await fsp.writeFile(LARGE, largeLines.join('\n'), 'utf8');

  console.log('[purge:plan] Gerado:');
  console.log('  ', path.relative(ROOT, CANDIDATES));
  console.log('  ', path.relative(ROOT, LARGE));
  console.log('  ', path.relative(ROOT, PATHS), '(edite antes da purga)');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
