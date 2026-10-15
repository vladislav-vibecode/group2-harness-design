# 04 · Charts & tables

Charts in these decks are **arguments, not dashboards**. Each chart answers the slide title
and nothing else.

## Core rules

1. **One highlighted series/point.** Everything else neutral grey (`#B9BFCB`-ish). The
   highlight is the subject, the current period, the forecast, or the outlier the title
   talks about. Label the highlighted value in bold accent.
2. **Direct labels, no legends where possible.** Values on/above bars; series names at line
   ends. Legend only for ≥ 3 series, top-left under the kicker.
3. **Kicker = metric + unit + scope** («LOREM IPSUM, UNIT»). The chart itself has no title.
4. **Forecast / estimate** marked with `*` on the axis label (`P4*`) and explained in the
   footnote; forecast bars may use a lighter tint.
5. **No 3D, no gradients inside data marks, no gridlines except a faint baseline.** If values
   are labelled, drop the value axis.
6. **Sorting**: ranked bars always sorted; time left→right; table rows in the order of the
   argument (subject last, highlighted).
7. **Index instead of absolutes when data is sensitive**: "subject = 1,0". Shows relative
   position without exposing values.

## Pattern library

| Need | Form | Notes |
|---|---|---|
| Value over periods | vertical bars, 4–7 bars | current/forecast bar accent; deltas as small labels above |
| Ranking | horizontal ranked bars | subject bar accent_2; value labels at bar end; sub-label under each name |
| Share & concentration | 2 donuts side by side | single accent slice; big % in the hole |
| Position vs leaders | rank ladder (L07) | dots on a 1–10 grid, target zone shaded |
| Two series over time | grouped bars or 2 lines | subject accent, comparator grey; annotate the turning point |
| Step-to-step drop | table with % rows | the "drop" row tinted `card_alt` |
| Split of a total | donut ≤ 6 slices **or** 100% bar | absolute values in the legend |
| Intensity by period | 12-cell strip or heat table (L32) | 4-step ramp; 1-letter period labels |
| Scenario effects | ascending stacked bars (L17) | ranges in labels, last scenario highlighted |
| Indicator history | 4 small bar charts in a 2×2 grid | same scale per chart, current period accent, "lower is better" note where relevant |
| Cohorts | table with heat colouring | accent ramp for ≥ benchmark |
| Calendar | Gantt-like table | filled cells accent, labels inside |

## Tables

- Header: bold 9.5–10 pt, `ink` text, 2 px rule under it — or, in ledger, `ink` fill with
  white text for dense tables.
- Rows: hairline `line` separators, no zebra (except long Appendix tables: very light zebra).
- Numbers right-aligned, tabular figures, same decimals per column.
- Highlight: subject/total row `card_alt` fill + bold; a single decisive cell in accent.
- Deltas `+0,0%` green / `−0,0%` red, only inside tables.
- ≤ 8 rows on an argument slide; full data → Appendix in the same style.

## Colour ramps (derive from theme)

- **Sequential (heat)**: 4 steps from `card` to `accent`, or the warm ramp
  `#FDE7DA → #F6BE9C → #EC9063 → #D9622E`.
- **Categorical (donuts)**: accent, accent at 60%, accent_2, muted grey, light grey,
  card_alt. Never more than 6.

## PPTX vs HTML

- PPTX: native charts (python-pptx `add_chart`) so numbers stay editable;
  `deckkit.bars()` sets fonts, removes gridlines and colours the highlighted point.
  In templates use the label format `'"00"'` so every label prints a placeholder.
- HTML: inline CSS/SVG bars in the page; same rules.
