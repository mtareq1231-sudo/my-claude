# Tile 03: 12-point rosette, quarter tile

One tile holds a quarter of a 12-point rosette, and the rosette's center is the tile's
corner. Lay four tiles 2 × 2, each a mirror image of its neighbour, and the full rosette
appears in the middle.

| File | What it is |
|------|------------|
| `tile-03-quarter.svg` | One tile, colored in the Fez zellige palette. 200 × 200 mm. |
| `tile-03-pattern.svg` | The four tiles laid 2 × 2, colored. 400 × 400 mm. |
| `tile-03-quarter-lines.svg` | One tile as a black line drawing, like the source. |
| `tile-03-pattern-lines.svg` | The 2 × 2 layout as a line drawing. |
| `compare-drawing.jpg` | The source drawing, the traced line drawing and the colored version, side by side. |
| `trace_drawing.py` | Script that builds the four SVGs from the drawing. Run it with `python3 trace_drawing.py DRAWING.png .` (needs numpy and Pillow). |

## Notes

- **Pieces.** Each tile has 23 pieces. Every piece is its own closed path, so you can recolor any piece in Illustrator or Inkscape.
- **Accuracy.** The traced lines match the source drawing to within 1 px (about 0.5 mm at 20 cm) for 99% of their length. Edges are snapped straight, to multiples of 15°. The five-point-star field also uses 36° and 54° edges.
- **Size.** Tiles are set to 20 × 20 cm. The drawings are vector, so you can scale them to any size.
- **Layout.** In the 2 × 2 files, each tile is its own group (`tile-top-left`, `tile-top-right`, …). The tile joints are a separate layer.

## Colors

The colors follow traditional Fez zellige. The white strapwork is the ivory background.

| Piece | Color |
|-------|-------|
| Strapwork (background) | Ivory `#EFE8D6` |
| Central 12-point star, ring of small stars, five-point star | Gold `#C8902C` |
| Petals, slivers around the star, long edge pieces | Black `#1C1B1D` |
| Arrow pieces on the diagonals, small corner pieces | Cobalt `#3F62A8` |
| Other arrow pieces, pentagons, corner square | Turquoise `#2E9A92` |
