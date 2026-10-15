"""deckkit — build decks in PPTX from the shared slide grammar + one theme.

All geometry is in PERCENT of slide width (x, w) and height (y, h), matching
references/02-slide-grammar.md. Themes come from themes/themes.json.

Usage (library):
    from deckkit import Deck
    d = Deck("ledger", logo_a="LOGO A", logo_b="LOGO B")
    d.cover("Lorem\\nIpsum", "Dolor sit amet · 00.00.0000")
    s = d.content(tag="LOREM · IPSUM", title="Lorem ipsum dolor: 00% sit amet",
                  verdict=("LOREM", "Consectetur adipiscing elit, sed do eiusmod"),
                  footnote="Lorem: ipsum dolor. Source: lorem ipsum.")
    d.bars(s, [3, 21, 51, 57], ["P1", "P2", "P3"], [3, 4, 5], highlight=2, fmt='"00"')
    d.save("out.pptx")

Or via JSON spec: see build_pptx.py and examples/*.json.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

ROOT = Path(__file__).resolve().parent.parent
THEMES = json.loads((ROOT / "themes" / "themes.json").read_text(encoding="utf-8"))

SLIDE_W, SLIDE_H = 12192000, 6858000  # 13.333 x 7.5 in

# ---- grid (percent) --------------------------------------------------------
M = 3.0                      # side margin
HEADER_Y, HEADER_H = 3.0, 5.2
TITLE_Y, TITLE_H = 11.7, 8.0
BODY_Y, BODY_B = 21.0, 79.0  # body top / bottom
VERDICT_Y, VERDICT_H = 81.2, 8.2
RULE_Y, FOOT_Y = 92.3, 93.5


def rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr.lstrip("#").upper())


def mix(a: str, b: str, t: float) -> str:
    """Blend colour a→b by t (0..1)."""
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


class Deck:
    def __init__(self, theme: str = "ledger", logo_a: str = "LOGO A", logo_b: str = "LOGO B",
                 accent: str | None = None, font: str | None = None):
        if theme not in THEMES:
            raise ValueError(f"unknown theme {theme}; choose from "
                             f"{[k for k in THEMES if not k.startswith('_')]}")
        self.t = dict(THEMES[theme])
        self.t.update({k: v for k, v in THEMES["_shared"].items() if k not in self.t})
        if accent:
            self.t["accent"] = accent
        self.name = theme
        self.font = font or THEMES["_shared"]["font"]
        self.logo_a, self.logo_b = logo_a, logo_b
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = SLIDE_W, SLIDE_H
        self.blank = self.prs.slide_layouts[6]
        self.page = 0

    # ---- unit helpers ------------------------------------------------------
    @staticmethod
    def X(p): return Emu(int(SLIDE_W * p / 100))

    @staticmethod
    def Y(p): return Emu(int(SLIDE_H * p / 100))

    def c(self, key):  # theme colour
        v = self.t.get(key, key)
        return v if v.startswith("#") else "#" + v

    # ---- primitives --------------------------------------------------------
    def rect(self, s, x, y, w, h, fill=None, radius=None, line=None, alpha=None, shape=None):
        shp_type = shape or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE)
        shp = s.shapes.add_shape(shp_type, self.X(x), self.Y(y), self.X(w), self.Y(h))
        if radius and shp_type == MSO_SHAPE.ROUNDED_RECTANGLE:
            # radius given in % of the shorter side (python-pptx adj is fraction of min side)
            shp.adjustments[0] = max(0.0, min(0.5, radius))
        if fill:
            shp.fill.solid()
            shp.fill.fore_color.rgb = rgb(self.c(fill))
            if alpha is not None:
                self._alpha(shp, alpha)
        else:
            shp.fill.background()
        if line:
            shp.line.color.rgb = rgb(self.c(line))
            shp.line.width = Pt(0.75)
        else:
            shp.line.fill.background()
        # drop the theme style reference (it carries a default shadow LibreOffice/Keynote render)
        st = shp._element.find(qn("p:style"))
        if st is not None:
            shp._element.remove(st)
        return shp

    def _alpha(self, shp, alpha):
        srgb = shp.fill._xPr.find(".//" + qn("a:srgbClr"))
        if srgb is not None:
            a = etree.SubElement(srgb, qn("a:alpha"))
            a.set("val", str(int(alpha * 100000)))

    def soft(self, shp, radius_pt=40):
        """Soft (blurred) edges — used for bloom/signal/aurora motifs."""
        spPr = shp._element.spPr
        eff = etree.SubElement(spPr, qn("a:effectLst"))
        se = etree.SubElement(eff, qn("a:softEdge"))
        se.set("rad", str(int(radius_pt * 12700)))

    def gradient(self, shp, stops, angle=90):
        shp.fill.gradient()
        shp.fill.gradient_angle = angle
        gs = shp.fill.gradient_stops
        # python-pptx gives 2 stops; set them, extend via XML if more
        gsLst = shp.fill._xPr.find(".//" + qn("a:gsLst"))
        for g in list(gsLst):
            gsLst.remove(g)
        for i, col in enumerate(stops):
            g = etree.SubElement(gsLst, qn("a:gs"))
            g.set("pos", str(int(100000 * i / max(1, len(stops) - 1))))
            c = etree.SubElement(g, qn("a:srgbClr"))
            c.set("val", self.c(col).lstrip("#"))
        return shp

    def text(self, s, x, y, w, h, txt, size=11, bold=False, color="text", align="l",
             anchor="t", caps=False, weight=None, italic=False, spacing=None, lh=None,
             strike=False):
        tb = s.shapes.add_textbox(self.X(x), self.Y(y), self.X(w), self.Y(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Emu(0)
        tf.margin_top = tf.margin_bottom = Emu(0)
        tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE,
                              "b": MSO_ANCHOR.BOTTOM}[anchor]
        lines = txt if isinstance(txt, list) else str(txt).split("\n")
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
            if lh:
                p.line_spacing = lh
            # inline **bold** support
            parts = str(line).split("**")
            for j, part in enumerate(parts):
                if not part:
                    continue
                r = p.add_run()
                r.text = part.upper() if caps else part
                f = r.font
                f.size = Pt(size)
                f.name = self.font
                f.bold = bold or (j % 2 == 1) or (weight is not None and weight >= 600)
                f.italic = italic
                f.color.rgb = rgb(self.c(color))
                if strike:
                    r._r.get_or_add_rPr().set("strike", "sngStrike")
                if spacing:
                    r._r.get_or_add_rPr().set("spc", str(int(spacing * 100)))
        return tb

    # ---- motifs ------------------------------------------------------------
    def _bg(self, s, color):
        bg = s.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb(self.c(color))

    def draw_cover_art(self, s, kind="cover"):
        t, n = self.t, self.name
        if n == "ledger":
            if kind in ("cover", "closing"):
                r = self.rect(s, 0, 0, 100, 100)
                self.gradient(r, [t["cover_bg"][1], t["cover_bg"][0]], angle=0)
                for i, a in enumerate((0.35, 0.22, 0.12)):
                    e = self.rect(s, 58 - i * 6, 10 - i * 8, 40 + i * 12, 80 + i * 16,
                                  fill="accent", alpha=a, shape=MSO_SHAPE.OVAL)
                    self.soft(e, 60)
                return "#FFFFFF"
            self._bg(s, "bg")
            w = self.rect(s, 62, -5, 45, 110, fill="accent", shape=MSO_SHAPE.WAVE)
            w.rotation = 90
            o = self.rect(s, 60, -5, 45, 110, line="accent_2", shape=MSO_SHAPE.WAVE)
            o.rotation = 90
            o.line.width = Pt(2.5)
            for i in range(4):
                for j in range(5):
                    self.rect(s, 86 + j * 2.2, 6 + i * 4, 0.6, 1.07, fill="#FFFFFF",
                              shape=MSO_SHAPE.OVAL)
            return t["ink"]
        if n == "horizon":
            r = self.rect(s, 0, 0, 100, 100)
            self.gradient(r, t["cover_bg"], angle=90)
            for (x, y, w, h, a) in ((45, 30, 55, 45, .45), (10, 65, 60, 40, .35),
                                    (60, 70, 45, 35, .5), (-10, 20, 40, 30, .25)):
                e = self.rect(s, x, y, w, h, fill="#FFFFFF", alpha=a, shape=MSO_SHAPE.OVAL)
                self.soft(e, 50)
            return "#FFFFFF"
        if n == "bloom":
            self._bg(s, "bg")
            b = t["blobs"]
            for (x, y, w, h, col, a) in ((55, -25, 60, 90, b[0], .75), (75, 30, 40, 70, b[1], .6),
                                         (-15, 60, 40, 60, b[2], .5)):
                e = self.rect(s, x, y, w, h, fill=col, alpha=a, shape=MSO_SHAPE.OVAL)
                self.soft(e, 80)
            return t["ink"]
        if n == "signal":
            self._bg(s, "bg")
            for i, (a, dx) in enumerate(((.18, 0), (.35, 6), (.6, 12))):
                e = self.rect(s, 45 + dx, -30 + dx, 70 - dx, 55, fill="accent", alpha=a,
                              shape=MSO_SHAPE.OVAL)
                e.rotation = -30
                self.soft(e, 45)
            self.rect(s, M, 88, 94, 0.25, fill="ink")
            return t["ink"]
        if n == "aurora":
            r = self.rect(s, 0, 0, 100, 100)
            self.gradient(r, [t["cover_bg"][0], "#C9B8F5", t["cover_bg"][1]], angle=135)
            self.rect(s, 4, 9, 92, 82, fill="#FFFFFF", alpha=.28, radius=.06, line="#FFFFFF")
            for i in range(4):
                for j in range(8):
                    self.rect(s, 70 + j * 3, 14 + i * 4, .35, .62, fill="#FFFFFF", alpha=.8,
                              shape=MSO_SHAPE.OVAL)
            return t["ink"]
        if n == "ember":
            stripes = 24
            for i in range(stripes):
                col = mix(t["cover_bg"][0], t["cover_bg"][1], i / (stripes - 1))
                self.rect(s, i * 100 / stripes, 0, 100 / stripes + .05, 100, fill=col)
            return "#FFFFFF"
        self._bg(s, "bg")
        return t["ink"]

    def draw_content_motif(self, s):
        t, n = self.t, self.name
        self._bg(s, "bg")
        if n == "bloom":
            b = t["blobs"]
            for (x, y, w, h, col, a) in ((84, -18, 26, 40, b[0], .45), (92, -10, 14, 30, b[1], .4),
                                         (-8, 88, 22, 30, b[2], .35)):
                e = self.rect(s, x, y, w, h, fill=col, alpha=a, shape=MSO_SHAPE.OVAL)
                self.soft(e, 40)
        elif n == "signal":
            e = self.rect(s, 70, -25, 45, 40, fill="accent", alpha=.12, shape=MSO_SHAPE.OVAL)
            self.soft(e, 50)
            e = self.rect(s, -10, 85, 60, 30, fill="accent", alpha=.08, shape=MSO_SHAPE.OVAL)
            self.soft(e, 50)
        elif n == "aurora":
            r = self.rect(s, M, 2.5, 94, 5.5, radius=.25)
            self.gradient(r, ["accent", "accent_2", "accent_3"], angle=0)
        elif n == "ember":
            r = self.rect(s, M, 2.8, 94, 5.2)
            self.gradient(r, ["accent", mix(t["accent"], "#9A9A9A", .7), "#D8D8D8"], angle=0)

    # ---- bands -------------------------------------------------------------
    def _lockup(self, s, color, y=HEADER_Y + .6, big=False):
        size = 15 if big else 10
        aw = len(self.logo_a) * (1.25 if big else 0.85) + 1.0  # approx text width, %
        self.text(s, M, y, aw + 2, 4, self.logo_a, size=size, bold=True, color=color, spacing=1)
        self.rect(s, M + aw, y + .2, .12, 3.4 if big else 2.8, fill=color)
        self.text(s, M + aw + 1, y, 25, 4, self.logo_b, size=size, bold=True,
                  color=color, italic=True)

    def _tag(self, s, tag, breadcrumb=None):
        t = self.t
        shape = t["tag_shape"]
        if shape in ("header-band",):
            # section name sits inside the gradient band (left), lockup on the right
            self.text(s, M + 1.2, 3.3, 50, 4, tag, size=10, bold=True, color="#FFFFFF",
                      anchor="m")
            self.text(s, 70, 3.3, 26, 4, f"{self.logo_a} × {self.logo_b}", size=9,
                      bold=True, color="#FFFFFF", align="r", anchor="m")
            return
        self._lockup(s, t["ink"] if t["mode"] == "light" else "#FFFFFF")
        if shape == "corner-tab":
            self.rect(s, 79, -1, 22, 7, fill="tag_bg", radius=.3)
            self.text(s, 80, 1.2, 19, 4, tag, size=9, bold=True, color="tag_text",
                      align="c", anchor="m", caps=True, spacing=0.5)
        elif shape == "pill-pair" and "│" in tag:
            a, b = [x.strip() for x in tag.split("│", 1)]
            self.rect(s, 64, HEADER_Y, 11, 4.4, fill="accent", radius=.5)
            self.text(s, 64, HEADER_Y, 11, 4.4, a, size=8, bold=True, color="#FFFFFF",
                      align="c", anchor="m")
            self.rect(s, 75.5, HEADER_Y, 21.5, 4.4, fill="tag_bg", radius=.5)
            self.text(s, 75.5, HEADER_Y, 21.5, 4.4, b, size=8, bold=True, color="tag_text",
                      align="c", anchor="m")
        else:
            self.rect(s, 81, HEADER_Y, 16, HEADER_H, fill="tag_bg", radius=.5)
            self.text(s, 81, HEADER_Y, 16, HEADER_H, tag, size=8, bold=True, color="tag_text",
                      align="c", anchor="m", caps=True, spacing=0.5)
        if breadcrumb:
            self.text(s, 45, HEADER_Y + .6, 34.5, 4, breadcrumb, size=9, color="muted",
                      align="r", anchor="m")

    def _title(self, s, title, subtitle=None):
        t = self.t
        w = t.get("title_weight", 800)
        self.text(s, M, TITLE_Y, 94, TITLE_H, title, size=26, bold=w >= 600, color="ink",
                  anchor="t", lh=1.0)
        if subtitle:
            self.text(s, M, TITLE_Y + 7.6, 90, 3.5, subtitle, size=11, color="muted")

    def _verdict(self, s, label, statement):
        self.rect(s, M, VERDICT_Y, 94, VERDICT_H, fill="verdict_bg",
                  radius=.15 if self.name in ("bloom", "aurora", "signal") else .08)
        self.text(s, 4.6, VERDICT_Y, 10, VERDICT_H, label, size=8, bold=True,
                  color="verdict_label", anchor="m", caps=True, spacing=0.6)
        self.text(s, 15.2, VERDICT_Y, 80, VERDICT_H, statement, size=13, bold=True,
                  color="verdict_text", anchor="m")

    def _footer(self, s, footnote=None):
        self.page += 1
        self.rect(s, M, RULE_Y, 94, 0.12, fill="line")
        if footnote:
            self.text(s, M, FOOT_Y, 88, 5.3, footnote, size=7.5, color="muted", lh=1.0)
        self.text(s, 92, FOOT_Y - .2, 5, 4, f"{self.page:02d}", size=10, bold=True,
                  color="ink", align="r")

    # ---- slide types -------------------------------------------------------
    def cover(self, title, subtitle=None, kind="cover"):
        s = self.prs.slides.add_slide(self.blank)
        fg = self.draw_cover_art(s, kind)
        self._lockup(s, fg, y=6, big=True)
        size = 54 if kind != "divider" else 46
        self.text(s, 5 if self.name == "aurora" else M + 1, 30, 60, 40, title, size=size,
                  bold=self.t.get("title_weight", 800) >= 600 or kind == "cover",
                  color=fg, anchor="m", lh=0.95)
        if subtitle:
            self.text(s, M + 1, 73, 60, 10, subtitle, size=13, color=fg)
        self.page += 1
        return s

    def divider(self, title, chip=None, desc=None):
        s = self.cover(title, desc, kind="divider")
        if chip:
            self.rect(s, M + 1, 24, 9, 4.6, fill="accent_2" if self.name == "horizon" else "accent",
                      radius=.2)
            self.text(s, M + 1, 24, 9, 4.6, chip, size=10, bold=True, color="#FFFFFF",
                      align="c", anchor="m")
        return s

    def closing(self, title, subtitle=None):
        return self.cover(title, subtitle, kind="closing")

    def content(self, tag, title, subtitle=None, verdict=None, footnote=None, breadcrumb=None):
        s = self.prs.slides.add_slide(self.blank)
        self.draw_content_motif(s)
        self._tag(s, tag, breadcrumb)
        self._title(s, title, subtitle)
        if verdict:
            self._verdict(s, *verdict)
        self._footer(s, footnote)
        return s

    # ---- components --------------------------------------------------------
    def card(self, s, x, y, w, h, fill="card", inverted=False):
        if inverted:
            fill = "accent_3" if self.name == "bloom" else (
                "accent" if self.name in ("signal", "ember") else "ink")
        r = self.rect(s, x, y, w, h, fill=fill, radius=.06)
        # white-on-white cards (aurora, signal) need a hairline to exist
        if not inverted and self.c(fill).upper() in (self.c("bg").upper(), "#FFFFFF"):
            r.line.color.rgb = rgb(self.c("line"))
            r.line.width = Pt(0.75)
        return "#FFFFFF" if inverted else None

    def kicker(self, s, x, y, w, txt, color="muted"):
        return self.text(s, x, y, w, 3, txt, size=8, bold=True, color=color, caps=True,
                         spacing=0.6)

    def stats(self, s, box, items, cols=None, stacked=False, highlight=None):
        """items: [{"value","label","kicker"?}] — metric tiles (row) or stat rows (stacked)."""
        x, y, w, h = box
        n = len(items)
        g = 1.5
        if stacked:
            ih = (h - g * (n - 1)) / n
            for i, it in enumerate(items):
                yy = y + i * (ih + g)
                inv = it.get("invert", False)
                fill = "card_alt" if (highlight == i) else "card"
                fg = self.card(s, x, yy, w, ih, fill=fill, inverted=inv)
                vs = 24 if len(it["value"]) <= 7 else (20 if len(it["value"]) <= 10 else 16)
                self.text(s, x + 1.6, yy, w * .38, ih, it["value"], size=vs, bold=True,
                          color=fg or it.get("color", "accent_2" if i == 0 else "accent"),
                          anchor="m")
                self.text(s, x + w * .4, yy, w * .56, ih, it["label"], size=10,
                          color=fg or "text", anchor="m")
            return
        cols = cols or n
        cw = (w - g * (cols - 1)) / cols
        rows = (n + cols - 1) // cols
        rh = (h - g * (rows - 1)) / rows
        for i, it in enumerate(items):
            cx, cy = x + (i % cols) * (cw + g), y + (i // cols) * (rh + g)
            inv = it.get("invert", False)
            fg = self.card(s, cx, cy, cw, rh, fill="card_alt" if highlight == i else "card",
                           inverted=inv)
            yy = cy + 2.4
            if it.get("kicker"):
                self.kicker(s, cx + 1.6, yy, cw - 3.2, it["kicker"], color=fg or "accent")
                yy += 4
            vs = 26 if len(it["value"]) <= 8 else 20
            self.text(s, cx + 1.6, yy, cw - 3.2, 8, it["value"], size=vs, bold=True,
                      color=fg or it.get("color", "accent"))
            self.text(s, cx + 1.6, yy + 8.5, cw - 3.2, rh - (yy - cy) - 9, it["label"],
                      size=10, color=fg or "text")

    def cards(self, s, box, items, cols=None, invert=None, numbered=True, fill="card",
              body_size=9.5):
        """items: [{"title","body"(str|list),"kicker"?,"chip"?,"num"?,"foot_kicker"?,"foot"?}]"""
        x, y, w, h = box
        n = len(items)
        cols = cols or n
        g = 1.5
        cw = (w - g * (cols - 1)) / cols
        rows = (n + cols - 1) // cols
        rh = (h - g * (rows - 1)) / rows
        for i, it in enumerate(items):
            cx, cy = x + (i % cols) * (cw + g), y + (i // cols) * (rh + g)
            inv = (invert == i) or it.get("invert", False)
            fg = self.card(s, cx, cy, cw, rh, fill=it.get("fill", fill), inverted=inv)
            yy = cy + 2.4
            if it.get("kicker"):
                self.kicker(s, cx + 1.6, yy, cw * .6, it["kicker"], color=fg or "accent")
            if it.get("chip"):
                chip_col = it.get("chip_color", "accent_2")
                self.rect(s, cx + cw - 10.5, yy - .6, 9, 4, fill=chip_col, radius=.5)
                self.text(s, cx + cw - 10.5, yy - .6, 9, 4, it["chip"], size=7, bold=True,
                          color="#FFFFFF", align="c", anchor="m", caps=True)
            if it.get("kicker") or it.get("chip"):
                yy += 4.5
            head_x = cx + 1.6
            if numbered:
                num = it.get("num", f"{i + 1:02d}")
                self.text(s, cx + 1.6, yy - .4, 5, 5, num, size=17, bold=True,
                          color=fg or "accent_2")
                if cols >= 4 or rh > 30:
                    yy += 5.5
                else:
                    head_x = cx + 6.4
            if it.get("value"):
                self.text(s, cx + 1.6, yy - .5, cw - 3.2, 8, it["value"], size=26, bold=True,
                          color=fg or it.get("value_color", "accent"))
                yy += 8.5
            if it.get("title"):
                self.text(s, head_x, yy, cx + cw - head_x - 1.6, 7, it["title"], size=12.5,
                          bold=True, color=fg or "ink", lh=1.0)
                yy += 6.2 if len(it["title"]) < 28 or cols <= 2 else 8.5
            body = it.get("body")
            if body:
                if isinstance(body, list):
                    body = "\n".join("• " + b for b in body)
                self.text(s, cx + 1.6, yy, cw - 3.2, max(4, cy + rh - yy - 9), body,
                          size=body_size, color=fg or "text", lh=1.15)
            if it.get("foot"):
                fy = cy + rh - 8.5
                self.rect(s, cx + 1.6, fy, cw - 3.2, .12, fill=fg or "line")
                if it.get("foot_kicker"):
                    self.kicker(s, cx + 1.6, fy + 1, cw - 3.2, it["foot_kicker"], color=fg or "muted")
                self.text(s, cx + 1.6, fy + 4, cw - 3.2, 4, it["foot"], size=9.5, bold=True,
                          color=fg or "ink")

    def table(self, s, box, header, rows, highlight_row=None, num_cols=None, bold_col=None,
              col_widths=None, kicker=None):
        x, y, w, h = box
        if kicker:
            self.kicker(s, x, y, w, kicker)
            y += 3.6
            h -= 3.6
        nr, nc = len(rows) + 1, len(header)
        gt = s.shapes.add_table(nr, nc, self.X(x), self.Y(y), self.X(w), self.Y(h))
        tbl = gt.table
        # strip default style
        tblPr = gt._element.graphic.graphicData.tbl.tblPr
        tblPr.set("firstRow", "0")
        tblPr.set("bandRow", "0")
        style = tblPr.find(qn("a:tableStyleId"))
        if style is not None:
            style.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"  # No Style, Table Grid
        num_cols = set(num_cols or [])
        if col_widths:
            tot = sum(col_widths)
            for j, cw in enumerate(col_widths):
                tbl.columns[j].width = self.X(w * cw / tot)
        rh = self.Y(h / nr)
        dense_header = self.name == "ledger"
        for i in range(nr):
            tbl.rows[i].height = rh
            for j in range(nc):
                cell = tbl.cell(i, j)
                val = header[j] if i == 0 else rows[i - 1][j]
                cell.margin_left = cell.margin_right = Emu(60000)
                cell.margin_top = cell.margin_bottom = Emu(20000)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                hl = (i - 1) == highlight_row and i > 0
                if i == 0:
                    fill = "ink" if dense_header else "bg"
                elif hl:
                    fill = "card_alt"
                else:
                    fill = "bg"
                cell.fill.solid()
                cell.fill.fore_color.rgb = rgb(self.c(fill))
                tf = cell.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.RIGHT if (j in num_cols) else PP_ALIGN.LEFT
                r = p.add_run()
                r.text = str(val)
                f = r.font
                f.name = self.font
                f.size = Pt(9 if i == 0 else 9.5)
                f.bold = i == 0 or hl or j == bold_col
                col = ("#FFFFFF" if dense_header else "ink") if i == 0 else (
                    "accent" if hl and j in num_cols else "text")
                f.color.rgb = rgb(self.c(col))
                self._cell_border(cell, bottom=self.c("ink") if i == 0 else self.c("line"),
                                  width=19050 if i == 0 else 6350)

    def _cell_border(self, cell, bottom, width):
        tcPr = cell._tc.get_or_add_tcPr()
        for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
            ln = etree.SubElement(tcPr, qn(tag))
            if tag == "a:lnB":
                ln.set("w", str(width))
                sf = etree.SubElement(ln, qn("a:solidFill"))
                c = etree.SubElement(sf, qn("a:srgbClr"))
                c.set("val", bottom.lstrip("#"))
            else:
                ln.set("w", "0")
                etree.SubElement(ln, qn("a:noFill"))

    def bars(self, s, box, categories, values, highlight=None, horizontal=False, kicker=None,
             fmt='0.0', neutral="#B9BFCB", series_name="Series", highlight_color="accent",
             labels=True):
        x, y, w, h = box
        if kicker:
            self.kicker(s, x, y, w, kicker)
            y += 3.6
            h -= 3.6
        cd = CategoryChartData()
        cd.categories = categories
        cd.add_series(series_name, values)
        ct = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
        gf = s.shapes.add_chart(ct, self.X(x), self.Y(y), self.X(w), self.Y(h), cd)
        ch = gf.chart
        ch.has_legend = False
        ch.has_title = False
        ch.font.name = self.font
        ch.font.size = Pt(9)
        ch.font.color.rgb = rgb(self.c("muted"))
        va = ch.value_axis
        va.visible = False
        va.has_major_gridlines = False
        ca = ch.category_axis
        ca.format.line.color.rgb = rgb(self.c("line"))
        ca.tick_labels.font.size = Pt(9)
        if horizontal:
            ca.reverse_order = True
        plot = ch.plots[0]
        plot.gap_width = 60
        ser = plot.series[0]
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = rgb(self.c(neutral))
        if labels:
            plot.has_data_labels = True
            dl = plot.data_labels
            dl.number_format = fmt
            dl.number_format_is_linked = False
            dl.position = XL_LABEL_POSITION.OUTSIDE_END
            dl.font.size = Pt(9)
            dl.font.bold = True
            dl.font.color.rgb = rgb(self.c("ink"))
        hl = highlight if isinstance(highlight, (list, tuple)) else (
            [] if highlight is None else [highlight])
        for i in hl:
            pt = ser.points[i]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = rgb(self.c(highlight_color))
        return ch

    def donut(self, s, box, labels, values, highlight=0, center=None, kicker=None):
        x, y, w, h = box
        if kicker:
            self.kicker(s, x, y, w, kicker)
            y += 3.6
            h -= 3.6
        cd = CategoryChartData()
        cd.categories = labels
        cd.add_series("Share", values)
        side = min(w * SLIDE_W / 100, h * SLIDE_H / 100)
        gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, self.X(x), self.Y(y),
                                Emu(int(side)), Emu(int(side)), cd)
        ch = gf.chart
        ch.has_legend = False
        ch.has_title = False
        ser = ch.plots[0].series[0]
        ramp = [self.c("accent"), mix(self.c("accent"), "#FFFFFF", .45), self.c("accent_2"),
                "#9EA3AE", "#CDD1D9", self.c("card_alt")]
        for i in range(len(values)):
            pt = ser.points[i]
            pt.format.fill.solid()
            col = ramp[0] if i == highlight else ramp[(i + (1 if i < highlight else 0)) % 6 or 3]
            pt.format.fill.fore_color.rgb = rgb(col)
            pt.format.line.color.rgb = rgb("#FFFFFF")
        hole = ch.plots[0]._element.find(qn("c:holeSize"))
        if hole is None:
            hole = etree.SubElement(ch.plots[0]._element, qn("c:holeSize"))
        hole.set("val", "62")
        side_pct_w = side / SLIDE_W * 100
        side_pct_h = side / SLIDE_H * 100
        if center:
            self.text(s, x, y + side_pct_h / 2 - 4, side_pct_w, 8, center, size=20, bold=True,
                      color="accent", align="c", anchor="m")
        # legend
        lx = x + side_pct_w + 1.5
        for i, (lab, v) in enumerate(zip(labels, values)):
            ly = y + 3 + i * 5
            col = ramp[0] if i == highlight else ramp[(i + (1 if i < highlight else 0)) % 6 or 3]
            self.rect(s, lx, ly + .8, 1.1, 2, fill=col, radius=.3)
            self.text(s, lx + 1.8, ly, max(5, x + w - lx - 2), 4, f"{lab} — **{v}**", size=9.5,
                      color="text", anchor="m")

    def steps(self, s, box, items):
        """Numbered rows separated by hairlines (next steps / plans)."""
        x, y, w, h = box
        n = len(items)
        rh = h / n
        for i, it in enumerate(items):
            yy = y + i * rh
            self.text(s, x, yy, 6, rh, f"{i + 1:02d}", size=18, bold=True, color="accent_2",
                      anchor="m")
            self.text(s, x + 7, yy, w - 7, rh, it, size=12, color="ink", anchor="m")
            if i < n - 1:
                self.rect(s, x, yy + rh - .1, w, .1, fill="line")

    def timeline(self, s, box, phases):
        """phases: [{"when","title","items":[...]}]"""
        x, y, w, h = box
        n = len(phases)
        g = 1.5
        cw = (w - g * (n - 1)) / n
        self.rect(s, x, y + 5.2, w, .25, fill="line")
        for i, ph in enumerate(phases):
            cx = x + i * (cw + g)
            col = "accent_2" if i == 0 else "accent"
            self.rect(s, cx, y + 4.3, 1.1, 2, fill=col, shape=MSO_SHAPE.OVAL)
            self.text(s, cx, y, cw, 3.5, ph["when"], size=8, bold=True, color=col, caps=True,
                      spacing=.5)
            self.card(s, cx, y + 8, cw, h - 8)
            self.text(s, cx + 1.4, y + 10, cw - 2.8, 6, ph["title"], size=12, bold=True,
                      color="ink", lh=1.0)
            self.text(s, cx + 1.4, y + 17, cw - 2.8, h - 19,
                      "\n".join("• " + t for t in ph.get("items", [])), size=9.5, color="text",
                      lh=1.1)

    def heat_strip(self, s, box, values, label=None, months="ЯФМАМИИАСОНД"):
        """12 cells coloured 0..3 (or any numbers, normalised)."""
        x, y, w, h = box
        ramp = ["#FDE7DA", "#F6BE9C", "#EC9063", "#D9622E"]
        lo, hi = min(values), max(values)
        lw = 14 if label else 0
        if label:
            self.text(s, x, y, lw - 1, h, label, size=9, bold=True, color="ink", anchor="m")
        cw = (w - lw) / 12
        for i, v in enumerate(values):
            k = 0 if hi == lo else round(3 * (v - lo) / (hi - lo))
            self.rect(s, x + lw + i * cw, y + h * .35, cw - .3, h * .65, fill=ramp[k])
            self.text(s, x + lw + i * cw, y, cw, h * .35, months[i], size=7, color="muted",
                      align="c")

    def ladder(self, s, box, rows, n=10, target=3, gap_header="GAP"):
        """rows: [{"label","sub"?,"pos":int|str,"gap":str}] — position on 1..n scale."""
        x, y, w, h = box
        lw, gw = 24, 18
        gx = x + lw
        gwid = w - lw - gw
        cw = gwid / n
        self.rect(s, gx, y + 3, cw * target, h - 3, fill="card_alt", radius=.05)
        self.text(s, gx, y + h + .3, cw * target, 3, f"1–{target}", size=8, bold=True,
                  color="accent", align="c")
        for k in range(n):
            self.text(s, gx + k * cw, y, cw, 3, str(k + 1), size=8, color="muted", align="c")
        self.kicker(s, x + w - gw + 1, y, gw, gap_header)
        rh = (h - 4) / len(rows)
        for i, r in enumerate(rows):
            yy = y + 4 + i * rh
            self.text(s, x, yy, lw - 1, rh * .6, r["label"], size=10, bold=True, color="ink",
                      anchor="m")
            if r.get("sub"):
                self.text(s, x, yy + rh * .52, lw - 1, rh * .4, r["sub"], size=7.5,
                          color="muted")
            self.rect(s, gx, yy + rh / 2 - .05, gwid, .1, fill="line")
            pos = r["pos"]
            p0 = float(str(pos).split("–")[0])
            cx = gx + (p0 - 1) * cw + cw / 2 - 1.2
            self.rect(s, cx, yy + rh / 2 - 2.1, 2.4, 4.2, fill="accent_2", shape=MSO_SHAPE.OVAL)
            self.text(s, cx - .5, yy + rh / 2 - 2.1, 3.4, 4.2, str(pos), size=8, bold=True,
                      color="#FFFFFF", align="c", anchor="m")
            self.text(s, x + w - gw + 1, yy, gw - 1, rh, r.get("gap", ""), size=9,
                      color="accent", bold=True, anchor="m")

    def callout(self, s, box, label, txt):
        x, y, w, h = box
        self.rect(s, x, y, w, h, fill="card_alt", radius=.12)
        self.kicker(s, x + 1.6, y + 1.2, w - 3.2, label, color="accent")
        self.text(s, x + 1.6, y + 4.4, w - 3.2, h - 5, txt, size=10.5, color="ink", bold=True)

    def old_new(self, s, box, old, new, was="было:", now="стало:"):
        x, y, w, h = box
        self.text(s, x + 8, y, 30, 4, was, size=11, color="muted")
        self.rect(s, x + 8, y + 5, w - 16, h * .28, fill="card", radius=.15)
        self.text(s, x + 10, y + 5, w - 20, h * .28, old, size=15, color="muted",
                  anchor="m", align="c", strike=True)
        self.text(s, x + w / 2 - 4, y + 5 + h * .28 + 1, 8, h * .16, "»", size=40, bold=True,
                  color="accent", align="c", anchor="m")
        y2 = y + 5 + h * .28 + 2 + h * .16
        self.text(s, x + 8, y2, 30, 4, now, size=11, color="accent", bold=True)
        self.rect(s, x + 8, y2 + 5, w - 16, h * .28, fill="card_alt", radius=.15)
        self.text(s, x + 10, y2 + 5, w - 20, h * .28, new, size=15, bold=True, color="ink",
                  anchor="m", align="c")

    def placeholder(self, s, box, caption):
        x, y, w, h = box
        self.rect(s, x, y, w, h, fill="card", radius=.06, line="line")
        self.text(s, x, y, w, h, caption, size=9, color="muted", align="c", anchor="m",
                  italic=True)

    def save(self, path):
        cp = self.prs.core_properties
        cp.author, cp.title, cp.comments, cp.last_modified_by = "", "", "", ""
        self.prs.save(path)
        return path
