# Tile 01: quatrefoil with clovers

A vector version of the physical 20×20 cm cement tile (dark-brown quatrefoil,
terracotta clovers and grey acanthus corners).

| File | What it is |
|------|------------|
| `tile-01-single.svg` | One tile, 200 × 200 mm. This is what you print or cut a stencil from. |
| `tile-01-4up.svg` | Four tiles laid 2×2. The full rosette appears here. |
| `generate.py` | Script that builds both SVGs. Edit the numbers and run `python3 generate.py`. |

A single tile holds one quarter of the rosette. The 2×2 layout uses the same
tile four times, each turned 90° from the last.

## Opening in Illustrator / Inkscape

Each colour sits on its own group: `background`, `grey`, `dark-brown` and
`terracotta`. That matches the separate colour moulds used for cement tiles.
In Illustrator, use **Object → Clipping Mask → Release** to get the parts that
run past the tile edge. To get merged shapes, use **Pathfinder → Unite** on each
colour group.

## Colours

| Name | Hex |
|------|-----|
| Background | `#F1F0EB` |
| Dark brown | `#3B2A26` |
| Terracotta | `#B5573F` |
| Grey | `#BEBDBA` |
