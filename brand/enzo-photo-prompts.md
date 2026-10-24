# Photography and product images

The goal is that every product image looks like it was taken by a real food photographer with a real camera, of the real Enzo product. Nobody should be able to say "that's AI".

## The look

- **Hero:** one product, front-on at eye level or slightly low, with the bun leaning toward the camera and fillings visible at the edges.
- **Light:** warm and directional from back-left, with a soft white bounce from the front. Highlights glint on the bun and sauce. Never use cold daylight or flat, even light.
- **Surface:** a worn dark walnut board or a sheet of cream deli paper on a wooden counter.
- **Background:** a blurred warm saloon interior with wood, brick and warm lamps. **Menu images are always cut-outs**, generated on plain parchment `#F3E6CC` and then cut out with no background. Never use pure white or black.
- **Crop:** 1:1 for menu cards and 4:5 for Instagram. Leave 15% clear above the bun for stickers.
- **Honesty:** portion size, bun and fillings must match what the kitchen actually serves. If the photo promises more than arrives, the photo is wrong.

## How to avoid the "AI look"

AI food images give themselves away through things that are too perfect. Ask for, and check for, the imperfections a real camera captures:

| AI tell | What a real photo has |
|---|---|
| A perfectly symmetric, plastic-shiny bun | A slightly uneven bun with crumbs, a flour dusting and one torn edge |
| Melted cheese like liquid gold | Cheese that is partly set, with a few blisters and one thick drip |
| Lettuce that is identical and glossy | Ruffled leaves with torn edges and a slightly wilted spot |
| Sauce placed in perfect drops | Irregular smears, one drip on the board and a fingerprint smudge on the paper |
| Everything in focus | Shallow focus: the front edge is sharp and the back of the bun is soft |
| A glowing, rim-lit halo | Natural falloff, real shadows under the burger and a slight film grain |
| Extra fillings that aren't on the menu | Only the ingredients listed on the menu |
| Garbled text or fake logos | No text and no logos in the image. Stickers and the crest are added afterwards in design |

**Human touch (optional, recommended for social posts):** in one image per category, include a real person's hands, for example two hands holding the burger with fingers pressing into the bun, a sleeve of a black Enzo tee, natural skin texture and short clean nails. Never show a full face in AI images. Use real staff or customers for faces.

## Making the images with Codex CLI

1. **Shoot a phone reference of the real product** in daylight near a window. The AI image must match it, which keeps it honest.
2. Open Codex CLI in a folder for the images and attach the reference: `codex -i reference/the-original.jpg`.
3. Paste the **style block** below, then the product's **subject line**. Ask for **4 variations** at **1024×1024** (menu) or **1024×1280** (Instagram).
4. Pick the most believable one using the checklist in the table above. If it fails one row, regenerate with a fix line, for example "make the bun less shiny, add crumbs".
5. Save the result as `enzo-<item-name>-<1x1|4x5>.webp`, for example `enzo-the-original-1x1.webp`.
6. **Before the menu goes live, replace the hero photos with a real shoot when you can.** Use AI images for the long tail of items.

### Style block (paste first, every time)

```
Real editorial food photograph for a classic American grill house menu.
Shot on a full-frame DSLR, 100mm macro lens, f/4, 1/160s, ISO 200, tripod,
eye-level front view, slight low angle. Warm tungsten key light from back-left,
white bounce card front-right, soft natural shadows, gentle natural falloff.
Surface: worn dark walnut board with a sheet of cream deli paper.
Background: out-of-focus warm diner interior, red and cream tones, hint of brick,
creamy bokeh. Shallow depth of field: front edge tack-sharp, back softly blurred.
Real-world imperfections: slightly uneven brioche bun with crumbs and a light
flour dusting, irregular sauce drips, torn lettuce edges, natural grease sheen,
a few crumbs on the paper. Subtle film grain, true-to-life colours, realistic
portion size. No text, no logos, no watermark, no extra garnish, no props
that are not food. Must look like a real photograph, not CGI or illustration.
```

### Product subject lines


#### Burgers

**THE ORIGINAL** (Single and Double: shoot both, the Double with two patties)

```
Subject: single smashed-edge beef patty, one slice of melted American cheese, crisp green-leaf lettuce, one slice of ripe tomato, thin white onion rings, dill pickle chips, mayo and ketchup visibly dripping. Only these ingredients, nothing else.
```

**GOLDEN CHEESE BURGER** (cheese pull is the hero)

```
Subject: beef patty with a thick, glossy, golden melted cheddar curtain running down the sides, lettuce, tomato, onion, pickles, mayo and ketchup. Only these ingredients, nothing else.
```

**BEEF BACON**

```
Subject: beef patty, crispy rendered beef bacon strips sticking out of the bun, melted cheese, orange-red Texas sauce, dark BBQ sauce, mayo, lettuce, tomato, onion and pickles. Only these ingredients, nothing else.
```

**MUSHROOM ROYAL**

```
Subject: beef patty topped with a heap of sautéed brown button mushrooms, melted white cheese, glossy caramelized onions, Texas sauce, mayo, lettuce, tomato and pickles. Only these ingredients, nothing else.
```

**ENZO PRIME (Signature)** (the flagship: give it the most dramatic, low-angle hero shot)

```
Subject: tall double-stack beef burger with beef bacon, sautéed mushrooms, caramelized onions, melted cheese and stretchy mozzarella, Texas sauce, mayo, lettuce and pickles. Only these ingredients, nothing else.
```

**ENZO BURGER WRAP**

```
Subject: grilled flour tortilla wrap cut in half on a diagonal, showing a cross-section of chopped beef patty, melted mozzarella, Texas sauce, mayo, shredded lettuce and pickles, wrapped in printed cream deli paper. Only these ingredients, nothing else.
```

**DONER KEBAB BURGER**

```
Subject: beef patty topped with thin shaved doner kebab slices with charred edges, melted mozzarella, Texas sauce, mayo, lettuce and pickles. Only these ingredients, nothing else.
```

**DONER KEBAB WRAP**

```
Subject: grilled tortilla wrap cut in half, cross-section showing beef patty, shaved doner kebab, melted mozzarella, Texas sauce, mayo, lettuce and pickles. Only these ingredients, nothing else.
```


#### Chicken

**FIRE ZINGER** (spicy: a few loose jalapeño slices on the board)

```
Subject: craggy, deep-golden crispy fried chicken fillet with visible crunchy flakes, melted cheddar, sriracha sauce drips, mayo, sliced green jalapeños and shredded lettuce. Only these ingredients, nothing else.
```

**RANCH BUTTERMILK**

```
Subject: crispy buttermilk fried chicken fillet, beef bacon strips, creamy white ranch sauce dripping, mayo, pickles and shredded lettuce. Only these ingredients, nothing else.
```

**ALPHA CHICKEN WRAP**

```
Subject: grilled tortilla wrap cut in half showing crispy chicken strips, melted mozzarella and cheddar, Texas sauce, ketchup, mayo, pickles and lettuce. Only these ingredients, nothing else.
```

**SPANISH COOK (Grilled)** (grilled, so no breading anywhere)

```
Subject: grilled chicken breast with real char marks (not fried), beef bacon, melted mozzarella and cheddar, sautéed mushrooms, caramelized onions, Texas sauce and mayo. Only these ingredients, nothing else.
```

**CHICKEN MELTED CHEESE**

```
Subject: crispy fried chicken fillet smothered in melted mozzarella and cheddar, beef bacon, thousand island sauce, mayo, lettuce and pickles. Only these ingredients, nothing else.
```


#### Hot Dogs

**CLASSIC HOT DOG**

```
Subject: long grilled hot dog sausage with grill marks in a soft split-top bun, zigzag of ketchup and yellow mustard, chopped pickles and shredded lettuce. Only these ingredients, nothing else.
```

**MAXI DOG**

```
Subject: hot dog sausage in a bun loaded with melted mozzarella, BBQ sauce, ketchup, sliced black olives, diced fresh onion, peppers and tomatoes. Only these ingredients, nothing else.
```

**MIX CHEESE HOT DOG**

```
Subject: hot dog sausage in a bun with melted mozzarella and a pour of warm cheddar cheese sauce, ketchup, pickles and lettuce. Only these ingredients, nothing else.
```


#### Fries

**FRENCH FRIES (Medium and Large)** (shoot Medium and Large side by side so the size difference is honest)

```
Subject: golden skin-on French fries, lightly salted with visible salt crystals, in a red-and-cream paper cup, a few fries spilling onto the board. Only these ingredients, nothing else.
```


#### Fries Meals

**RANCH FRIES MEAL**

```
Subject: a paper tray of fries loaded with chopped crispy chicken, drizzled ranch sauce and sliced jalapeños. Only these ingredients, nothing else.
```

**CHEDDAR FRIES MEAL**

```
Subject: a paper tray of fries loaded with crispy chicken pieces, warm cheddar cheese sauce and jalapeños. Only these ingredients, nothing else.
```

**FRIES HOT DOG**

```
Subject: a paper tray of fries topped with sliced grilled hot dog sausage, cheddar sauce and jalapeños. Only these ingredients, nothing else.
```


#### Add-ons

**SODA DRINK** (no real soft-drink brands or logos)

```
Subject: an ice-cold unbranded soda in a plain red-and-cream paper cup with condensation droplets and a straw. Only these ingredients, nothing else.
```

**EXTRA SAUCES** (overhead flat-lay, 3:2)

```
Subject: seven small paper sauce cups in a row, overhead: orange-red Texas sauce, dark BBQ, white ranch, yellow cheddar sauce, red sriracha, pink thousand island and white mayo. Only these ingredients, nothing else.
```


### Variants

- **Cut-out for the menu (default):** add `Plain seamless parchment background (#F3E6CC), no props, no shadow on the background, sharp clean edges all around the food, so it can be cut out cleanly.`
- **Hand-held:** add `Two real human hands holding it toward the camera, fingers gently pressing the bun, black t-shirt sleeve visible, natural skin texture, face not visible.`
- **Instagram 4:5:** add `Vertical 4:5 framing, 15% empty space above the food for text.`
- **Texas chapter:** add `Warm sunset-rust rim light, a coil of rope and a small cast-iron skillet blurred in the background.`

## Cut-outs and the floor shadow

- Every product on the online menu is a **cut-out with no background**. Generate it on plain parchment, remove the background and save a transparent WebP.
- Clean the edge: no soft halo, no leftover shadow baked into the cut-out.
- Add **one oval floor shadow underneath the sandwich** in the layout. It is an ellipse about 80% of the sandwich width and 16px tall, using a radial gradient from `floor` to transparent, sitting just under the bottom bun.
- Never use `drop-shadow` around the whole outline. It makes the sandwich look like it is floating.
- Cleaned versions of the current cut-outs are `beef-burger-cutout-clean.webp` and `chicken-burger-cutout-clean.webp`.

## Current images in this system

The photos under `assets/Photography/` were extracted from the print menu and flyer. They are placeholders: they are AI-generated, show the "too perfect" tells above, and should be replaced using this kit.

## Stickers and badges

- Stickers are small wooden planks or brass-edged tags in `green` or `red`, with Rye text. Examples: "100% Fresh Beef" and "Crispy Chicken".
- The round stamp ("Every sandwich with fries") is a `radius-round` disc in `red` with a dashed `on-red` ring, like a sheriff's seal.
- Use at most two stickers per image. Add them in design, never in the AI prompt.

## Patterns

- **Checkerboard:** 16px `green` squares on `surface-100`, as one 16px-high strip under the poster and above the footer. Never use it as a full background.
- **Star rule:** ★ ── ★ ── ★ in `gold`.
- **Five-star row** from the crest: use it under headlines.
