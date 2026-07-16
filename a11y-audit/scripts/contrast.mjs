#!/usr/bin/env node
// WCAG 2.x contrast calculator for the Looties palette.
//
// Default (run from repo root): loads colors.neon from ./tailwind.config.js and sweeps
// the standard combinations (text on the three dark surfaces, dark-on-neon and
// white-on-neon button fills, non-text borders/rings).
//
//   node .claude/skills/a11y-audit/scripts/contrast.mjs
//   node .claude/skills/a11y-audit/scripts/contrast.mjs --pair '#94A3B8,#334155' [--pair …]
//   node .claude/skills/a11y-audit/scripts/contrast.mjs --config path/to/tailwind.config.js
//
// AA: ≥4.5 normal text, ≥3.0 large text (≥24px, or ≥18.66px bold) and non-text UI.
// AAA: ≥7.0 / ≥4.5.

import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const hex = (h) => {
  const s = h.replace('#', '');
  const full = s.length === 3 ? [...s].map((c) => c + c).join('') : s;
  return [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16) / 255);
};
const lum = (h) =>
  hex(h)
    .map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
    .reduce((a, c, i) => a + c * [0.2126, 0.7152, 0.0722][i], 0);
const ratio = (a, b) => {
  const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
};
const grade = (r) => (r >= 7 ? 'AAA' : r >= 4.5 ? 'AA' : r >= 3 ? 'AA-large/UI only' : 'FAIL');
const row = (name, r) => console.log(`${name.padEnd(16)} ${r.toFixed(2).padStart(6)}  ${grade(r)}`);

// Tailwind default slate scale (the config does not override slate — verify if that changes).
const SLATE = {
  'slate-200': '#E2E8F0', 'slate-300': '#CBD5E1', 'slate-400': '#94A3B8',
  'slate-500': '#64748B', 'slate-600': '#475569', 'slate-700': '#334155',
  'slate-800': '#1E293B', 'slate-900': '#0F172A', 'slate-950': '#020617',
};

const args = process.argv.slice(2);
const pairs = [];
let configPath = './tailwind.config.js';
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--pair') pairs.push(args[++i]);
  else if (args[i] === '--config') configPath = args[++i];
}

if (pairs.length > 0) {
  console.log('== ad-hoc pairs (fg,bg) ==');
  for (const p of pairs) {
    const [fg, bg] = p.split(',').map((s) => s.trim());
    row(`${fg} on ${bg}`, ratio(fg, bg));
  }
  process.exit(0);
}

const config = (await import(pathToFileURL(resolve(configPath)).href)).default;
const neon = config?.theme?.extend?.colors?.neon;
if (!neon) {
  console.error(`No theme.extend.colors.neon found in ${configPath}`);
  process.exit(1);
}

const TEXT = {
  white: '#FFFFFF',
  'slate-200': SLATE['slate-200'], 'slate-300': SLATE['slate-300'],
  'slate-400': SLATE['slate-400'], 'slate-500': SLATE['slate-500'],
  'slate-600': SLATE['slate-600'],
  ...Object.fromEntries(Object.entries(neon).map(([k, v]) => [`neon-${k}`, v])),
};
const BG = {
  'page bg (slate-950)': SLATE['slate-950'],
  'surface (slate-900)': SLATE['slate-900'],
  'card (slate-800)': SLATE['slate-800'],
  'raised (slate-700)': SLATE['slate-700'],
};

for (const [bgName, bg] of Object.entries(BG)) {
  console.log(`\n== text on ${bgName} ==`);
  Object.entries(TEXT)
    .map(([name, c]) => [name, ratio(c, bg)])
    .sort((a, b) => b[1] - a[1])
    .forEach(([name, r]) => row(name, r));
}

console.log('\n== dark text (slate-950) on neon fills — the house convention ==');
for (const [name, c] of Object.entries(neon)) row(`neon-${name}`, ratio(SLATE['slate-950'], c));

console.log('\n== white text on neon fills — avoid ==');
for (const [name, c] of Object.entries(neon)) row(`neon-${name}`, ratio('#FFFFFF', c));

console.log('\n== non-text (SC 1.4.11, needs 3.0): neon borders/rings on page bg ==');
for (const [name, c] of Object.entries(neon)) {
  const r = ratio(c, SLATE['slate-950']);
  console.log(`neon-${name}`.padEnd(16) + ` ${r.toFixed(2).padStart(6)}  ${r >= 3 ? 'ok' : 'FAIL'}`);
}
