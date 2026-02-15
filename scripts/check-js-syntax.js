/**
 * Checa sintaxe JS via node --check (ignora *.min.js, dist/build/vendor).
 * Aceita lista de arquivos do lint-staged (após --) ou usa fast-glob.
 */
const { spawnSync } = require('node:child_process');
const path = require('node:path');

const SEP = '--';
const rawArgs = process.argv.slice(2);
const sepIdx = rawArgs.indexOf(SEP);
const args = sepIdx === -1 ? rawArgs : rawArgs.slice(0, sepIdx);

let files = [];
if (args.length) {
  files = args.filter((f) => typeof f === 'string' && f.endsWith('.js') && !/\.min\.js$/.test(f));
} else {
  try {
    const fg = require('fast-glob');
    files = fg.sync(
      [
        'backend/static/js/**/*.js',
        'frontend/src/**/*.js',
        'scripts/**/*.js',
        'tests/**/*.js',
        '!**/*.min.js',
        '!**/vendor/**',
        '!**/dist/**',
        '!**/build/**',
        '!**/node_modules/**'
      ],
      { dot: true }
    );
  } catch (e) {
    const fs = require('node:fs');
    const root = path.join(__dirname, '..', 'backend', 'static', 'js');
    if (!fs.existsSync(root)) {
      console.log('[check-js] Nenhum arquivo para checar');
      process.exit(0);
    }
    const walk = (dir) => {
      let list = [];
      for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, ent.name);
        if (ent.isDirectory()) list = list.concat(walk(full));
        else if (ent.isFile() && ent.name.endsWith('.js') && !ent.name.endsWith('.min.js')) list.push(full);
      }
      return list;
    };
    files = walk(root);
  }
}

files = files.filter((f) => f.endsWith('.js') && !/\.min\.js$/.test(f));
if (!files.length) {
  console.log('[check-js] Nenhum arquivo para checar');
  process.exit(0);
}

for (const f of files) {
  const r = spawnSync(process.execPath, ['--check', f], { stdio: 'inherit' });
  if (r.status !== 0) {
    console.error('[check-js] Falha em:', f);
    process.exit(r.status || 1);
  }
}
console.log('[check-js] OK em', files.length, 'arquivos');
