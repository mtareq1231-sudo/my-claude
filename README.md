# my-claude — PDF pipeline

Batch PDF → Markdown conversion built on
[`@firecrawl/pdf-inspector`](https://github.com/firecrawl/pdf-inspector), a Rust
library (native Node binding) that classifies a PDF as text-based or scanned and
extracts clean Markdown **without OCR** — typically single-digit milliseconds per
document.

## Setup

```bash
npm install
```

That's it — the native binary for your platform is installed automatically (Linux
x64/arm64, macOS arm64, Windows x64). No Rust toolchain, no Python, no ML models,
no API keys, no network calls at runtime.

Verify the install against the bundled sample:

```bash
npm run inspect samples
```

## Usage

Drop PDFs into `pdfs/` and run:

```bash
npm run inspect                       # every PDF in pdfs/ → out/*.md
npm run inspect -- path/to/file.pdf   # specific files
npm run inspect -- some/dir another/  # directories, searched recursively
npm run classify                      # detect type only, no extraction
```

Each run writes:

- `out/<name>.md` — the extracted Markdown, one file per PDF
- `out/report.json` — classification and metadata for every file processed

Console output is one line per PDF:

```
TextBased     1p  129 chars      pdfs/sample.pdf
Scanned      14p  0 chars        [ocr:14p] pdfs/contract-scan.pdf
TextBased    32p  84210 chars    [tables columns] pdfs/annual-report.pdf
```

### Options

| Flag | Meaning |
| --- | --- |
| `-o, --out <dir>` | output directory (default `out`) |
| `-c, --classify-only` | detect PDF type only, skip Markdown extraction |
| `-p, --pages <spec>` | limit extraction to pages, 1-indexed: `1,3-5` |
| `-j, --concurrency <n>` | files processed in parallel (default 4) |
| `-q, --quiet` | print only the summary line |
| `-h, --help` | show help |

Pass flags after `--` when going through npm: `npm run inspect -- --pages 1-3`.
Exit code is `1` if any file failed, `2` for bad arguments.

## Reading the report

`out/report.json` carries the fields worth acting on:

- `pdfType` — `TextBased`, `Scanned`, `ImageBased`, or `Mixed`
- `pagesNeedingOcr` — 1-indexed pages whose text is missing or untrustworthy
- `ocrReasonsByPage` — why a page needs OCR (empty text, GID fonts, encoding issues)
- `pagesWithTables` / `pagesWithColumns` / `isComplexLayout` — layout warnings
- `confidence`, `pageCount`, `processingTimeMs`

The practical workflow: run everything through this first, take the Markdown for
whatever comes back `TextBased`, and only send files with a non-empty
`pagesNeedingOcr` to an OCR service. That's the point of the tool — it keeps the
expensive path for the documents that actually need it.

Find every file that needs OCR:

```bash
node -e "const r=require('./out/report.json');r.results.filter(x=>x.pagesNeedingOcr?.length).forEach(x=>console.log(x.file,x.pagesNeedingOcr))"
```

## Layout

```
pdfs/            drop PDFs here (contents git-ignored — data, not code)
samples/         tiny text-based PDF for verifying the setup
scripts/         inspect.mjs — the batch CLI
out/             generated Markdown + report.json (git-ignored)
```

## Beyond the batch script

`@firecrawl/pdf-inspector` exposes more than this script uses — positioned text
extraction with fonts and coordinates (`extractTextWithPositions`), per-page
Markdown (`extractPagesMarkdown`), region-scoped text and table extraction for
hybrid OCR pipelines (`extractTextInRegions`, `extractTablesInRegions`), and
tagged-PDF structure elements (`extractStructureElements`). See
`node_modules/@firecrawl/pdf-inspector/index.d.ts` for the full typed API.
