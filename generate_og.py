#!/usr/bin/env python3
"""1200×630 share image from design A and the published research table."""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "docs" / "site-export" / "package-2026-10-01.json"
OUT = ROOT / "assets" / "og-image.png"
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

BG = (22, 13, 7, 255)
CARD = (34, 24, 16, 255)
TEXT = (247, 241, 227, 255)
MUTED = (188, 175, 156, 255)
ACCENT = (239, 182, 86, 255)
SILVER = (201, 187, 168, 255)
BRONZE = (176, 134, 85, 255)
BORDER = (76, 64, 53, 255)


def score_text(raw) -> str:
    d = Decimal(str(raw)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(d, ".2f")


def rounded(draw: ImageDraw.ImageDraw, xy, r, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def main() -> None:
    pkg = json.loads(PKG.read_text(encoding="utf-8"), parse_float=lambda x: x)
    rows = pkg["tables"]["research"]
    top = rows[:3]
    as_of = pkg["as_of"]
    y, m, d = as_of.split("-")
    months = {
        "01": "января",
        "10": "октября",
    }
    date_human = f"{int(d)} {months.get(m, m)} {y}"

    img = Image.new("RGBA", (1200, 630), BG)
    draw = ImageDraw.Draw(img)
    draw.ellipse((220, -260, 980, 280), fill=(239, 182, 86, 22))

    title_f = ImageFont.truetype(str(FONT_BOLD), 36)
    sub_f = ImageFont.truetype(str(FONT), 22)
    name_f = ImageFont.truetype(str(FONT_BOLD), 28)
    name1_f = ImageFont.truetype(str(FONT_BOLD), 32)
    score_f = ImageFont.truetype(str(FONT_BOLD), 40)
    score1_f = ImageFont.truetype(str(FONT_BOLD), 48)
    small_f = ImageFont.truetype(str(FONT), 18)
    mark_f = ImageFont.truetype(str(FONT_BOLD), 16)

    draw.text((64, 48), "РЕЙТИНГИ АВТОПРОКАТОВ", font=mark_f, fill=ACCENT)
    draw.text(
        (64, 88),
        "Топ компаний по аренде автомобилей",
        font=title_f,
        fill=TEXT,
    )
    draw.text(
        (64, 136),
        f"в Калининграде 2026  ·  исследование  ·  {date_human}",
        font=sub_f,
        fill=MUTED,
    )
    draw.text(
        (64, 172),
        f"{len(rows)} компаний  ·  места из среза, без пересчёта",
        font=small_f,
        fill=MUTED,
    )

    # Podium 2-1-3, real research places/scores.
    layout = [
        (top[1], 64, 248, 340, 310, SILVER, name_f, score_f),
        (top[0], 430, 228, 340, 350, ACCENT, name1_f, score1_f),
        (top[2], 796, 248, 340, 310, BRONZE, name_f, score_f),
    ]
    for row, x, y0, w, h, tone, nf, sf in layout:
        outline = tone if int(row["place"]) == 1 else BORDER
        rounded(draw, (x, y0, x + w, y0 + h), 28, CARD, outline=outline, width=2)
        place = int(row["place"])
        draw.text((x + 24, y0 + 22), f"Место {place}", font=small_f, fill=tone)
        draw.text((x + 24, y0 + 62), row["name"], font=nf, fill=TEXT)
        draw.text((x + 24, y0 + h - 78), score_text(row["score"]), font=sf, fill=tone)
        draw.text((x + 24, y0 + h - 32), "балл", font=small_f, fill=MUTED)

    draw.text(
        (64, 580),
        f"1-е место: {top[0]['name']}  ·  балл {score_text(top[0]['score'])} из 100",
        font=small_f,
        fill=MUTED,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(OUT, "PNG")
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
