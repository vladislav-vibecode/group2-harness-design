#!/usr/bin/env python3
"""Build a .pptx from a JSON deck spec.

    python scripts/build_pptx.py examples/sample-deck.json out.pptx [--theme bloom] [--accent "#0A84FF"]

Spec shape (see examples/*.json):
{
  "theme": "ledger", "logo_a": "LOGO A", "logo_b": "LOGO B", "accent": null,
  "slides": [
    {"type": "cover",   "title": "Lorem\\nIpsum", "subtitle": "..."},
    {"type": "divider", "title": "Lorem ipsum", "chip": "Part 1"},
    {"type": "content", "layout": "L04", "tag": "LOREM · IPSUM", "title": "...", "subtitle": null,
     "breadcrumb": null, "verdict": ["LOREM", "..."], "footnote": "...",
     "blocks": [ {"kind": "bars", "box": [3,21,51,57], ...}, ... ]},
    {"type": "closing", "title": "Lorem ipsum"}
  ]
}

Block kinds → Deck methods: stats, cards, table, bars, donut, steps, timeline, heat_strip,
ladder, callout, old_new, placeholder, text, kicker.
`box` = [x, y, w, h] in % of slide. Omit box to use the full body zone [3, 21, 94, 58].
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deckkit import Deck  # noqa: E402

BODY = [3, 21, 94, 58]


def build(spec, out, theme=None, accent=None):
    d = Deck(theme or spec.get("theme", "ledger"), logo_a=spec.get("logo_a", "LOGO A"),
             logo_b=spec.get("logo_b", "LOGO B"), accent=accent or spec.get("accent"))
    for sl in spec["slides"]:
        t = sl.get("type", "content")
        if t == "cover":
            d.cover(sl["title"], sl.get("subtitle"))
        elif t == "divider":
            d.divider(sl["title"], sl.get("chip"), sl.get("desc"))
        elif t == "closing":
            d.closing(sl["title"], sl.get("subtitle"))
        else:
            s = d.content(sl.get("tag", ""), sl["title"], sl.get("subtitle"),
                          tuple(sl["verdict"]) if sl.get("verdict") else None,
                          sl.get("footnote"), sl.get("breadcrumb"))
            for b in sl.get("blocks", []):
                b = dict(b)
                kind = b.pop("kind")
                box = b.pop("box", BODY if sl.get("verdict") else [3, 21, 94, 66])
                if kind == "text":
                    d.text(s, *box, b.pop("text"), **b)
                elif kind == "kicker":
                    d.kicker(s, box[0], box[1], box[2], b["text"], color=b.get("color", "muted"))
                else:
                    getattr(d, kind)(s, box, **b)
    d.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("out")
    ap.add_argument("--theme")
    ap.add_argument("--accent")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    print(build(spec, a.out, a.theme, a.accent))
