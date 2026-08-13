#!/usr/bin/env node
// Batch PDF -> Markdown converter built on @firecrawl/pdf-inspector.
//
//   node scripts/inspect.mjs                  # process every PDF in pdfs/
//   node scripts/inspect.mjs a.pdf some/dir   # process specific files/dirs
//   node scripts/inspect.mjs --classify-only  # detect type only, no markdown
//
// See README.md for the full flag list.

import { readFile, writeFile, mkdir, readdir, stat } from 'node:fs/promises';
import { basename, extname, join, relative, resolve } from 'node:path';
import { classifyPdfAsync, processPdfAsync } from '@firecrawl/pdf-inspector';

const DEFAULT_INPUT = 'pdfs';
const DEFAULT_OUT = 'out';

function parseArgs(argv) {
  const opts = {
    inputs: [],
    out: DEFAULT_OUT,
    classifyOnly: false,
    pages: null,
    concurrency: 4,
    quiet: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case '--out':
      case '-o':
        opts.out = argv[++i];
        break;
      case '--classify-only':
      case '-c':
        opts.classifyOnly = true;
        break;
      case '--pages':
      case '-p':
        opts.pages = parsePages(argv[++i]);
        break;
      case '--concurrency':
      case '-j':
        opts.concurrency = Math.max(1, Number(argv[++i]) || 1);
        break;
      case '--quiet':
      case '-q':
        opts.quiet = true;
        break;
      case '--help':
      case '-h':
        opts.help = true;
        break;
      default:
        if (arg.startsWith('-')) {
          throw new Error(`unknown flag: ${arg}`);
        }
        opts.inputs.push(arg);
    }
  }

  if (opts.inputs.length === 0) opts.inputs.push(DEFAULT_INPUT);
  return opts;
}

// "1,3-5" -> [0, 2, 3, 4]  (the library takes 0-indexed pages)
function parsePages(spec) {
  if (!spec) throw new Error('--pages needs a value, e.g. 1,3-5');
  const pages = [];
  for (const part of spec.split(',')) {
    const range = part.trim().match(/^(\d+)\s*-\s*(\d+)$/);
    if (range) {
      const [from, to] = [Number(range[1]), Number(range[2])];
      if (from < 1 || to < from) throw new Error(`bad page range: ${part}`);
      for (let p = from; p <= to; p++) pages.push(p - 1);
    } else {
      const p = Number(part.trim());
      if (!Number.isInteger(p) || p < 1) throw new Error(`bad page number: ${part}`);
      pages.push(p - 1);
    }
  }
  return pages;
}

async function collectPdfs(inputs) {
  const found = [];

  const walk = async (path) => {
    let info;
    try {
      info = await stat(path);
    } catch {
      throw new Error(`no such file or directory: ${path}`);
    }
    if (info.isDirectory()) {
      for (const entry of await readdir(path, { withFileTypes: true })) {
        if (entry.name.startsWith('.')) continue;
        await walk(join(path, entry.name));
      }
    } else if (extname(path).toLowerCase() === '.pdf') {
      found.push(path);
    }
  };

  for (const input of inputs) await walk(input);
  return [...new Set(found)].sort();
}

// Keep output names unique when two input dirs hold the same filename.
function outputNames(files) {
  const names = new Map();
  const taken = new Set();
  for (const file of files) {
    const stem = basename(file, extname(file));
    let name = stem;
    for (let n = 2; taken.has(name); n++) name = `${stem}-${n}`;
    taken.add(name);
    names.set(file, name);
  }
  return names;
}

async function mapWithConcurrency(items, limit, fn) {
  const results = new Array(items.length);
  let next = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (true) {
      const i = next++;
      if (i >= items.length) return;
      results[i] = await fn(items[i], i);
    }
  });
  await Promise.all(workers);
  return results;
}

async function inspectOne(file, { classifyOnly, pages, out, name }) {
  const started = Date.now();
  const buffer = await readFile(file);

  if (classifyOnly) {
    const c = await classifyPdfAsync(buffer);
    return {
      file,
      ok: true,
      pdfType: c.pdfType,
      pageCount: c.pageCount,
      confidence: c.confidence,
      pagesNeedingOcr: c.pagesNeedingOcr.map((p) => p + 1), // classify is 0-indexed
      elapsedMs: Date.now() - started,
    };
  }

  const r = await processPdfAsync(buffer, pages);
  const markdownPath = join(out, `${name}.md`);
  await writeFile(markdownPath, r.markdown ?? '');

  return {
    file,
    ok: true,
    markdown: markdownPath,
    title: r.title,
    pdfType: r.pdfType,
    pageCount: r.pageCount,
    confidence: r.confidence,
    chars: (r.markdown ?? '').length,
    pagesNeedingOcr: r.pagesNeedingOcr, // processPdf is already 1-indexed
    ocrReasonsByPage: r.ocrReasonsByPage,
    pagesWithTables: r.pagesWithTables,
    pagesWithColumns: r.pagesWithColumns,
    isComplexLayout: r.isComplexLayout,
    hasEncodingIssues: r.hasEncodingIssues,
    processingTimeMs: r.processingTimeMs,
    elapsedMs: Date.now() - started,
  };
}

const HELP = `Usage: node scripts/inspect.mjs [files-or-dirs...] [options]

Converts every PDF it finds to Markdown in out/, and writes out/report.json
with the classification of each file. Defaults to reading pdfs/.

Options:
  -o, --out <dir>        output directory (default: ${DEFAULT_OUT})
  -c, --classify-only    detect PDF type only, skip markdown extraction
  -p, --pages <spec>     limit extraction to pages, 1-indexed, e.g. 1,3-5
  -j, --concurrency <n>  files processed in parallel (default: 4)
  -q, --quiet            only print the summary line
  -h, --help             show this help

Exit code is 1 if any file failed to process.`;

async function main() {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (err) {
    console.error(`error: ${err.message}\n\n${HELP}`);
    process.exit(2);
  }

  if (opts.help) {
    console.log(HELP);
    return;
  }

  let files;
  try {
    files = await collectPdfs(opts.inputs);
  } catch (err) {
    console.error(`error: ${err.message}`);
    process.exit(2);
  }

  if (files.length === 0) {
    console.error(`No PDFs found in: ${opts.inputs.join(', ')}`);
    console.error(`Drop files into ${DEFAULT_INPUT}/ or pass paths explicitly.`);
    process.exit(1);
  }

  await mkdir(opts.out, { recursive: true });
  const names = outputNames(files);

  const results = await mapWithConcurrency(files, opts.concurrency, async (file) => {
    try {
      const result = await inspectOne(file, { ...opts, name: names.get(file) });
      if (!opts.quiet) console.log(formatRow(result));
      return result;
    } catch (err) {
      const failure = { file, ok: false, error: err.message };
      console.error(`FAIL  ${relative(process.cwd(), file)} — ${err.message}`);
      return failure;
    }
  });

  const failed = results.filter((r) => !r.ok);
  const report = {
    generatedAt: new Date().toISOString(),
    inputs: opts.inputs.map((i) => resolve(i)),
    classifyOnly: opts.classifyOnly,
    total: results.length,
    failed: failed.length,
    needsOcr: results.filter((r) => r.ok && r.pagesNeedingOcr?.length > 0).length,
    results,
  };
  const reportPath = join(opts.out, 'report.json');
  await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);

  console.log(
    `\n${results.length - failed.length}/${results.length} processed` +
      `${failed.length ? `, ${failed.length} failed` : ''}` +
      ` — report: ${reportPath}`,
  );

  if (failed.length) process.exit(1);
}

function formatRow(r) {
  const flags = [];
  if (r.pagesNeedingOcr?.length) flags.push(`ocr:${r.pagesNeedingOcr.length}p`);
  if (r.pagesWithTables?.length) flags.push('tables');
  if (r.pagesWithColumns?.length) flags.push('columns');
  if (r.hasEncodingIssues) flags.push('encoding-issues');

  const name = relative(process.cwd(), r.file);
  const size = r.chars != null ? `${r.chars} chars` : 'classified';
  return `${r.pdfType.padEnd(10)} ${String(r.pageCount).padStart(4)}p  ${size.padEnd(14)} ${
    flags.length ? `[${flags.join(' ')}] ` : ''
  }${name}`;
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
