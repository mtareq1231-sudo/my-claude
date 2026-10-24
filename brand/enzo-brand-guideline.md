Enzo Grill House is a Western-style American grill house in Cairo (Cairo Capital Hub, El Mokattam). It serves burgers, crispy chicken and hot dogs, and every sandwich comes with fries.

**Version 2 (approved style): Western saloon in red and green.** Think of a saloon bill of fare: parchment paper, wooden plank signs, a wanted-poster header and a cowboy display face. The colours are ranch green and chili red, with a diner checkerboard and square price chips.

The **Journey** stays: Chef Enzo travels across America, and each stop is a limited-time *chapter*. **Stop 01 is Texas.** See *Journey chapters*.

## Brand essence

| | |
|---|---|
| **Promise** | More than a sandwich. Every sandwich comes with fries. |
| **Personality** | A warm, rowdy saloon cook: generous, playful and proud of the food. Never fine-dining, never cold. |
| **Audience** | Students, young families, Capital Hub office workers and late-night eaters. |
| **Mascot** | Chef Enzo: cowboy hat, red bandana, the narrator of the Journey. |
| **Signature line** | "Wanted: big appetites" / «مطلوب: ناس جعانة» on the poster header. |

Tagline: **More than a sandwich.** / **أكتر من ساندوتش.**

## Logo

- **Master logo:** the Grill House crest (`assets/Logos/enzo-crest.webp`). Its maroon, cream and cowboy illustration already fits the Western look.
- **Chapter badge:** Enzo Texas (`assets/Logos/enzo-texas-badge.webp`). Use it only in the chapter ticket and on Texas promo material, cropped into the round medallion (`radius-round`) with a 3px `red` ring.
- Place the crest on `surface-100`, `surface-200` or `green`. Keep clear space equal to the height of the "E" in ENZO. The minimum width is 72px on screen and 20mm in print.
- Don't recolour, stretch or outline the crest, or add a shadow behind it.
- **Still needed:** a vector (SVG) crest and a one-colour version for stamps, bags and cups.

## Colour

Two brand colours, ranch green and chili red, on parchment. Gold is only brass hardware.

- `green` is for structure: plank section signs, the category strap, the footer, the poster frame and the checkerboard. Put `on-green` text on it.
- `red` is for action and price: Single chips, the Double chip outline, the active tab, primary buttons and the top strip. Put `on-red` text on it. Use `red-text` for red words on parchment.
- `gold` is used only for nails, ★ stars and plank kickers. It is never a fill behind words, except on the one gold footer button.
- `surface-100` is the parchment page and `surface-200` the poster panel. `ink` is for names and text, `ink-muted` for italic ingredients and `rope` for dashed dividers.
- `green-text` is for small green words on parchment, such as "With fries" and Grilled.
- Proportion: about 60% parchment, 20% green, 15% red and at most 5% gold.
- Dark mode is a night-time saloon: warm brown-black parchment, a slightly lighter green and red, and cream text. It is never pure black.

## Typography

| Role | Family | Use |
|---|---|---|
| Display | **Rye** | Poster headline, plank titles and the chapter ticket. Title case only, never uppercase, never below 22px. |
| Menu | **Zilla Slab** 500/700 | Item names (uppercase), chip numbers and labels, tabs, eyebrows. |
| Body | **Lora** 400 *italic* | Ingredient lines in italic, plus running text. |
| Arabic display | **Reem Kufi** 700 | Arabic poster headline, plank titles and the chapter ticket. |
| Arabic body | **Tajawal** 500/800 | Arabic names (800) and ingredients (500, upright). |

- Load from Google Fonts: `Rye`, `Zilla+Slab:wght@500;700`, `Lora:ital,wght@0,400;0,500;1,400`, `Reem+Kufi:wght@500;700` and `Tajawal:wght@500;800`.
- Prices use Western digits (160, 260) in both languages, with tabular figures.
- Uppercase labels get wide letter-spacing (0.12–0.3em). Arabic never gets letter-spacing.

## Signature graphics

- **Wanted poster:** the page header is a `surface-200` panel with a 3px `green` border and a thin inner rule 9px inside. The crest sits centred, with the red eyebrow "Wanted: big appetites", the Rye tagline and ★-separated categories.
- **Checkerboard strip:** a 16px-tall row of 16px `green` squares on `surface-100`. It goes under the poster and directly above the footer. Never fill a whole background with it.
- **Wooden plank:** a `green` sign with faint horizontal grain lines, `radius-plank`, `shadow-plank`, two `gold` nails at the ends and the title in Rye `on-green`. It has a `gold` kicker line underneath.
- **Dashed rope dividers:** 1px dashed `rope` between menu items, and 2px dashed above and below the chapter ticket.
- **Stars:** ★ in `gold` separate categories and sauces and frame the "With fries" line.

## Price chips

- **Single:** a filled `red` chip with `on-red` text. The small label is SINGLE / سنجل and the number is `price`.
- **Double:** a transparent chip with a 2px `red` inset border and `ink` text, labelled DOUBLE / دبل.
- **One price only:** a single filled `red` chip with no label.
- Chips sit at the end of the item's name line (right in English, left in Arabic). Use `radius-sm` corners and a minimum width of 54px. Show "Prices in EGP" once in the footer, not in the chips.

## Menu items

- Items are printed straight onto the parchment, with no card, box or background. A dashed `rope` line separates them.
- Each item has the name and chips on one line, an optional label row (★ Signature, Spicy, Grilled, Tortilla) as coloured text, and the italic ingredients below.
- **Photos are cut-outs only**, with no background. Put one oval floor shadow under the sandwich, using `floor` in a radial gradient. Never use a drop shadow around the outline. See *Photography and product images*.
- Show a photo only on Signature items and one hero per category.

## Iconography

- A custom line set (`assets/Icons/`) on a 24px grid with a 2px round stroke. It covers burger, chicken, hot dog, fries, drink and spicy, plus a solid star.
- The SVG files are drawn in `#1F1A16`. Inline them and set the stroke to `currentColor`, so they take `on-green` in tabs and `red-text` beside Spicy.
- Emoji may appear in social captions, never in the menu.

## Components

| Component | What it is |
|---|---|
| `PosterHeader` | Wanted-poster header with crest, eyebrow, tagline, categories and the language toggle |
| `CheckerStrip` | The green checkerboard strip |
| `ChapterBanner` | Dashed ticket with the round chapter medallion |
| `CategoryTabs` | Sticky green strap; the active tab is red |
| `SectionHeader` | Wooden plank sign with a "With fries" line |
| `MenuItem` | Name, price chips, labels, italic ingredients and an optional cut-out with floor shadow |
| `PriceTag` | Single / Double chips, or one chip |
| `Badge` | Coloured text labels: Signature, Spicy, Grilled, Tortilla, New |
| `SauceChips` | Toggle chips for add-on sauces |
| `Button` | Red primary, green secondary and gold footer buttons |

They are plain-DOM builders on `window.Enzo` (for example, `Enzo.MenuItem({...})` returns an element), styled by `components/bundle.css` through the tokens. The working reference page is the Option B draft of the online menu.
