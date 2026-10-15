---
name: deck-design-system
description: Design presentation decks (HTML slides or editable PPTX) with a consistent slide grammar, 39 layout patterns, chart/table rules and 6 isolated visual themes. Use this skill whenever the user asks for slides, a deck, a presentation a report in slide form, or wants an existing deck restyled or made consistent — even if they only say "make slides about X" or "оформи презентацию".
---

# Deck Design System

A design system for argument-driven presentations. It does not care about the topic: it
defines **how a slide is built** and **how a deck looks**. All examples use lorem ipsum
text and placeholder numbers (`00%`, `0,0`).

The system has **two layers**. Keep them separate — that is the whole trick.

| Layer | What it controls | Scope |
|---|---|---|
| **Grammar** (shared) | grid, header → title → body → verdict → footnote, type scale, components, chart rules, deck structure, copy rules | identical in every deck, every theme |
| **Theme** (isolated) | colour tokens, title weight, tag shape, cover/divider artwork, decorative motif | exactly **one** per deck, never mixed |

Why: the grammar is what makes a deck *read* well (a reader can skim titles + verdict bars
and get the whole argument); the theme only sets mood and brand. Mixing motifs from two
themes makes a deck look assembled from parts; varying the grammar between slides makes it
hard to read. So: grammar always, one theme, `accent` = the owner's brand colour.

## Workflow

1. **Plan the deck structure** → `references/01-deck-structure.md`.
   Write the whole deck as a list of slide titles first (one sentence each, stating the
   point of the slide). If the titles alone don't tell the story, fix them before designing.
2. **Pick one theme** → `references/05-themes.md`. Put the brand colour into the `accent`
   slot; leave the rest of the tokens alone.
3. **Lay out each slide** with a pattern from `references/03-layout-catalog.md`, inside the
   grid and component rules of `references/02-slide-grammar.md`. Charts and tables:
   `references/04-data-viz.md`.
4. **Build**:
   - HTML: copy `templates/deck.html`, set `<html data-theme="…">`, duplicate slide
     sections. Export to PDF/PNG with `scripts/export_pdf.py`.
   - PPTX: write a JSON spec (see `examples/sample-deck.json`) and run
     `python scripts/build_pptx.py spec.json out.pptx`. The builder (`scripts/deckkit.py`)
     already knows the grid, the components and all six themes; extend it rather than
     placing shapes by hand.
5. **QA** with `references/06-qa-checklist.md` — render to images and look at every slide.

## The slide, in one picture

```
┌──────────────────────────────────────────────────────────────┐ 0%
│ [LOGO A | LOGO B]               [breadcrumb]   [SECTION · TAG]│ 3–8%
│                                                              │
│ Slide title: the point of the slide, often with a number     │ 11.7–19.7%
│ (optional one-line subtitle in muted)                        │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐                 │
│ │ KICKER     │ │ KICKER     │ │ KICKER     │  body zone      │ 20–79%
│ │ 00%        │ │ 00%        │ │ 00%        │  (cards, chart, │
│ │ lorem      │ │ lorem      │ │ lorem      │   table…)       │
│ └────────────┘ └────────────┘ └────────────┘                 │
│ ██ LABEL ██  One-sentence takeaway the reader must remember  │ 81–89%
│ ──────────────────────────────────────────────────────────── │ 92.3%
│ Notes · abbreviations · sources                          07  │ 93.5–99%
└──────────────────────────────────────────────────────────────┘
 3% side margins, 16:9
```

Not every slide needs every band (covers, dividers and gallery slides drop them), but an
*argument* slide always has: section tag, title, body, verdict, footnote, page number.

## Non-negotiables (and why)

- **Title = the point, not the topic.** "Lorem ipsum grew 00% in two periods", not
  "Lorem ipsum". Readers often read titles only; a topic title makes them decode the chart.
- **One idea per slide, one verdict per slide.** The verdict bar holds the sentence the
  reader should repeat. Label it with a short caps word (e.g. ВЫВОД / ИТОГ / ПЛАН, or
  SUMMARY / NEXT / RULE in English).
- **Highlight exactly one thing.** In a chart, colour only the bar/row that matters;
  everything else is neutral grey. In a row of cards, make at most one card dark/inverted.
- **Every number has a unit and a source.** The footnote holds abbreviations, sources and
  period. This is what makes a deck defensible.
- **Number typography** (Russian style when writing in Russian): `1 234,5`, `−00%`,
  `+0,0 п.п.`, ranges with en dash `00–00`, non-breaking space before units.
- **Grid is fixed.** Margins 3%, same title position on every slide, verdict bar always at
  the same height. Stable anchors make a long deck feel calm.
- **Type scale** (13.33" × 7.5" slide): title 26–30 pt (theme sets weight); hero number
  30–34 pt; card heading 13–16 pt bold; body 11–12 pt; kicker 9 pt bold caps with
  letter-spacing; footnote 8 pt. Nothing below 8 pt. If text doesn't fit, cut text — don't
  shrink it.
- **Placeholder content stays placeholder.** In templates and examples use lorem ipsum and
  `00` numbers (`references/07-placeholder-content.md`); never paste real data into the
  skill files.

## Reference map

| File | Read when |
|---|---|
| `references/01-deck-structure.md` | starting any deck: deck shapes, section order, title formulas |
| `references/02-slide-grammar.md` | before laying out: grid numbers, bands, components, copy rules |
| `references/03-layout-catalog.md` | choosing a layout for a given message (39 patterns, wireframes) |
| `references/04-data-viz.md` | any chart, table, heatmap, timeline or scenario comparison |
| `references/05-themes.md` | picking/adapting a theme; mixing rules; brand-colour slot |
| `references/06-qa-checklist.md` | before handing the deck over |
| `references/07-placeholder-content.md` | writing templates/examples; lorem and number placeholders |
| `themes/themes.json` | exact tokens (single source for CSS and PPTX) |
| `templates/deck.html` | HTML starting point with all bands and core components |
| `scripts/deckkit.py`, `scripts/build_pptx.py` | PPTX generation from a JSON spec |

## Quick theme defaults

- Dense, many tables and charts, formal → **ledger**
- Long, structured, repeating page pairs → **horizon**
- Friendly, image-led → **bloom**
- Bold, growth numbers, before/after → **signal**
- Soft, modern, matrices and tabs → **aurora**
- Short and direct → **ember**

Ask only if the deck's purpose is genuinely unclear; otherwise state the choice in one line
and go.
