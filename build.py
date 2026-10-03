#!/usr/bin/env python3
"""Static HTML from a published snapshot. No live scoring."""

from __future__ import annotations

import html
import json
import re
import shutil
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DOCS_EXPORT = ROOT / "docs" / "site-export"
PACKAGE_PATH = DOCS_EXPORT / "package-2026-10-01.json"
WORDSTAT_RANKING_MD = DOCS_EXPORT / "wordstat-ranking-table.md"
REVIEWS_RANKING_MD = DOCS_EXPORT / "reviews-ranking-table.md"
RESEARCH_RANKING_MD = DOCS_EXPORT / "research-ranking-table.md"
MONTHS = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}

TEX_SYMBOLS = {
    "mu": "μ",
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "pi": "π",
    "sigma": "σ",
    "infty": "∞",
    "times": "×",
    "pm": "±",
    "leq": "≤",
    "geq": "≥",
    "neq": "≠",
}

# Banner slot exists in layout (CSS comment). Empty → do not render markup.
BANNER_HTML = ""

# Production origin is later topautoprokat.ru. Empty = GitHub Pages preview:
# noindex, no sitemap, no canonical/og:url. Do not invent the live host here.
PROD_ORIGIN = ""
PREVIEW_ORIGIN = "https://miroformer.github.io/autoprokat-ratings-site"
SITE_NAME = "Рейтинги автопрокатов"
CITY_PREP = "Калининграде"
METRIKA_ID = "113370218"
OG_IMAGE = "assets/og-image.png"
SHARE_MARK = "assets/marks/shared.svg"
SHARE_MARK_32 = "assets/marks/shared-32.png"
SHARE_MARK_180 = "assets/marks/shared-180.png"

INDEX_PATHS = (
    "",
    "kaliningrad/",
    "kaliningrad/zaprosy/",
    "kaliningrad/otzyvy/",
    "metodika/",
)

PUBLIC_FILES = ("index.html", "404.html", "robots.txt")
PUBLIC_DIRS = ("assets", "kaliningrad", "metodika")

RESEARCH_PUBLISHED = True
SCORE_DECIMALS = {"research": 2, "wordstat": 1, "reviews": 1}

COMPANY_ID_RE = re.compile(r"^[a-z0-9-]+$")
SCORE_RE = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$")
MD_RANK_ROW_RE = re.compile(
    r"^\|\s*([1-9]\d*)\s*\|\s*([^|]+?)\s*\|\s*"
    r"(-?(?:0|[1-9]\d*)(?:\.\d+)?)\s*\|\s*$"
)
HTTP_URL_RE = re.compile(r"^https?://", re.I)

CSP = (
    "default-src 'self'; "
    "script-src 'self' https://mc.yandex.ru https://mc.yandex.com; "
    "img-src 'self' https://mc.yandex.ru https://mc.yandex.com; "
    "connect-src 'self' https://mc.yandex.ru https://mc.yandex.com "
    "wss://mc.yandex.ru wss://mc.yandex.com; "
    "child-src blob: https://mc.yandex.ru https://mc.yandex.com; "
    "frame-src blob: https://mc.yandex.ru https://mc.yandex.com; "
    "object-src 'none'; "
    "base-uri 'self'"
)

CUP = (
    '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M7 3h10v1.1c0 3.2-1.7 5.6-4.1 6.3L13 13h1.6a.6.6 0 0 1 0 1.2H9.4a.6.6 0 0 1 0-1.2H11l.1-2.6C8.7 9.7 7 7.3 7 4.1V3zm0 1.2H5.1A2.2 2.2 0 0 0 5.2 8.6c.8.4 1.7.7 2.7.8A5.6 5.6 0 0 1 7 4.2zm10 0v.2a5.6 5.6 0 0 1-.9 4.2c1-.1 1.9-.4 2.7-.8a2.2 2.2 0 0 0 .1-4.4H17zM10.6 16.2h2.8v2.2h-2.8zm-2.4 3.1h7.6c.4 0 .8.3.85.7l.1.5A1.2 1.2 0 0 1 15.6 22H8.4a1.2 1.2 0 0 1-1.15-1.5l.1-.5c.05-.4.45-.7.85-.7z"/>'
    "</svg>"
)
STAR = (
    '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M12 2.6 14.4 9H21l-5.3 4.1 2 6.5L12 16.4 6.3 19.6l2-6.5L3 9h6.6z"/>'
    "</svg>"
)
SEARCH = (
    '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">'
    '<circle cx="10.5" cy="10.5" r="6.2" fill="none" stroke="currentColor" stroke-width="2"/>'
    '<path fill="currentColor" d="M15.2 16.3 20 21.1l1.1-1.1-4.8-4.8z"/>'
    "</svg>"
)
REVIEWS_ICO = (
    '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M5 4.5h14A1.5 1.5 0 0 1 20.5 6v8A1.5 1.5 0 0 1 19 15.5h-6.2L8 19.2V15.5H5A1.5 1.5 0 0 1 3.5 14V6A1.5 1.5 0 0 1 5 4.5zm2.2 3.2v1.6h9.6V7.7zm0 3.4v1.6h6.4v-1.6z"/>'
    "</svg>"
)
BOOK = (
    '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M6 3.8h11.2A1.8 1.8 0 0 1 19 5.6v13.1c0 .7-.6 1.2-1.3 1.1-2.8-.4-5.2-.4-8.4.3-.4.1-.8-.2-.8-.6V5.6C8.5 4.6 7.4 3.9 6 3.8zm.7 1.7c.7.3 1.3.8 1.3 1.6v11.3c2.6-.5 5-.5 7.6-.1V5.7H6.7z"/>'
    "</svg>"
)
CAL = (
    '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M8 3.2h1.6V5H14.4V3.2H16V5h2.2A1.8 1.8 0 0 1 20 6.8V19a1.8 1.8 0 0 1-1.8 1.8H5.8A1.8 1.8 0 0 1 4 19V6.8A1.8 1.8 0 0 1 5.8 5H8V3.2zM5.8 9.2v9.6h12.4V9.2z"/>'
    "</svg>"
)
SHIELD = (
    '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M12 2.4 19.2 5v6.2c0 4.4-2.9 7.6-7.2 9.4-4.3-1.8-7.2-5-7.2-9.4V5zM8.7 12.1 11.1 14.5 16 8.9l-1.1-1-3.7 4.2-1.4-1.4z"/>'
    "</svg>"
)
LIST = (
    '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M5 6h2.2V8.2H5zm4 0h10v2.2H9zM5 11h2.2v2.2H5zm4 0h10v2.2H9zM5 16h2.2v2.2H5zm4 0h10v2.2H9z"/>'
    "</svg>"
)


def is_preview() -> bool:
    return not PROD_ORIGIN


def site_origin() -> str:
    return PROD_ORIGIN.rstrip("/") if PROD_ORIGIN else PREVIEW_ORIGIN


def url_base_path() -> str:
    return urlparse(site_origin()).path.rstrip("/")


def root_href(path: str) -> str:
    """Site-root URL. Needed on 404.html: the browser stays on the missing path."""
    base = url_base_path()
    if not path:
        return f"{base}/" if base else "/"
    return f"{base}/{path.lstrip('/')}"


def e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def format_date(as_of: str) -> str:
    y, m, d = as_of.split("-")
    return f"{int(d)} {MONTHS[int(m)]} {y}"


def title_base(as_of: str) -> str:
    return f"Топ компаний по аренде автомобилей в {CITY_PREP} {as_of[:4]}"


def format_score(score, decimals: int | None = None) -> str | None:
    """Number as text, or None → em dash at render. Never a raw non-numeric string."""
    if score is None or isinstance(score, bool):
        return None
    if isinstance(score, int):
        text = str(score)
    elif isinstance(score, float):
        if score != score or score in (float("inf"), float("-inf")):
            return None
        text = format(score, "f")
    elif isinstance(score, str):
        text = score.strip()
        if not SCORE_RE.fullmatch(text):
            return None
    else:
        return None
    if decimals is None:
        return text
    try:
        value = Decimal(text)
    except InvalidOperation:
        return None
    q = Decimal(10) ** -decimals
    return format(value.quantize(q, rounding=ROUND_HALF_UP), f".{decimals}f")


def company_id_of(row: dict) -> str | None:
    cid = row.get("company_id") or row.get("id")
    if not isinstance(cid, str):
        return None
    cid = cid.strip()
    if not COMPANY_ID_RE.fullmatch(cid):
        return None
    return cid


def place_of(row: dict):
    raw = row.get("place") if "place" in row else row.get("rank")
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw if raw > 0 else None
    if isinstance(raw, float):
        if raw != raw or not raw.is_integer() or raw <= 0:
            return None
        return int(raw)
    if isinstance(raw, str) and re.fullmatch(r"[1-9]\d*", raw.strip()):
        return int(raw.strip())
    return None


def card_of(row: dict) -> dict | None:
    card = row.get("card")
    if not isinstance(card, dict):
        return None
    pros = [p for p in (card.get("pros") or []) if p]
    cons = [c for c in (card.get("cons") or []) if c]
    if not pros and not cons:
        return None
    return {"pros": pros, "cons": cons}


def normalize_rows(raw_rows, kind: str) -> list[dict]:
    out = []
    for row in raw_rows or []:
        cid = company_id_of(row)
        name = row.get("name")
        place = place_of(row)
        if not cid or not name or place is None:
            continue
        out.append(
            {
                "company_id": cid,
                "name": name,
                "place": place,
                "score": row.get("score"),
                "card": card_of(row),
                "kind": kind,
            }
        )
    # Places as published. Do not reorder by score.
    out.sort(key=lambda r: r["place"])
    return out


def load_package() -> dict:
    if not PACKAGE_PATH.is_file():
        raise FileNotFoundError(f"missing snapshot {PACKAGE_PATH}")
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"), parse_float=lambda x: x)


def parse_ranking_table(path: Path) -> list[dict]:
    """Places and scores from a ranking markdown table. Tokens as written."""
    if path.name == "ranking-table.md":
        raise ValueError("ranking-table.md is the same reviews list; do not use")
    text = path.read_text(encoding="utf-8")
    out: list[dict] = []
    seen: set[int] = set()
    for line in text.splitlines():
        m = MD_RANK_ROW_RE.match(line.strip())
        if not m:
            continue
        place = int(m.group(1))
        name = m.group(2).strip()
        score = m.group(3)
        if not name:
            continue
        if place in seen:
            raise ValueError(f"duplicate place {place} in {path.name}")
        seen.add(place)
        out.append(
            {
                "name": name,
                "place": place,
                "score": score,
                "card": None,
            }
        )
    out.sort(key=lambda r: r["place"])
    if not out:
        raise ValueError(f"no ranking rows in {path}")
    return out


def css_href(depth: int, *, rooted: bool = False) -> str:
    if rooted:
        return root_href("assets/style.css")
    return "../" * depth + "assets/style.css"


def asset_href(depth: int, path: str, *, rooted: bool = False) -> str:
    if rooted:
        return root_href(path)
    return "../" * depth + path


def href(depth: int, path: str, *, rooted: bool = False) -> str:
    if rooted:
        return root_href(path)
    if path == "":
        return "./" if depth == 0 else "../" * depth
    return "../" * depth + path


def abs_url(path: str) -> str:
    origin = site_origin()
    if not path:
        return origin + "/"
    return origin + "/" + path.lstrip("/")


def header(depth: int, active: str, date_human: str, *, rooted: bool = False) -> str:
    items = [
        ("home", href(depth, "", rooted=rooted), "Оглавление"),
        ("hub", href(depth, "kaliningrad/", rooted=rooted), "Калининград"),
        ("zaprosy", href(depth, "kaliningrad/zaprosy/", rooted=rooted), "Запросы"),
        ("otzyvy", href(depth, "kaliningrad/otzyvy/", rooted=rooted), "Отзывы"),
        ("metodika", href(depth, "metodika/", rooted=rooted), "Методика"),
    ]
    pills = []
    for key, url, label in items:
        cls = "pill is-active" if key == active else "pill"
        pills.append(f'<a class="{cls}" href="{e(url)}">{e(label)}</a>')
    mark = asset_href(depth, SHARE_MARK, rooted=rooted)
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{e(href(depth, "", rooted=rooted))}">
      <span class="logo-tile"><img src="{e(mark)}" width="36" height="36" alt=""></span>
      <span class="brand-text">
        <span class="brand-name">{e(SITE_NAME)}</span>
        <span class="brand-sub">на {e(date_human)}</span>
      </span>
    </a>
    <nav class="pill-nav" aria-label="Разделы">{"".join(pills)}</nav>
  </div>
</header>"""


def footer(depth: int, *, rooted: bool = False) -> str:
    return f"""<footer class="site-footer">
  <div class="wrap">
    Витрина публикует готовые рейтинги, здесь их не считает.
    <a href="{e(href(depth, "metodika/", rooted=rooted))}">Методика</a>.
  </div>
</footer>"""


def metrika_html(depth: int, *, rooted: bool = False) -> str:
    src = asset_href(depth, "assets/metrika.js", rooted=rooted)
    watch = f"https://mc.yandex.ru/watch/{METRIKA_ID}"
    return (
        "<!-- Yandex.Metrika counter -->\n"
        f'<script type="text/javascript" src="{e(src)}"></script>\n'
        f'<noscript><div><img class="ym-noscript" src="{e(watch)}" alt=""></div></noscript>\n'
        "<!-- /Yandex.Metrika counter -->"
    )


def ranking_description(kind: str, date_human: str, rows: list[dict], as_of: str) -> str:
    """Description from published table facts only. No 'лучший', no invented ranks."""
    year = as_of[:4]
    if kind == "research":
        lead = (
            f"Топ компаний по аренде автомобилей в {CITY_PREP} {year}. "
            f"Исследование. На {date_human}."
        )
    elif kind == "zaprosy":
        lead = (
            f"Топ компаний по аренде автомобилей в {CITY_PREP} {year} — запросы. "
            f"Рейтинг по брендовым поисковым запросам. На {date_human}."
        )
    elif kind == "otzyvy":
        lead = (
            f"Топ компаний по аренде автомобилей в {CITY_PREP} {year} — отзывы. "
            f"Рейтинг по картам и отзывам. На {date_human}."
        )
    else:
        raise ValueError(f"unknown ranking kind {kind}")
    parts = [lead]
    if rows:
        parts.append(f"В рейтинге {len(rows)} компаний.")
        parts.append(f"1-е место: {rows[0]['name']}.")
    if kind == "zaprosy":
        parts.append("100 — наибольший спрос в этом срезе.")
    return " ".join(parts)


def head_tags(
    *,
    title: str,
    description: str,
    canonical_path: str,
    indexable: bool,
    depth: int,
    rooted: bool,
) -> str:
    tags = [
        f'<meta http-equiv="Content-Security-Policy" content="{CSP}">',
    ]
    preview = is_preview()
    closed = preview or not indexable
    if closed:
        tags.append('<meta name="robots" content="noindex, nofollow">')
    loc = abs_url(canonical_path)
    if not preview and indexable and PROD_ORIGIN:
        tags.append(f'<link rel="canonical" href="{e(loc)}">')
        tags.append(f'<meta property="og:url" content="{e(loc)}">')
    image = abs_url(OG_IMAGE)
    icon = asset_href(depth, SHARE_MARK, rooted=rooted)
    icon32 = asset_href(depth, SHARE_MARK_32, rooted=rooted)
    icon180 = asset_href(depth, SHARE_MARK_180, rooted=rooted)
    tags.extend(
        [
            f'<link rel="icon" href="{e(icon)}" type="image/svg+xml">',
            f'<link rel="icon" href="{e(icon32)}" sizes="32x32" type="image/png">',
            f'<link rel="apple-touch-icon" href="{e(icon180)}">',
            f"<title>{e(title)}</title>",
            f'<meta name="description" content="{e(description)}">',
            f'<meta property="og:title" content="{e(title)}">',
            f'<meta property="og:description" content="{e(description)}">',
            '<meta property="og:type" content="website">',
            '<meta property="og:locale" content="ru_RU">',
            f'<meta property="og:site_name" content="{e(SITE_NAME)}">',
            f'<meta property="og:image" content="{e(image)}">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            '<meta property="og:image:type" content="image/png">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{e(title)}">',
            f'<meta name="twitter:description" content="{e(description)}">',
            f'<meta name="twitter:image" content="{e(image)}">',
        ]
    )
    return "\n  ".join(tags)


def page(
    depth: int,
    title: str,
    active: str,
    date_human: str,
    body: str,
    *,
    description: str,
    canonical_path: str,
    indexable: bool = True,
    rooted: bool = False,
) -> str:
    extra_head = head_tags(
        title=title,
        description=description,
        canonical_path=canonical_path,
        indexable=indexable,
        depth=depth,
        rooted=rooted,
    )
    banner = BANNER_HTML.strip()
    banner_block = f"{banner}\n" if banner else ""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {extra_head}
  <link rel="stylesheet" href="{e(css_href(depth, rooted=rooted))}">
</head>
<body>
{banner_block}{header(depth, active, date_human, rooted=rooted)}
<main class="wrap">
{body}
</main>
{footer(depth, rooted=rooted)}
{metrika_html(depth, rooted=rooted)}
</body>
</html>
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def stage_public(dest: Path) -> Path:
    """Copy only public HTML/CSS/assets. Snapshot JSON and docs stay out."""
    dest = dest.resolve()
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    (dest / ".nojekyll").write_text("", encoding="utf-8")
    for name in PUBLIC_FILES:
        src = ROOT / name
        if not src.is_file():
            raise FileNotFoundError(f"missing public file {name}")
        shutil.copy2(src, dest / name)
    for name in PUBLIC_DIRS:
        src = ROOT / name
        if not src.is_dir():
            raise FileNotFoundError(f"missing public dir {name}")
        shutil.copytree(src, dest / name)
    forbidden = []
    for pattern in ("*.json", "*ranking-table.md", "sitemap.xml"):
        forbidden.extend(dest.rglob(pattern))
    for name in ("data", "docs", "media", "mockups"):
        if (dest / name).exists():
            forbidden.append(dest / name)
    if list(dest.rglob("*a-tile*")) or list(dest.rglob("a-32.png")) or list(dest.rglob("a-180.png")):
        forbidden.extend(dest.rglob("*a-tile*"))
        forbidden.extend(dest.rglob("a-32.png"))
        forbidden.extend(dest.rglob("a-180.png"))
    if forbidden:
        names = ", ".join(str(p.relative_to(dest)) for p in forbidden)
        raise RuntimeError(f"non-public files staged: {names}")
    return dest


def write_robots() -> None:
    if is_preview():
        write(ROOT / "robots.txt", "User-agent: *\nDisallow: /\n")
        return
    write(
        ROOT / "robots.txt",
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {site_origin()}/sitemap.xml\n",
    )


def write_sitemap(as_of: str) -> None:
    path = ROOT / "sitemap.xml"
    if is_preview():
        if path.exists():
            path.unlink()
        return
    blocks = []
    for url_path in INDEX_PATHS:
        blocks.append(
            "  <url>\n"
            f"    <loc>{e(abs_url(url_path))}</loc>\n"
            f"    <lastmod>{e(as_of)}</lastmod>\n"
            "  </url>"
        )
    write(
        path,
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(blocks)
        + "\n</urlset>\n",
    )


def depth_pills() -> str:
    return f"""<nav class="depth-pills" aria-label="Глубина списка">
  <a class="pill" href="#top-3">{CUP}Топ-3</a>
  <a class="pill" href="#top-5">Топ-5</a>
  <a class="pill" href="#top-10">Топ-10</a>
</nav>"""


def top3_html(rows: list[dict], kind: str) -> str:
    decimals = SCORE_DECIMALS[kind]
    cards = []
    for row in rows[:3]:
        score = format_score(row["score"], decimals)
        score_html = f'<div class="place-score">{e(score)}</div>' if score is not None else ""
        p = int(row["place"])
        extra = (
            '<span class="stars" aria-hidden="true">' + STAR * 3 + "</span>" if p == 1 else ""
        )
        cards.append(
            f'<article class="card place-card" data-p="{p}">'
            f'<div class="place-head"><div class="place-num">Место {e(p)}</div>'
            f'<span class="trophy">{CUP}</span></div>'
            f'<div class="place-name">{e(row["name"])}</div>{extra}'
            f"{score_html}"
            f'<div class="score-label">балл</div></article>'
        )
    return f'<section id="top-3" class="top3">{"".join(cards)}</section>'


def trust_html(depth: int, date_human: str) -> str:
    return f"""<section class="card trust">
  <div class="trust-row">
    <div class="trust-item">{CAL}<p>На {e(date_human)}.</p></div>
    <div class="trust-item">{SHIELD}<p>Места в таблице не продаются. Таблица — не реклама.</p></div>
    <div class="trust-item">{BOOK}<p><a href="{e(href(depth, "metodika/"))}">Как считали</a></p></div>
  </div>
</section>"""


def cards_html(rows: list[dict]) -> str:
    articles = []
    for row in rows[:10]:
        card = row.get("card")
        if not card:
            continue
        parts = [f'<article class="card desc-card"><h3>{e(row["place"])}. {e(row["name"])}</h3>']
        if card["pros"]:
            items = "".join(f"<li>{e(p)}</li>" for p in card["pros"])
            parts.append(f"<p>Плюсы</p><ul>{items}</ul>")
        if card["cons"]:
            items = "".join(f"<li>{e(c)}</li>" for c in card["cons"])
            parts.append(f"<p>Минусы</p><ul>{items}</ul>")
        parts.append("</article>")
        articles.append("".join(parts))
    if not articles:
        return ""
    return f'<section id="cards-top-10" class="cards">{"".join(articles)}</section>'


def table_html(rows: list[dict], kind: str, note: str | None = None) -> str:
    if not rows:
        return ""
    decimals = SCORE_DECIMALS[kind]
    body_rows = []
    for row in rows:
        row_id = ""
        if row["place"] == 5:
            row_id = ' id="top-5"'
        elif row["place"] == 10:
            row_id = ' id="top-10"'
        score = format_score(row["score"], decimals)
        score_cell = e(score) if score is not None else "—"
        top_cls = ' class="is-top"' if row["place"] <= 3 else ""
        cup = CUP if row["place"] <= 3 else ""
        body_rows.append(
            f"<tr{top_cls}{row_id}><td class=\"num\"><span class=\"rank\">{cup}{e(row['place'])}</span></td>"
            f"<td>{e(row['name'])}</td>"
            f"<td class=\"num\">{score_cell}</td></tr>"
        )
    note_html = note or "Места в таблице не продаются. Таблица — не реклама."
    return f"""<section class="card table-block" id="full-list">
  <h2>{CUP} Полный список</h2>
  <div class="table-scroll">
    <table>
      <thead><tr><th class="num">Место</th><th>Компания</th><th class="num">Балл</th></tr></thead>
      <tbody>
        {"".join(body_rows)}
      </tbody>
    </table>
  </div>
  <p class="table-note">{e(note_html)}</p>
</section>"""


def ranking_body(
    depth: int,
    kicker: str,
    heading: str,
    lead: str,
    rows: list[dict],
    date_human: str,
    kind: str,
    extra: str = "",
    table_note: str | None = None,
    kicker_icon: str = "",
    facts: str = "",
) -> str:
    first = rows[0] if rows else None
    first_line = ""
    if first:
        score = format_score(first["score"], SCORE_DECIMALS[kind])
        score_bit = f", балл {score}" if score is not None else ""
        first_line = f" 1-е место: {e(first['name'])}{e(score_bit)}."
    kicker_html = (
        f'<p class="kicker-row">{kicker_icon}<span>{e(kicker)}</span></p>'
        if kicker_icon
        else f'<p class="kicker">{e(kicker)}</p>'
    )
    return f"""{kicker_html}
<h1>{e(heading)}</h1>
<p class="lead">{e(lead)}{first_line}</p>
{facts}
{depth_pills()}
{top3_html(rows, kind)}
{trust_html(depth, date_human)}
{cards_html(rows)}
{table_html(rows, kind, table_note)}
{extra}"""


def md_inline(text: str) -> str:
    parts: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", text[i:])
        if m:
            label, url = m.group(1), m.group(2).strip()
            if HTTP_URL_RE.match(url) and "javascript:" not in url.lower():
                parts.append(f'<a href="{e(url)}" rel="nofollow noopener">{e(label)}</a>')
            else:
                parts.append(e(label))
            i += m.end()
            continue
        m = re.match(r"\*\*(.+?)\*\*", text[i:])
        if m:
            parts.append(f"<strong>{e(m.group(1))}</strong>")
            i += m.end()
            continue
        m = re.match(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", text[i:])
        if m:
            parts.append(f"<em>{e(m.group(1))}</em>")
            i += m.end()
            continue
        m = re.match(r"`([^`]+)`", text[i:])
        if m:
            parts.append(f"<code>{e(m.group(1))}</code>")
            i += m.end()
            continue
        parts.append(e(text[i]))
        i += 1
    return "".join(parts)


def tex_to_html(tex: str) -> str:
    s = tex.strip()
    n = len(s)
    i = 0
    out: list[str] = []

    def parse_group() -> str:
        nonlocal i
        if i >= n or s[i] != "{":
            return ""
        i += 1
        start = i
        depth = 1
        while i < n and depth:
            if s[i] == "{":
                depth += 1
            elif s[i] == "}":
                depth -= 1
            i += 1
        return tex_to_html(s[start : i - 1])

    while i < n:
        if s.startswith(r"\frac", i):
            i += 5
            while i < n and s[i].isspace():
                i += 1
            num = parse_group()
            while i < n and s[i].isspace():
                i += 1
            den = parse_group()
            out.append(
                '<span class="frac">'
                f'<span class="frac-num">{num}</span>'
                f'<span class="frac-den">{den}</span>'
                "</span>"
            )
            continue
        if s.startswith(r"\mathrm", i):
            i += 7
            while i < n and s[i].isspace():
                i += 1
            out.append(f'<span class="mathrm">{parse_group()}</span>')
            continue
        if s.startswith(r"\ln", i) and (i + 3 == n or not s[i + 3].isalpha()):
            i += 3
            out.append('<span class="mathrm">ln</span>')
            continue
        if s.startswith(r"\sum", i):
            i += 4
            out.append("∑")
            continue
        if s.startswith(r"\cdot", i):
            i += 5
            while i < n and s[i].isspace():
                i += 1
            out.append("·")
            continue
        if s.startswith(r"\bigl", i) or s.startswith(r"\bigr", i):
            i += 5
            continue
        if s.startswith(r"\qquad", i):
            i += 6
            out.append('<span class="math-gap"></span>')
            continue
        if s.startswith(r"\,", i):
            i += 2
            out.append("\u2009")
            continue
        if s[i] == "_" and i + 1 < n:
            i += 1
            if s[i] == "{":
                out.append(f"<sub>{parse_group()}</sub>")
            else:
                out.append(f"<sub>{e(s[i])}</sub>")
                i += 1
            continue
        if s.startswith("{,}", i):
            i += 3
            out.append(",")
            continue
        if s[i] == "{":
            out.append(parse_group())
            continue
        if s[i] == "\\":
            i += 1
            m = re.match(r"[A-Za-z]+", s[i:])
            if m:
                name = m.group(0)
                i += len(name)
                out.append(e(TEX_SYMBOLS.get(name, name)))
            elif i < n:
                out.append(e(s[i]))
                i += 1
            continue
        j = i
        while j < n and s[j] not in "\\_{}":
            j += 1
        out.append(e(s[i:j]))
        i = j
    return "".join(out)


def formula_html(tex: str, display: bool) -> str:
    inner = tex_to_html(tex)
    cls = "formula" if display else "formula inline"
    return f'<span class="{cls}" role="math">{inner}</span>'


def md_table_html(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and re.match(r"^:?-{3,}:?$", cells[0].replace(" ", "")):
            continue
        if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells if c):
            continue
        rows.append(cells)
    if not rows:
        return ""
    head, body = rows[0], rows[1:]
    thead = "".join(f"<th>{md_inline(c)}</th>" for c in head)
    body_html = []
    for row in body:
        padded = row + [""] * (len(head) - len(row))
        tds = "".join(f"<td>{md_inline(c)}</td>" for c in padded[: len(head)])
        body_html.append(f"<tr>{tds}</tr>")
    return (
        '<div class="table-scroll"><table>'
        f"<thead><tr>{thead}</tr></thead>"
        f"<tbody>{''.join(body_html)}</tbody>"
        "</table></div>"
    )


def md_to_html(src: str) -> str:
    src = src.replace("\r\n", "\n").strip()
    chunks: list[str] = []

    def take_math(match: re.Match) -> str:
        inner = match.group(1).strip()
        idx = len(chunks)
        display = match.group(0).startswith("\\[")
        chunks.append(formula_html(inner, display))
        return f"@@MATH{idx}@@"

    src = re.sub(r"\\\[(.+?)\\\]", take_math, src, flags=re.S)
    src = re.sub(r"\\\((.+?)\\\)", take_math, src)

    parts: list[str] = []
    list_buf: list[str] = []
    list_type: str | None = None
    table_buf: list[str] = []
    quote_buf: list[str] = []

    def flush_list() -> None:
        nonlocal list_buf, list_type
        if not list_buf:
            return
        tag = list_type or "ul"
        items = "".join(f"<li>{md_inline(x)}</li>" for x in list_buf)
        parts.append(f"<{tag}>{items}</{tag}>")
        list_buf = []
        list_type = None

    def flush_table() -> None:
        nonlocal table_buf
        if not table_buf:
            return
        parts.append(md_table_html(table_buf))
        table_buf = []

    def flush_quote() -> None:
        nonlocal quote_buf
        if not quote_buf:
            return
        inner = md_to_html("\n".join(quote_buf))
        parts.append(f"<blockquote>{inner}</blockquote>")
        quote_buf = []

    def flush_all() -> None:
        flush_list()
        flush_table()
        flush_quote()

    for raw in src.split("\n"):
        line = raw.rstrip()
        if line.startswith("> "):
            flush_list()
            flush_table()
            quote_buf.append(line[2:])
            continue
        if line == ">":
            flush_list()
            flush_table()
            quote_buf.append("")
            continue
        if quote_buf:
            flush_quote()
        if line.startswith("|") and line.endswith("|"):
            flush_list()
            table_buf.append(line)
            continue
        if table_buf:
            flush_table()
        if not line.strip():
            flush_list()
            continue
        if line.startswith("# "):
            flush_all()
            parts.append(f"<h2>{md_inline(line[2:])}</h2>")
            continue
        if line.startswith("## "):
            flush_all()
            parts.append(f"<h2>{md_inline(line[3:])}</h2>")
            continue
        if line.startswith("### "):
            flush_all()
            parts.append(f"<h3>{md_inline(line[4:])}</h3>")
            continue
        m_ul = re.match(r"^[-*] (.+)$", line)
        if m_ul:
            if list_type == "ol":
                flush_list()
            list_type = "ul"
            list_buf.append(m_ul.group(1))
            continue
        m_ol = re.match(r"^\d+\. (.+)$", line)
        if m_ol:
            if list_type == "ul":
                flush_list()
            list_type = "ol"
            list_buf.append(m_ol.group(1))
            continue
        flush_list()
        parts.append(f"<p>{md_inline(line)}</p>")
    flush_all()
    html_out = "\n".join(parts)
    for i, chunk in enumerate(chunks):
        html_out = html_out.replace(f"@@MATH{i}@@", chunk)
    return html_out


def package_markdown(pkg: dict, key: str) -> str:
    block = pkg.get(key) or {}
    md = block.get("markdown") if isinstance(block, dict) else None
    if not isinstance(md, str) or not md.strip():
        raise ValueError(f"package.{key}.markdown missing")
    return md


def side_links(depth: int) -> str:
    cards = [
        (href(depth, "kaliningrad/zaprosy/"), "Брендовые запросы", "Рейтинг по поисковым запросам.", SEARCH),
        (href(depth, "kaliningrad/otzyvy/"), "Отзовики", "Рейтинг по картам и отзывам.", REVIEWS_ICO),
        (href(depth, "metodika/"), "Методика", "Как считали исследование, запросы и отзовики.", BOOK),
    ]
    links = []
    for url, title, text, ico in cards:
        links.append(
            f'<a class="card link-card" href="{e(url)}">'
            f'<span class="link-ico">{ico}</span>'
            f"<span><h2>{e(title)}</h2><p>{e(text)}</p></span>"
            f'<span class="go" aria-hidden="true">→</span></a>'
        )
    return f'<section class="link-grid">{"".join(links)}</section>'


def build_home(pkg: dict, date_human: str, research: list[dict]) -> str:
    as_of = pkg["as_of"]
    first = research[0]["name"] if research else ""
    body = f"""<p class="kicker">Оглавление</p>
<h1>{e(title_base(as_of))}</h1>
<p class="lead">Готовые рейтинги Калининграда. Федерального топа нет. На {e(date_human)}.</p>
<section class="toc-grid">
  <a class="card link-card" href="{e(href(0, "kaliningrad/"))}">
    <span class="link-ico">{CUP}</span>
    <span>
      <h2>Калининград — исследование</h2>
      <p>На {e(date_human)}. {e(len(research))} компаний. 1-е место: {e(first)}.</p>
    </span>
    <span class="go" aria-hidden="true">→</span>
  </a>
  <a class="card link-card" href="{e(href(0, "kaliningrad/zaprosy/"))}">
    <span class="link-ico">{SEARCH}</span>
    <span>
      <h2>Брендовые запросы</h2>
      <p>Рейтинг по поисковым запросам. 100 — наибольший спрос в этом срезе.</p>
    </span>
    <span class="go" aria-hidden="true">→</span>
  </a>
  <a class="card link-card" href="{e(href(0, "kaliningrad/otzyvy/"))}">
    <span class="link-ico">{REVIEWS_ICO}</span>
    <span>
      <h2>Отзовики</h2>
      <p>Рейтинг по картам и отзывам. На {e(date_human)}.</p>
    </span>
    <span class="go" aria-hidden="true">→</span>
  </a>
  <a class="card link-card" href="{e(href(0, "metodika/"))}">
    <span class="link-ico">{BOOK}</span>
    <span>
      <h2>Методика</h2>
      <p>Как считали исследование, запросы и отзовики.</p>
    </span>
    <span class="go" aria-hidden="true">→</span>
  </a>
</section>"""
    return page(
        0,
        f"{title_base(as_of)} — оглавление",
        "home",
        date_human,
        body,
        description=(
            f"Топ компаний по аренде автомобилей в {CITY_PREP} {as_of[:4]}. "
            f"Оглавление. Калининград, на {date_human}. Федерального топа нет."
        ),
        canonical_path="",
    )


def build_hub(pkg: dict, date_human: str, research: list[dict]) -> str:
    as_of = pkg["as_of"]
    article = md_to_html(package_markdown(pkg, "article"))
    authors = md_to_html(package_markdown(pkg, "authors"))
    extra = (
        f'<section class="card article" id="statya">{article}</section>'
        f'<section class="card authors" id="avtory">{authors}</section>'
        f"{side_links(1)}"
    )
    facts = f"""<ul class="facts">
  <li>{CAL} Срез {e(date_human)}</li>
  <li>{LIST} {e(len(research))} компаний в исследовании</li>
  <li>{CUP} 1-е место: {e(research[0]["name"]) if research else "—"}</li>
</ul>"""
    body = ranking_body(
        1,
        "Исследование",
        title_base(as_of),
        f"На {date_human}. Рейтинг-исследование.",
        research,
        date_human,
        "research",
        extra=extra,
        facts=facts,
    )
    return page(
        1,
        f"{title_base(as_of)} — исследование",
        "hub",
        date_human,
        body,
        description=ranking_description("research", date_human, research, as_of),
        canonical_path="kaliningrad/",
    )


def build_metodika(date_human: str, method_version: str | None, as_of: str) -> str:
    research = md_to_html((DOCS_EXPORT / "method-description.md").read_text(encoding="utf-8"))
    wordstat = md_to_html(
        (DOCS_EXPORT / "wordstat-method-description.md").read_text(encoding="utf-8")
    )
    reviews = md_to_html(
        (DOCS_EXPORT / "reviews-method-description.md").read_text(encoding="utf-8")
    )
    body = f"""<p class="kicker">Методика</p>
<h1>Как считали</h1>
<p class="lead">На {e(date_human)}.</p>
<section class="card method" id="issledovanie">
{research}
</section>
<section class="card method" id="zaprosy">
{wordstat}
</section>
<section class="card method" id="otzyvy">
{reviews}
</section>"""
    version_bit = f" Версия методики {method_version}." if method_version else ""
    return page(
        1,
        f"{title_base(as_of)} — методика",
        "metodika",
        date_human,
        body,
        description=(
            f"Топ компаний по аренде автомобилей в {CITY_PREP} {as_of[:4]} — методика. "
            f"Как считали исследование, запросы и отзовики. На {date_human}.{version_bit}"
        ),
        canonical_path="metodika/",
    )


def build_404(date_human: str, as_of: str) -> str:
    home = href(0, "", rooted=True)
    body = f"""<p class="kicker">Ошибка</p>
<h1>Страница не найдена</h1>
<p class="lead">Такой страницы нет. <a href="{e(home)}">К оглавлению</a>.</p>"""
    return page(
        0,
        "Страница не найдена",
        "home",
        date_human,
        body,
        description="Такой страницы нет.",
        canonical_path="",
        indexable=False,
        rooted=True,
    )


def main() -> None:
    pkg = load_package()
    if pkg.get("as_of") != "2026-10-01":
        raise ValueError(f"unexpected as_of {pkg.get('as_of')}")
    date_human = format_date(pkg["as_of"])
    tables = pkg.get("tables") or {}
    if RESEARCH_PUBLISHED and "research" not in tables:
        raise ValueError("research table missing from published package")

    research = normalize_rows(tables.get("research"), "research")
    wordstat = normalize_rows(tables.get("wordstat"), "wordstat")
    reviews = normalize_rows(tables.get("reviews"), "reviews")
    if not research or not wordstat or not reviews:
        raise ValueError("published tables must not be empty")

    write(ROOT / "index.html", build_home(pkg, date_human, research))
    write(ROOT / "kaliningrad" / "index.html", build_hub(pkg, date_human, research))
    method_version = pkg.get("methodology_version")
    if not isinstance(method_version, str) or not method_version.strip():
        method_version = None
    else:
        method_version = method_version.strip()

    write(
        ROOT / "kaliningrad" / "zaprosy" / "index.html",
        page(
            2,
            f"{title_base(pkg['as_of'])} — запросы",
            "zaprosy",
            date_human,
            ranking_body(
                2,
                "Рейтинг брендовых запросов",
                f"{title_base(pkg['as_of'])} — запросы",
                f"На {date_human}. 100 — наибольший спрос в этом срезе.",
                wordstat,
                date_human,
                "wordstat",
                table_note=(
                    "Места в таблице не продаются. Таблица — не реклама. "
                    "100 — наибольший спрос в этом срезе."
                ),
                kicker_icon=SEARCH,
            ),
            description=ranking_description("zaprosy", date_human, wordstat, pkg["as_of"]),
            canonical_path="kaliningrad/zaprosy/",
        ),
    )
    write(
        ROOT / "kaliningrad" / "otzyvy" / "index.html",
        page(
            2,
            f"{title_base(pkg['as_of'])} — отзывы",
            "otzyvy",
            date_human,
            ranking_body(
                2,
                "Рейтинг по отзовикам",
                f"{title_base(pkg['as_of'])} — отзывы",
                f"На {date_human}.",
                reviews,
                date_human,
                "reviews",
                kicker_icon=REVIEWS_ICO,
            ),
            description=ranking_description("otzyvy", date_human, reviews, pkg["as_of"]),
            canonical_path="kaliningrad/otzyvy/",
        ),
    )
    write(ROOT / "metodika" / "index.html", build_metodika(date_human, method_version, pkg["as_of"]))
    write(ROOT / "404.html", build_404(date_human, pkg["as_of"]))
    write_robots()
    write_sitemap(pkg["as_of"])
    print(
        "built",
        pkg["as_of"],
        len(research),
        "research,",
        len(wordstat),
        "wordstat,",
        len(reviews),
        "reviews",
    )


if __name__ == "__main__":
    main()
