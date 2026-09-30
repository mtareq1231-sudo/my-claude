#!/usr/bin/env node
// Build an RTL Arabic slide deck (1280×720 pages) from decks/<name>/content.mjs
// into decks/<name>/deck.html and decks/<name>/<name>.pdf.
//
//   node scripts/build-deck.mjs decks/hektar-sea-view [--png]
//
// Layout rules that keep Arabic tables aligned:
// - the whole document is dir="rtl", so the first column (the label) sits on the right;
// - every number run is isolated as an LTR span, so "18–24", "(6,835,257)" and
//   "1.68×" never get reordered by the bidi algorithm;
// - tables use fixed column widths and tabular figures so values line up row to row.

import { pathToFileURL } from 'node:url';
import { writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { chromium } from 'playwright';

const args = process.argv.slice(2);
const deckDir = path.resolve(args.find((a) => !a.startsWith('--')) ?? 'decks/hektar-sea-view');
const wantPng = args.includes('--png');
const name = path.basename(deckDir);
const { default: deck } = await import(pathToFileURL(path.join(deckDir, 'content.mjs')).href);

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// Wrap numeric runs (incl. ranges, parens for negatives, %, ×) in isolated LTR spans.
const NUM = /\(\d[\d,.]*\)|\d[\d,.]*(?:\s?[–-]\s?\d[\d,.]*)?[%×]?/g;
const fmt = (s) => esc(s).replace(NUM, (m) => `<span class="n" dir="ltr">${m}</span>`);

const pad = (n) => String(n).padStart(2, '0');

function table(b) {
  const cols = b.head.length;
  const widths = b.widths ?? (cols === 2 ? [58, 42] : Array(cols).fill(100 / cols));
  const rows = b.rows.map((r) => (Array.isArray(r) ? { cells: r } : r));
  return `
  <table class="t${b.compact ? ' compact' : ''}">
    ${b.caption ? `<caption>${fmt(b.caption)}</caption>` : ''}
    <colgroup>${widths.map((w) => `<col style="width:${w}%">`).join('')}</colgroup>
    <thead><tr>${b.head.map((h) => `<th>${fmt(h)}</th>`).join('')}</tr></thead>
    <tbody>${rows
      .map(
        (r) =>
          `<tr class="${r.total ? 'total' : r.sub ? 'sub' : ''}">${r.cells
            .map((c, i) => `<td class="${i === 0 ? 'label' : 'val'}">${fmt(c)}</td>`)
            .join('')}</tr>`,
      )
      .join('')}</tbody>
  </table>`;
}

function block(b) {
  switch (b.type) {
    case 'table':
      return table(b);
    case 'text':
      return `<div class="text">${b.paras.map((p) => `<p>${fmt(p)}</p>`).join('')}</div>`;
    case 'h3':
      return `<h3>${fmt(b.text)}</h3>`;
    case 'note':
      return `<p class="note">${fmt(b.text)}</p>`;
    case 'list':
      return `<ul class="list">${b.items.map((i) => `<li>${fmt(i)}</li>`).join('')}</ul>`;
    case 'stats':
      return `<div class="stats${b.column ? ' column' : ''}">${b.items
        .map((s) => `<div class="stat"><div class="sv">${fmt(s.value)}</div><div class="sl">${fmt(s.label)}</div></div>`)
        .join('')}</div>`;
    case 'card':
      return `<div class="card"><div class="ct">${fmt(b.title)}</div>${
        b.big ? `<div class="cb">${fmt(b.big)}</div>` : ''
      }${b.text && !b.big ? `<p>${fmt(b.text)}</p>` : ''}</div>`;
    case 'bar':
      return `<div class="bar">${b.segments
        .map((s, i) => `<div class="seg s${i}" style="flex:${s.value}"><span class="n" dir="ltr">${s.value.toFixed(2)}%</span></div>`)
        .join('')}</div><div class="legend">${b.segments
        .map((s, i) => `<span><i class="s${i}"></i>${fmt(s.label)}</span>`)
        .join('')}</div>`;
    case 'split-bar':
      return `<div class="splitbar">${b.caption ? `<div class="sb-cap">${fmt(b.caption)}</div>` : ''}<div class="bar">${b.parts
        .map((p, i) => `<div class="seg s${i}" style="flex:${p.value}"><span>${fmt(p.label)}</span><span class="n" dir="ltr">${p.value}%</span></div>`)
        .join('')}</div></div>`;
    default:
      throw new Error(`unknown block type: ${b.type}`);
  }
}

const logoMark = `<div class="mark"><img src="../assets/osool-logo.png" alt=""></div>`;

function cover(c) {
  const media = c.image
    ? `<img class="cover-img" src="${esc(c.image)}" alt="">`
    : `<div class="cover-ph"><img src="../assets/osool-logo.png" alt=""></div>`;
  return `
  <section class="page cover">
    <div class="cover-text">
      <img class="cover-logo" src="../assets/osool-logo.png" alt="أصول">
      <div class="rule"></div>
      <div class="eyebrow">${fmt(c.eyebrow)}</div>
      <h1 class="name" dir="ltr">${esc(c.name)}</h1>
      <div class="subtitle">${fmt(c.subtitle)}</div>
      <p class="lead">${fmt(c.lead)}</p>
      <div class="meta">${c.meta.map(fmt).join('<span class="sep">|</span>')}</div>
    </div>
    <div class="cover-media">${media}</div>
  </section>`;
}

function slide(s, n) {
  const body =
    s.layout === 'split'
      ? `<div class="split" style="grid-template-columns:${s.ratio ?? '1fr 1fr'}">
           <div class="col">${s.right.map(block).join('')}</div>
           <div class="col">${s.left.map(block).join('')}</div>
         </div>`
      : `<div class="stack">${s.blocks.map(block).join('')}</div>`;
  return `
  <section class="page">
    <header>
      <div class="eyebrow">${fmt(s.eyebrow)}</div>
      <h2>${fmt(s.title)}</h2>
    </header>
    <main>${body}</main>
    <footer>${logoMark}<span class="n pg" dir="ltr">${pad(n)}</span></footer>
  </section>`;
}

const html = `<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>${esc(deck.title)}</title>
<link rel="stylesheet" href="../assets/fonts.css">
<link rel="stylesheet" href="../assets/deck.css">
</head>
<body>
${cover(deck.cover)}
${deck.slides.map((s, i) => slide(s, i + 2)).join('\n')}
</body>
</html>`;

const htmlPath = path.join(deckDir, 'deck.html');
await writeFile(htmlPath, html);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);

// Fail loudly if any slide's content overflows its page.
const overflow = await page.evaluate(() =>
  [...document.querySelectorAll('.page')]
    .map((p, i) => {
      const m = p.querySelector('main');
      if (!m) return null;
      return m.scrollHeight > m.clientHeight + 1 || m.scrollWidth > m.clientWidth + 1 ? i + 1 : null;
    })
    .filter(Boolean),
);
if (overflow.length) console.warn(`WARNING: content overflows on page(s): ${overflow.join(', ')}`);

const pdfPath = path.join(deckDir, `${name}.pdf`);
await page.pdf({ path: pdfPath, width: '1280px', height: '720px', printBackground: true, preferCSSPageSize: true });

if (wantPng) {
  const outDir = path.join(deckDir, 'preview');
  await mkdir(outDir, { recursive: true });
  const pages = await page.$$('.page');
  for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: path.join(outDir, `p${pad(i + 1)}.png`) });
}
await browser.close();
console.log(`wrote ${path.relative(process.cwd(), pdfPath)} (${deck.slides.length + 1} pages)`);
