# 06 · QA checklist

Render every slide to an image (PPTX: `soffice --headless --convert-to pdf` then
`pdftoppm -r 60 -png`; HTML: `scripts/export_pdf.py --png`) and look at each one. Contact
sheets of 12–16 slides make inconsistencies jump out.

## Structure
- [ ] Reading only dividers + titles + verdict bars gives the complete story.
- [ ] Every title states a point (has a verb or a number), ≤ 2 lines.
- [ ] Every large section ends with a summary slide; deck ends with plan/team/next steps.
- [ ] Effects are ranges/scenarios with assumptions, not single promises.

## Grammar
- [ ] Title, tag, verdict bar and page number sit at the same position on every slide.
- [ ] Exactly one verdict bar per argument slide.
- [ ] Each chart highlights one thing; others neutral.
- [ ] At most one inverted card per row.
- [ ] Footnote has abbreviations + sources + period where numbers appear.
- [ ] No text below 8 pt / 10 px; nothing overflows; no orphan words in titles.
- [ ] Numbers: units everywhere, consistent decimals, `−` minus, en-dash ranges, spaced thousands.

## Theme
- [ ] Only one theme's motifs appear in the deck.
- [ ] `accent` = brand colour, contrast checked; accent area ≤ ~10% per slide.
- [ ] Dividers use the same art throughout.

## Hygiene
- [ ] No leftover placeholders in a finished deck (lorem, `00`, «TODO», «xx»).
- [ ] No leftover content from other decks (names, logos, screenshots, numbers).
- [ ] Hidden/backup slides removed or moved to Appendix; speaker notes and file metadata clean.
- [ ] Images compressed (≤ 200 KB each); file size reasonable.
