# 03 · Layout catalog (39 patterns)

Every pattern lives inside the body zone (y 20–79%) unless marked *full-bleed*. IDs are used
in PPTX specs (`"layout": "L06"`) and as HTML comments (`<!-- L06 -->`).
All sample copy is lorem ipsum; numbers are `00` placeholders.

## Index
| Group | Patterns |
|---|---|
| Structure | L01 cover · L02 divider · L03 task grid · L22 next steps · L36 closing |
| Numbers | L04 chart + stat stack · L05 Metric row · L13 big-number trio · L17 scenario bars |
| Comparison | L06 table w/ highlight row · L07 rank ladder · L09 segment columns · L10 ranked bars · L18 before/after · L19 pros/cons · L33 old → new |
| Synthesis | L08 section summary · L11 problem → meaning → proposal · L16 scenarios · L25 goal panel + steps · L28 hypothesis card |
| Overview | L23 one-page grid · L24 table + strip · L26 three levels · L27 path / journey · L30 status matrix · L31 breakdown · L32 heat table · L37 scoring matrix |
| Process | L12 checklist · L14 trend + commentary · L15 timeline · L20 process steps · L35 ways of working · L38 cycle |
| People & visuals | L21 team chart · L29 track record · L34 image gallery · L39 annotated screens |

---

### L01 Cover *(full-bleed)*
```
│ LOGO A │ LOGO B                                 │
│                                                 │
│ Lorem                             [theme art]   │
│ Ipsum                                           │
│ dolor sit amet · 00.00.0000                     │
```
Title 2 lines max, huge. Theme art on the right ~45% (abstract shape or gradient).

### L02 Section divider *(full-bleed)*
Same as the cover with the section name. Optional chip «Блок 1» / "Part 1" above the title
or a one-line description under it. Use the *same* divider art throughout the deck.

### L03 Task grid (2×2)
```
┌ 01 Lorem ipsum ─────────┐ ┌ 02 Dolor sit ───────────┐
│ 1–2 lines               │ │                         │
└─────────────────────────┘ └─────────────────────────┘
┌ 03 Amet consectetur ────┐ ┌ 04 Adipiscing elit ─────┐
```
Numbers in accent_2, heading bold, light cards. No verdict.

### L04 Chart + stat stack
```
│ kicker: METRIC, UNIT          │ ┌ 00%  │ lorem ipsum  ┐ │
│ ▇ ▇ █ ▇  (one bar accent)     │ ├ −00% │ lorem ipsum  ┤ │
│ P1  P2  P3  P4*               │ └ 00–00% │ (card_alt) ┘ │
██ LABEL ██ Lorem ipsum dolor sit amet, consectetur adipiscing
```
Chart w ≈ 51%, stack w ≈ 40%. Third stat tinted `card_alt` = the forward-looking one.

### L05 Metric row
3–5 stat tiles across, then a table or two text columns below (or nothing). The title can
contain the target itself.

### L06 Comparison table with highlighted row
Header: `ink` text with a thick bottom rule (or `ink` fill + white text in ledger). The
subject row at the bottom, `card_alt` fill, bold. Numbers right-aligned. ≤ 8 rows × 7 cols;
beyond that → Appendix.

### L07 Rank ladder (dot plot)
Rows = criteria, columns = ranks 1…10. Subject position = filled accent_2 circle with the
number; target zone (ranks 1–3) shaded `card_alt`; right column "GAP" (+0,0 to target).
Shows how realistic an ambition is.

### L08 Section summary
Two or three tinted panels, each with a kicker and 2–4 numbered one-line findings. No verdict
bar — the slide *is* the verdict.

### L09 Segment columns (A / B / C)
```
┌ A · LOREM   ┐ ┌ B · IPSUM  ┐ █ C · DOLOR    █
│ 00% lorem   │ │ 00%        │ █ 00%          █
│ at 00% of X │ │ at 00%     │ █ at 00%       █
│ ─ INCLUDES  │ │ ─          │ █ ─            █
```
The column that breaks the pattern is inverted. Classic "small share of input gives most of
the output".

### L10 Ranked horizontal bars
Sorted desc, labels left with a 1-line sub-label, values at bar end. Others neutral/accent,
subject bar accent_2. Right card with 3 numbered observations.

### L11 Problem → meaning → proposal
Left dark card «PROBLEM» + big number; right top «WHAT IT MEANS» list; right bottom «WHAT WE
PROPOSE» list.

### L12 Checklist / standard
3 columns with numbered items 01–07, then a full-width strip with 08–10. Verdict «RULE».

### L13 Big-number trio
Lead paragraph (muted) + 3 equal tiles with one huge number each (`~00` / `0` / `00`) and a
2-line meaning. First number in accent_2 if it's the alarm.

### L14 Trend + commentary
Grouped bars or lines over periods (subject accent, comparator grey) on the left 55%;
right: 2 stacked cards explaining the trend with their own numbers.

### L15 Timeline
Horizontal line with dots (period labels above in accent caps), cards below each dot (phase
name + 2–4 bullets). Max 5 phases.

### L16 Scenarios
2–3 large cards: kicker «SCENARIO 1 · LOREM», big number, 3 mini-metrics, assumptions line.
Recommended scenario = accent fill (or inverted). Bottom strip compares outcomes.

### L17 Scenario bars
3 ascending bars (stacked when effects add up), each labelled with a range «+00–00»; under
each a caption card (scenario, period, requirement). Last scenario highlighted.

### L18 Before / after table
Columns: Parameter · Now · After. Right column tinted `card_alt`, bold where improved. 5–7
rows. Verdict = the single benefit.

### L19 Pros / cons
Left light card «PROS», right inverted card «CONS». Verdict = the response.

### L20 Process steps
5–6 narrow numbered columns 01–06, each 1 heading + 2 lines; a support strip below. Shows
ownership of each step.

### L21 Team chart
Groups of role cards (initials circle, role, share of time). Centre card inverted. Bottom
row: 4 numbered collaboration principles. *Templates never contain real names or photos.*

### L22 Next steps
4–5 numbered rows (accent_2 numbers, one line each, hairline separators) + verdict «START».

### L23 One-page grid
```
┌ CHIP 1 ────┐┌ CHIP 2 ───┐┌ CHIP 3 ────┐┌ visual   ┐
│ 1 lorem    ││ lorem     ││ lorem 00%  ││ slot     │
│ 2 ipsum    ││ ipsum     ││ ipsum 00%  ││          │
├ CHIP 4 ────┴────────────┤├ CHIP 5 ────┤│          │
│ 1 … 2 … 3 …             ││ 00 + strip ││          │
```
Chips (accent_2) as card headers. One per item of a portfolio; pair with L24.

### L24 Table + strip
Table (item · amount · target) with header row in accent, total row bold; right: visual
card; bottom: «Logic.» one paragraph + a 12-cell intensity strip.

### L25 Goal panel + steps
Left inverted panel (goal, indicators, how measured); right numbered list of 4–5 actions,
each with a bold lead phrase. One slide per goal.

### L26 Three levels
3 columns «LEVEL 1», «LEVEL 2», «LEVEL 3», each: who / what / how measured. Chip headers.

### L27 Path / journey
Either a curve with stage dots and notes under each, or a table: stages as columns, rows =
tasks / means / indicators.

### L28 Hypothesis card
Grid: Hypothesis (large «!» icon) · Mechanism (bullets) · Risks · Expected effect (huge `+0,0%`
in accent). Breadcrumb «Goal 3 │ Lorem».

### L29 Track record
Left: stat tiles (`00` periods · `0,0` score · pills). Right: bar chart over time (last bar
accent). Bottom: 3 numbered wins.

### L30 Status matrix
Rows = items, columns = periods; cells are small pills «done» (accent), «not done» (grey),
«possible» (outlined accent). Legend below. Shows growth of scope.

### L31 Breakdown
3 tiles on top (total · 00 · 00), then 3 cards: donut by type A, donut by type B, columns
by period. Donuts ≤ 6 slices, one accent slice.

### L32 Heat table
Categories × periods; cells = index (100 = average) coloured by a 4-step ramp. Legend under
the table.

### L33 Old → new
«was:» card with strikethrough text → big accent «»» → «now:» card. Reframes a task.

### L34 Image gallery
3–4 equal tiles (image placeholders) with a caption chip above each. Optional left text
column with the principle. No verdict.

### L35 Ways of working
6 cards: cadence · internal statuses · shared statuses · follow-up · planning · reporting.
Icon + heading + 2 lines.

### L36 Closing *(full-bleed)*
Cover art + one line.

### L37 Scoring matrix
Rows = options, columns = weighted criteria → «Total» bold. Row "weight" at the bottom in
muted. Top-scored rows tinted.

### L38 Cycle
Circle of 5–6 nodes with a text column explaining the same steps on the left.

### L39 Annotated screens
2 device frames (placeholders), each with: stage chip, «Issue» text, «Fix» text. Header stat
row before the series: «0 stages · 00 screens · 00 issues · 00 fixes».
