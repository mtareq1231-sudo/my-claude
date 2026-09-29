# Noureen (نورين) — board presentation redesign

## `deck/index.html` — the presentation
A single self-contained HTML file (42 slides, A4 landscape 842 × 595) built on the
**إذاعة نورين** design system: its colour tokens, header/footer geometry, section colours,
supergraphic rules and the real vector logo.

Open it in a browser:

| Key | Action |
| --- | --- |
| ← / Space / Enter | next slide (RTL) |
| → / Backspace | previous slide |
| G | overview of all slides (click one to jump) |
| E | edit mode: click any text and type |
| Save button | download a copy of the HTML that includes your edits |
| P | export to PDF (one slide per A4-landscape page) |
| F | full screen |

Content slides get their header and footer from two attributes, so changing a section
name or icon is a one-word edit: `data-section="المحتوى البرامجي" data-icon="i-mic"`.
The icons are the `<symbol id="i-…">` entries at the end of the file.

Budget amounts are left as dashed `—` fields because the source deck has no figures.
Fill them in with edit mode.

## `assets/logo/` — vector logo
Horizontal, stacked, symbol and wordmark versions, each in primary, reversed, teal and white.

## `source/`
- `content.md` — all the text from the original PDF
- `slides/` — renders of the original 45 slides, for reference
- `brand/tokens.json` — the palette sampled from the PDF

## Fonts
Thmanyah Sans is licensed for embedding but can't be hosted, so the deck uses it when it
is installed and falls back to Tajawal otherwise. The basmala uses Amiri Quran.
