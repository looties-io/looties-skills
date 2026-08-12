#!/usr/bin/env node
// WCAG 2.x contrast calculator for a Tailwind palette.
//
// Ad-hoc mode works anywhere, with no config and no project:
//
//   node scripts/contrast.mjs --pair '#94A3B8,#334155' [--pair …]
//
// Sweep mode reads your Tailwind config and grades every brand color against a set of
// surface colors, in the four combinations that actually matter: text on surfaces,
// dark text on brand fills, white text on brand fills, and brand borders/rings on the
// page background (non-text, SC 1.4.11).
//
//   node scripts/contrast.mjs
//   node scripts/contrast.mjs --config path/to/tailwind.config.js
//   node scripts/contrast.mjs --palette brand          # a single group under theme.extend.colors
//   node scripts/contrast.mjs --surfaces '#020617,#0F172A,#1E293B'
//
// By default it sweeps every flat color group under theme.extend.colors, and grades
// against the Tailwind slate scale as a stand-in dark surface ladder. Pass --surfaces
// with your own values (darkest first) if your app is light-themed or uses custom
// surfaces; the first surface is treated as the page background.
//
// AA: >=4.5 normal text, >=3.0 large text (>=24px, or >=18.66px bold) and non-text UI.
// AAA: >=7.0 / >=4.5.

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
const row = (name, r) => console.log(`${name.padEnd(20)} ${r.toFixed(2).padStart(6)}  ${grade(r)}`);
const isHex = (v) => typeof v === 'string' && /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(v);

// Tailwind's default slate scale, used as a neutral stand-in when --surfaces is absent.
const SLATE = {
  'slate-200': '#E2E8F0', 'slate-300': '#CBD5E1', 'slate-400': '#94A3B8',
  'slate-500': '#64748B', 'slate-600': '#475569', 'slate-700': '#334155',
  'slate-800': '#1E293B', 'slate-900': '#0F172A', 'slate-950': '#020617',
};

const args = process.argv.slice(2);
const pairs = [];
let configPath = './tailwind.config.js';
let paletteKey = null;
let surfaceArg = null;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--pair') pairs.push(args[++i]);
  else if (args[i] === '--config') configPath = args[++i];
  else if (args[i] === '--palette') paletteKey = args[++i];
  else if (args[i] === '--surfaces') surfaceArg = args[++i];
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
const groups = config?.theme?.extend?.colors ?? {};

// Collect brand colors as `group-shade` pairs, keeping only flat hex maps. A palette
// key narrows the sweep to one group; without it, every eligible group is included.
const brand = {};
for (const [group, value] of Object.entries(groups)) {
  if (paletteKey && group !== paletteKey) continue;
  if (isHex(value)) { brand[group] = value; continue; }
  if (value && typeof value === 'object') {
    for (const [shade, c] of Object.entries(value)) {
      if (isHex(c)) brand[`${group}-${shade}`] = c;
    }
  }
}

if (Object.keys(brand).length === 0) {
  console.error(
    `No hex colors found under theme.extend.colors${paletteKey ? `.${paletteKey}` : ''} in ${configPath}.\n` +
      `Use --palette <key> to name a group, or --pair '#fg,#bg' to grade colors directly.`,
  );
  process.exit(1);
}

const surfaces = surfaceArg
  ? Object.fromEntries(surfaceArg.split(',').map((s, i) => [i === 0 ? `page bg (${s.trim()})` : s.trim(), s.trim()]))
  : {
      'page bg (slate-950)': SLATE['slate-950'],
      'surface (slate-900)': SLATE['slate-900'],
      'card (slate-800)': SLATE['slate-800'],
      'raised (slate-700)': SLATE['slate-700'],
    };
const pageBg = Object.values(surfaces)[0];
const darkest = surfaceArg ? pageBg : SLATE['slate-950'];

const TEXT = {
  white: '#FFFFFF',
  'slate-200': SLATE['slate-200'], 'slate-300': SLATE['slate-300'],
  'slate-400': SLATE['slate-400'], 'slate-500': SLATE['slate-500'],
  'slate-600': SLATE['slate-600'],
  ...brand,
};

for (const [bgName, bg] of Object.entries(surfaces)) {
  console.log(`\n== text on ${bgName} ==`);
  Object.entries(TEXT)
    .map(([name, c]) => [name, ratio(c, bg)])
    .sort((a, b) => b[1] - a[1])
    .forEach(([name, r]) => row(name, r));
}

console.log(`\n== dark text (${darkest}) on brand fills ==`);
for (const [name, c] of Object.entries(brand)) row(name, ratio(darkest, c));

console.log('\n== white text on brand fills ==');
for (const [name, c] of Object.entries(brand)) row(name, ratio('#FFFFFF', c));

console.log('\n== non-text (SC 1.4.11, needs 3.0): brand borders/rings on page bg ==');
for (const [name, c] of Object.entries(brand)) {
  const r = ratio(c, pageBg);
  console.log(name.padEnd(20) + ` ${r.toFixed(2).padStart(6)}  ${r >= 3 ? 'ok' : 'FAIL'}`);
}
