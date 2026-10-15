# 05 · Themes

Six themes. Tokens live in `themes/themes.json`; CSS in `themes/themes.css` (generated);
the PPTX builder reads the JSON.

## Isolation vs sharing — the rule

**Shared across all themes (never vary):** grid & bands, type scale, component anatomy,
chart rules, copy rules, footnote format, page numbers.

**Owned by a theme (never borrow):** colour values, title weight, section-tag shape, cover &
divider art, background decoration, card treatment (flat / tinted / hairline / frosted),
verdict bar colour.

**One theme per deck.** A long deck can have many sections, but they all use the same
divider art and tag shape. If a deck is assembled from several older decks, **re-skin**
every slide into the chosen theme instead of keeping each source's look — a collage of
styles reads as several different authors.

## Brand-colour slot

`accent` is meant to be replaced by the brand colour of the deck owner. Check:
- contrast of white text on `accent` ≥ 4.5:1 for chips/verdicts (if not, darken 10–15% or
  use `ink` for the verdict and keep accent for highlights only);
- `accent` vs `accent_2` must be clearly different hues (≥ 60° apart) — accent_2 is the
  "look here" colour.
Logos go only in the header lockup, never into theme art.

## The six themes

| Theme | Mood | Title | Tag | Verdict | Signature art |
|---|---|---|---|---|---|
| **ledger** | analytical, dense, formal | 800, ink | black pill | ink bar, orange label | navy radial cover; flat accent wave + accent_2 outline on dividers |
| **horizon** | calm, structured | 500, navy | corner tab flush to top-right | navy bar | sky-gradient cover; chip card headers; navy panels |
| **bloom** | warm, friendly | 400, one accent phrase | coral pill | rose bar | soft blurred blobs bleeding from corners |
| **signal** | bold, energetic | 800 | pill pair: accent + black | accent bar | accent flare from top-right; round black → button |
| **aurora** | soft, modern | 500 | gradient header band | violet bar | pastel gradient + frosted glass panel + dot grid |
| **ember** | compact, direct | 400, large | gradient band | accent bar | dark cover with vertical accent→black stripes |

### Choosing
- Many tables and charts → **ledger** (the black verdict bar carries a lot per slide).
- Repeating page pairs across many items → **horizon** (chips make repeated structure scannable).
- Image-led, friendly → **bloom** (soft art lets visuals dominate).
- Before/after and growth numbers → **signal**.
- Matrices, segment tabs, soft tone → **aurora**.
- Short and direct → **ember**.

### Motif recipes (draw the art without images)

- **ledger**: cover = radial gradient `#0B2A8A` centre → `#050F33` edges. Divider = white bg,
  large accent shape with a wavy left edge on the right 40%, a 3 px accent_2 stroke offset
  8 px, a small grid of white dots inside the shape.
- **horizon**: linear gradient `#1B4F9C` → `#9CC3F0`, soft white blurred ellipses at 30–50%
  opacity; chip «Part N» in accent_2 above the title.
- **bloom**: 3 blurred circles (blur 60–90 px, ~55% opacity) in the `blobs` colours off the
  top-right and bottom-left corners; on content slides only at the corners, ≤ 15% of area.
- **signal**: diagonal streak from the top-right: overlapping ellipses rotated −30° in accent
  at 10–35% opacity, blurred; content slides get only a faint wash.
- **aurora**: background 120° `#F7A8C8 → #C9B8F5 → #8FA8F5`; frosted panel = white 30% +
  1 px white border 50% + backdrop blur; 6 × 4 dot grid top-right.
- **ember**: cover = vertical stripes accent → near-black (24 steps); header band = 5% strip,
  accent at left fading to grey.

In PPTX gradients are native (`deckkit` writes gradient fills); blurs are approximated with
large semi-transparent ellipses with soft edges.

## Adding a seventh theme

Copy an entry in `themes.json`, change values and `motif`, run
`python scripts/gen_theme_css.py`, add the motif drawing to `deckkit.draw_cover_art()` /
`draw_content_motif()` and a `[data-theme="name"]` block in `templates/deck.html`. Keep the
grammar untouched.
