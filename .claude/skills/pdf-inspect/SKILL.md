---
name: pdf-inspect
description: Convert PDFs to Markdown and classify them as text-based vs scanned using the local pdf-inspector pipeline in this repo. Use whenever the user provides PDF files (one or many) and wants text extracted, wants to know which files are scanned or need OCR, or invokes /pdf-inspect. Handles batches — point it at files or directories.
---

# PDF inspect

Runs this repo's batch pipeline (`scripts/inspect.mjs`, built on
`@firecrawl/pdf-inspector`) to classify PDFs and extract clean Markdown without
OCR.

## Steps

1. **Make sure deps are installed.** If `node_modules/@firecrawl` is missing,
   run `npm install` from the repo root first. It pulls a prebuilt native
   binary — no Rust toolchain needed.

2. **Get the PDFs to a path.** Files the user attached or uploaded need to be on
   disk. Put loose files in `pdfs/` (its contents are git-ignored). If they gave
   a directory, use it directly.

3. **Run it.**

   ```bash
   node scripts/inspect.mjs                    # everything in pdfs/
   node scripts/inspect.mjs path/a.pdf dir/    # specific files or directories
   node scripts/inspect.mjs --classify-only    # type detection only, no extraction
   ```

   Useful flags: `--out <dir>` (default `out`), `--pages 1,3-5` (1-indexed),
   `--concurrency <n>` (default 4), `--quiet`.

   Exit code 1 means at least one file failed; 2 means bad arguments. A single
   corrupt file fails only itself — the rest of the batch still processes.

4. **Read the results.**
   - `out/<name>.md` — extracted Markdown, one per PDF
   - `out/report.json` — per-file classification

   In the report, the fields that drive decisions are `pdfType` (`TextBased`,
   `Scanned`, `ImageBased`, `Mixed`), `pagesNeedingOcr` (1-indexed pages whose
   text is missing or untrustworthy), `ocrReasonsByPage`, and the layout flags
   `pagesWithTables` / `pagesWithColumns` / `isComplexLayout`.

5. **Report back to the user** with what came through cleanly and which files
   need OCR. Anything with a non-empty `pagesNeedingOcr` is a scan — this tool
   cannot read it, and it needs an OCR service. Do not present empty Markdown
   from a scanned PDF as if extraction succeeded.

## Notes

- Everything runs locally: no API keys, no network calls, no ML models.
- Extraction is fast (single-digit ms for typical text PDFs), so just run the
  whole batch rather than sampling.
- For anything the batch script doesn't cover — positioned text with fonts and
  coordinates, per-page Markdown, region-scoped table extraction, tagged-PDF
  structure elements — the full typed API is in
  `node_modules/@firecrawl/pdf-inspector/index.d.ts`.
