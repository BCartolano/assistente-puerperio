module.exports = {
  env: { browser: true, node: true, es2021: true },
  extends: ['eslint:recommended'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'script' },
  ignorePatterns: [
    '**/*.min.js',
    'dist/',
    'build/',
    'vendor/',
    'node_modules/',
    '.cache/',
    '.parcel-cache/',
    '.turbo/',
    '.next/',
    '.nuxt/',
    'coverage/',
    '*.config.js',
    '*.config.cjs',
    'BMAD-METHOD-v5/',
    '**/BMAD-METHOD-v5/**'
  ],
  rules: {
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
    'no-empty': ['warn', { allowEmptyCatch: true }]
  },
  overrides: [
    { files: ['tests/**/*.js', '**/*.test.js'], env: { jest: true } },
    { files: ['frontend/**/*.js', 'frontend/**/*.jsx'], parserOptions: { sourceType: 'module' } },
    { files: ['backend/static/sw.js'], globals: { importScripts: 'readonly', self: 'readonly', caches: 'readonly', clients: 'readonly' } }
  ]
};
