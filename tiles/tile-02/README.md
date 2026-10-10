# Tile 02: zellige 12-point rosette, 50 × 50 cm

This is a vector version of the green and white zellige panel. It has a 12-point star
at the center, a ring of petals around it, and eight five-point stars further out. The
square border cuts off the rest of the pattern.

| File | What it is |
|------|------------|
| `tile-02.svg` | The full panel at 500 × 500 mm, with green pieces, grout and white strips. |
| `tile-02-cut-lines.svg` | Outlines only: one closed path per green piece plus the panel edge. Use it for cutting, stencils or a CNC/laser setup. |
| `compare-photo.jpg` | The straightened photo on the left and the SVG on the right. |
| `trace_photo.py` | Script that builds both SVGs from the photo. Run it with `python3 trace_photo.py PHOTO.jpg .` (needs numpy and Pillow). |

## What's in it

- **73 green pieces.** In the rosette there is 1 central star, 12 slivers, 12 petals and 12 arrow pieces. Around it there are 8 five-point stars, 4 hexagons, 4 corner pieces, 16 pieces cut by the panel edges, and 4 kite pieces near the middle of each side.
- **Exact symmetry.** Each kind of piece is traced once and then copied into place. The rosette has 12-fold symmetry and the whole square has 4-fold mirror symmetry. Every edge runs at a multiple of 15°, as in the real design.
- **The central star is constructed**, not traced. It has 12 right-angled points, a tip radius of 43 mm and valleys at 35 mm.
- **Accuracy.** Compared with the photo, the outlines agree to about 1–2 mm on most edges.

## Layers (Illustrator / Inkscape)

- `white-strips`: the beige background, which forms the white strapwork.
- `grout`: a 2.5 mm light grout border around every green piece.
- `green-pieces`: the green pieces.

The white strips are one shape. The SVG doesn't divide them into separate strip pieces,
and it doesn't draw the over/under joints where two strips cross. That is why the white
looks less "woven" than in the photo.

## Colors

| Name | Hex |
|------|-----|
| Green glaze | `#2A6650` |
| White strip (beige) | `#DCCDC9` |
| Grout | `#F3EDE9` |
