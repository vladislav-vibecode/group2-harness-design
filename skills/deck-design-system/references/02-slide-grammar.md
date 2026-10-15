# 02 · Slide grammar (shared by every theme)

## Contents
1. Canvas & grid
2. The five bands
3. Components
4. Typography
5. Copy rules
6. Colour roles (theme-agnostic)

---

## 1. Canvas & grid

- 16:9. PPTX: 13.333 × 7.5 in (12192000 × 6858000 EMU). HTML: 1280 × 720 px, scaled to fit.
- All positions below are **% of slide width (x, w) / height (y, h)**, so they are
  identical in HTML and PPTX.
- Side margins **3%** (content x 3 → 97, width 94). Gutter between columns **1.5–2%**.
- Columns: 2-up = 46.25% each; 3-up = 30.4%; 4-up = 22.4%; 5-up = 17.6% (1.5% gutter).
- Inner card padding ≈ 1.8% x / 2.5% y. Cards have radius ≈ 10–14 px (0.12 in), no borders
  in `ledger`/`horizon`, hairline in `signal`, soft shadow only in `aurora`.

## 2. The five bands

| Band | y | h | Content |
|---|---|---|---|
| Header | 3.0 | 5.2 | left: logo lockup «LOGO A │ LOGO B» (x 3, h ≈ 3.6); middle-right: optional breadcrumb («Lorem. Вопрос #2», muted, underlined part); right: **section tag** (x 81, w 16) |
| Title | 11.7 | 8.0 | slide title, 1 line preferred, 2 max. Optional subtitle (muted, 11 pt) directly below |
| Body | 20 – 79 | ~59 | layout pattern from the catalog |
| Verdict | 81.2 | 8.2 | full-width bar: **label** (x 4.6, w 10, 8–9 pt bold caps, `verdict_label`) + **statement** (x 15.2, w 80, 13–15 pt bold, `verdict_text`) |
| Footnote | 92.3 rule; 93.5 text | 5.3 | hairline rule `line`; 8 pt muted: abbreviations → sources → period → own-estimate note; page number right (x 93, bold 10–11 pt) |

If a slide has no verdict, the body may extend to 89%. Never move the title.

## 3. Components

**Section tag** — caps, 8–9 pt bold, letter-spacing .06em. Shape from theme (`pill`,
`corner-tab`, `pill-pair`, `header-band`). Text: `SECTION · SUBTOPIC`.

**Kicker** — small caps label above a heading or number inside a card («LOREM IPSUM»,
«A · DOLOR SIT»). 8–9 pt bold, muted or accent.

**Stat tile** — kicker (optional) → hero number 30–34 pt bold in accent (or accent_2 for
the one alarming value) → 1–2 lines of explanation 10–11 pt. Tiles in a row share height.
Variant *stat row*: number left (w ≈ 35%), explanation right, stacked 3-high next to a chart.

**Numbered card** — «01» in accent_2 (16–18 pt bold) → heading 13–14 pt bold → body 10–11 pt
→ optional divider + second kicker + bold one-liner.

**Status chip** — tiny filled pill inside a card's top-right («LOREM», «NEW», «WAS / NOW»).
Colours: accent = action, accent_2 = hypothesis/risk, ink/grey = not applicable.

**Inverted card** — one card per row may use `ink` (or `accent_3` / `accent` per theme)
background with white text: the problem, the recommendation, or the item that breaks the
pattern.

**Verdict bar** — see bands. Suggested labels: RU — ВЫВОД, ИТОГ, ГЛАВНОЕ, РЕШЕНИЕ, ПРИНЦИП,
ПРАВИЛО, ПЛАН, ДАЛЕЕ, СТАРТ, ЗАДАЧА, ОГРАНИЧЕНИЕ; EN — SUMMARY, KEY POINT, DECISION, RULE,
PLAN, NEXT, START.

**Callout strip** — light tinted box inside the body for a secondary note. Smaller and
lighter than the verdict; never two verdict-like bars on one slide.

**Breadcrumb / link** — muted header text with an underlined part («Lorem. Вопрос #3»).
Signals depth without adding slides.

**Arrow button** (signal theme) — round ink circle with →, bottom-right: "the point
continues on the next slide".

**Logo lockup** — mark A │ mark B with a hairline separator. Templates use the text
placeholders `LOGO A` / `LOGO B`.

## 4. Typography

Font: **Manrope** (open, Google Fonts) — fallback Inter / Arial. One family per deck.

| Role | PPTX pt (13.33") | HTML px (1280w) | Weight |
|---|---|---|---|
| Cover title | 54–60 | 72–80 | 800 (or theme `title_weight`) |
| Divider title | 46–54 | 64–72 | 800 / theme |
| Slide title | 26–30 | 34–36 | theme `title_weight` (800 ledger/signal, 500 horizon/aurora, 400 bloom/ember) |
| Subtitle | 11–12 | 15 | 500, muted |
| Hero number | 30–34 | 38–42 | 800 |
| Card heading | 13–16 | 16–19 | 700 |
| Body | 11–12 | 13–14 | 400–500 |
| Kicker / tag | 8–9 | 11 | 700 caps, +0.06em |
| Table text | 9.5–10.5 | 12–13 | 500; header 700 |
| Footnote | 8 | 10 | 400 muted |

Line-height 1.1–1.15 for titles and numbers, 1.3 for body. Left-align everything except
numbers in tables (right) and hero numbers inside centred tiles.

## 5. Copy rules

- Title ≤ 75 characters; bullets ≤ 2 lines; ≤ 5 bullets per card.
- Lead with the number, then the meaning: «−00% — lorem ipsum dolor».
- Abbreviations allowed in the body if decoded in the footnote.
- Plans in infinitive/imperative: «Lorem ipsum…», "Align…", "Launch…".
- No exclamation marks except the closing slide.
- Mark estimates: «≈», «~», "estimate".

## 6. Colour roles (theme supplies the values)

| Role | Used for |
|---|---|
| `ink` | verdict bar (ledger), inverted card, dark tags, table header rule |
| `text` / `muted` | body / secondary text, axis labels |
| `line` | hairlines, table rules, footnote rule |
| `card` / `card_alt` | default card fill / highlighted-light card fill |
| `accent` | **the subject / the main series** — brand slot |
| `accent_2` | the *one* alarming or comparative value, numbering, hypothesis chips |
| `pos` / `neg` | deltas inside tables only (+00% green, −00% red) |

Rule of thumb: ≥ 70% of any slide is `bg` + `card`; accents ≤ 10% of the area.
