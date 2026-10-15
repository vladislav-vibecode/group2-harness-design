#!/usr/bin/env python3
"""Generate CSS custom properties for every theme from themes/themes.json.

Writes themes/themes.css and refreshes the block between
/* THEME-TOKENS:START */ and /* THEME-TOKENS:END */ in templates/deck.html,
so the template stays a single self-contained file.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = json.loads((ROOT / "themes" / "themes.json").read_text(encoding="utf-8"))
shared = T["_shared"]

KEYS = ["bg", "ink", "text", "muted", "line", "card", "card_alt", "accent", "accent_2",
        "accent_3", "on_accent", "verdict_bg", "verdict_label", "verdict_text", "tag_bg",
        "tag_text"]

out = [f":root{{--font:'{shared['font']}',{shared['font_fallback']};"
       f"--pos:{shared['pos']};--neg:{shared['neg']};}}"]
for name, t in T.items():
    if name.startswith("_"):
        continue
    v = []
    for k in KEYS:
        val = t.get(k)
        if val is None:
            val = t.get("accent_2") if k == "accent_3" else None
        if val == "gradient":
            val = f"linear-gradient(90deg,{t['accent']},{t.get('accent_2')},{t.get('accent_3', t['accent'])})"
        if val:
            v.append(f"--{k.replace('_', '-')}:{val}")
    v.append(f"--title-weight:{t.get('title_weight', 800)}")
    v.append(f"--cover-a:{t['cover_bg'][0]};--cover-b:{t['cover_bg'][1]}")
    if "blobs" in t:
        v += [f"--blob-{i + 1}:{c}" for i, c in enumerate(t["blobs"])]
    out.append(f'[data-theme="{name}"]{{' + ";".join(v) + "}")
css = "\n".join(out) + "\n"
(ROOT / "themes" / "themes.css").write_text(css, encoding="utf-8")

deck = ROOT / "templates" / "deck.html"
if deck.exists():
    html = deck.read_text(encoding="utf-8")
    html = re.sub(r"/\* THEME-TOKENS:START \*/.*?/\* THEME-TOKENS:END \*/",
                  "/* THEME-TOKENS:START */\n" + css + "/* THEME-TOKENS:END */", html, flags=re.S)
    deck.write_text(html, encoding="utf-8")
print("ok:", ROOT / "themes" / "themes.css")
