# 07 · Placeholder content

Templates and examples in this skill contain **no real content**. Use these conventions so
placeholders are obvious, keep their shape, and can't be mistaken for data.

## Text
- Titles: lorem ipsum of realistic length (40–75 characters), e.g.
  «Lorem ipsum dolor sit amet: 00% consectetur».
- Body: 1–2 lines of lorem per bullet; keep bullet counts realistic (3–5).
- Labels and kickers: «LOREM IPSUM», «A · DOLOR», section tags «LOREM · IPSUM».
- Names of entities: «Lorem 1…N», «Item A/B/C», logo lockup «LOGO A │ LOGO B».
- People: role placeholders with initials («AB · Role»), never photos.

## Numbers
- Display numbers: `00`, `00%`, `0,0`, `+00%`, `−0,0`, ranges `00–00`, `0,0×`.
- Charts need geometry: give arbitrary values for bar heights but print every label as
  `00` (PPTX label format `'"00"'`; HTML label text `00`).
- Tables: `00,0`, `+0,0%`, `−0,0%` (keep +/− so the delta colouring is visible).
- Periods: «P1…P4», «Period 1–2», «00.00.0000».

## Images
- Grey placeholder rectangles with an italic caption («[image 16:9]», «[screen]»).

## Filling a template with real content
Replace every placeholder; run the hygiene part of `06-qa-checklist.md`; search the file
for `lorem`, `00`, `LOGO` before sending.
