#!/usr/bin/env python3
"""Static HTML from a published snapshot. No live scoring."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "site-export"
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

# Banner slot exists in layout (CSS comment). Empty → do not render.
BANNER_HTML = ""


def e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def format_date(as_of: str) -> str:
    y, m, d = as_of.split("-")
    return f"{int(d)} {MONTHS[int(m)]} {y}"


def format_score(score) -> str | None:
    if score is None:
        return None
    if isinstance(score, bool):
        return None
    if isinstance(score, str):
        return score
    if isinstance(score, (int, float)):
        return json.dumps(score)
    return None


def company_id_of(row: dict) -> str | None:
    return row.get("company_id") or row.get("id")


def place_of(row: dict):
    if "place" in row:
        return row.get("place")
    return row.get("rank")


def card_of(row: dict) -> dict | None:
    card = row.get("card")
    if not isinstance(card, dict):
        return None
    pros = [p for p in (card.get("pros") or []) if p]
    cons = [c for c in (card.get("cons") or []) if c]
    if not pros and not cons:
        return None
    return {"pros": pros, "cons": cons}


def normalize_rows(raw_rows) -> list[dict]:
    out = []
    for row in raw_rows or []:
        cid = company_id_of(row)
        name = row.get("name")
        place = place_of(row)
        if not cid or not name or place is None:
            continue
        item = {
            "company_id": cid,
            "name": name,
            "place": place,
            "score": row.get("score"),
            "card": card_of(row),
        }
        out.append(item)
    out.sort(key=lambda r: (r["place"], r["name"]))
    return out


def load_package() -> dict:
    path = DATA / "package-2026-09-26.json"
    return json.loads(path.read_text(encoding="utf-8"), parse_float=lambda x: x)


def css_href(depth: int) -> str:
    return "../" * depth + "assets/style.css"


def href(depth: int, path: str) -> str:
    if path == "":
        return "./" if depth == 0 else "../" * depth
    return "../" * depth + path


def logo_svg() -> str:
    return (
        '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">'
        '<rect x="3" y="11" width="3" height="5" rx="0.6" fill="currentColor"/>'
        '<rect x="7.5" y="7" width="3" height="9" rx="0.6" fill="currentColor"/>'
        '<rect x="12" y="3" width="3" height="13" rx="0.6" fill="currentColor"/>'
        "</svg>"
    )


def header(depth: int, active: str, date_human: str) -> str:
    items = [
        ("home", href(depth, ""), "Оглавление"),
        ("hub", href(depth, "kaliningrad/"), "Калининград"),
        ("zaprosy", href(depth, "kaliningrad/zaprosy/"), "Запросы"),
        ("otzyvy", href(depth, "kaliningrad/otzyvy/"), "Отзывы"),
        ("metodika", href(depth, "metodika/"), "Методика"),
    ]
    pills = []
    for key, url, label in items:
        cls = "pill is-active" if key == active else "pill"
        pills.append(f'<a class="{cls}" href="{e(url)}">{e(label)}</a>')
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{e(href(depth, ""))}">
      <span class="logo-tile">{logo_svg()}</span>
      <span class="brand-text">
        <span class="brand-name">Рейтинги автопрокатов</span>
        <span class="brand-sub">на {e(date_human)}</span>
      </span>
    </a>
    <nav class="pill-nav" aria-label="Разделы">{"".join(pills)}</nav>
  </div>
</header>"""


def footer(depth: int) -> str:
    return f"""<footer class="site-footer">
  <div class="wrap">
    Витрина публикует готовые рейтинги, здесь их не считает.
    <a href="{e(href(depth, "metodika/"))}">Методика</a>.
  </div>
</footer>"""


def page(depth: int, title: str, active: str, date_human: str, body: str) -> str:
    banner = BANNER_HTML
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <link rel="stylesheet" href="{e(css_href(depth))}">
</head>
<body>
{banner}{header(depth, active, date_human)}
<main class="wrap">
{body}
</main>
{footer(depth)}
</body>
</html>
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def depth_pills() -> str:
    return """<nav class="depth-pills" aria-label="Глубина списка">
  <a class="pill" href="#top-3">Топ-3</a>
  <a class="pill" href="#top-5">Топ-5</a>
  <a class="pill" href="#top-10">Топ-10</a>
</nav>"""


def top3_html(rows: list[dict]) -> str:
    cards = []
    for row in rows[:3]:
        score = format_score(row["score"])
        score_html = f'<div class="place-score">{e(score)}</div>' if score is not None else ""
        cards.append(
            f'<article class="card place-card">'
            f'<div class="place-num">Место {e(row["place"])}</div>'
            f'<div class="place-name">{e(row["name"])}</div>'
            f"{score_html}</article>"
        )
    return f'<section id="top-3" class="top3">{"".join(cards)}</section>'


def trust_html(depth: int, date_human: str) -> str:
    return f"""<section class="card trust">
  <p>На {e(date_human)}.</p>
  <p>Места в таблице не продаются. Таблица — не реклама.</p>
  <p><a href="{e(href(depth, "metodika/"))}">Как считали</a></p>
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


def table_html(rows: list[dict]) -> str:
    if not rows:
        return ""
    body_rows = []
    for row in rows:
        row_id = ""
        if row["place"] == 5:
            row_id = ' id="top-5"'
        elif row["place"] == 10:
            row_id = ' id="top-10"'
        score = format_score(row["score"])
        score_cell = e(score) if score is not None else "—"
        body_rows.append(
            f"<tr{row_id}><td class=\"num\">{e(row['place'])}</td>"
            f"<td>{e(row['name'])}</td>"
            f"<td class=\"num\">{score_cell}</td></tr>"
        )
    return f"""<section class="card table-block" id="full-list">
  <h2>Полный список</h2>
  <div class="table-scroll">
    <table>
      <thead><tr><th class="num">Место</th><th>Компания</th><th class="num">Балл</th></tr></thead>
      <tbody>
        {"".join(body_rows)}
      </tbody>
    </table>
  </div>
  <p class="table-note">Места в таблице не продаются. Таблица — не реклама.</p>
</section>"""


def ranking_body(
    depth: int,
    kicker: str,
    heading: str,
    lead: str,
    rows: list[dict],
    date_human: str,
) -> str:
    first = rows[0] if rows else None
    first_line = ""
    if first:
        score = format_score(first["score"])
        score_bit = f", балл {score}" if score is not None else ""
        first_line = f" {e(kicker)}, 1-е место: {e(first['name'])}{e(score_bit)}."
    return f"""<p class="kicker">{e(kicker)}</p>
<h1>{e(heading)}</h1>
<p class="lead">{e(lead)}{first_line}</p>
{depth_pills()}
{top3_html(rows)}
{trust_html(depth, date_human)}
{cards_html(rows)}
{table_html(rows)}"""


def md_inline(text: str) -> str:
    text = e(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


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

    def flush_list() -> None:
        nonlocal list_buf, list_type
        if not list_buf:
            return
        tag = list_type or "ul"
        items = "".join(f"<li>{md_inline(x)}</li>" for x in list_buf)
        parts.append(f"<{tag}>{items}</{tag}>")
        list_buf = []
        list_type = None

    for raw in src.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush_list()
            continue
        if line.startswith("# "):
            flush_list()
            parts.append(f"<h2>{md_inline(line[2:])}</h2>")
            continue
        if line.startswith("## "):
            flush_list()
            parts.append(f"<h2>{md_inline(line[3:])}</h2>")
            continue
        if line.startswith("### "):
            flush_list()
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
    flush_list()
    html_out = "\n".join(parts)
    for i, chunk in enumerate(chunks):
        html_out = html_out.replace(f"@@MATH{i}@@", chunk)
    return html_out


def build_home(pkg: dict, date_human: str) -> str:
    body = f"""<p class="kicker">Оглавление</p>
<h1>Рейтинги автопрокатов</h1>
<p class="lead">Готовые рейтинги. Федерального топа нет.</p>
<section class="toc-grid">
  <a class="card link-card" href="{e(href(0, "kaliningrad/"))}">
    <h2>Калининград</h2>
    <p>На {e(date_human)}. Исследование ещё не опубликовано.</p>
  </a>
  <a class="card link-card" href="{e(href(0, "kaliningrad/zaprosy/"))}">
    <h2>Брендовые запросы</h2>
    <p>Рейтинг по поисковым запросам. На {e(date_human)}.</p>
  </a>
  <a class="card link-card" href="{e(href(0, "kaliningrad/otzyvy/"))}">
    <h2>Отзовики</h2>
    <p>Рейтинг по картам и отзывам. На {e(date_human)}.</p>
  </a>
  <a class="card link-card" href="{e(href(0, "metodika/"))}">
    <h2>Методика</h2>
    <p>Как считали запросы и отзовики.</p>
  </a>
</section>"""
    return page(0, "Рейтинги автопрокатов", "home", date_human, body)


def build_hub(pkg: dict, date_human: str) -> str:
    body = f"""<p class="kicker">Калининград</p>
<h1>Автопрокаты Калининграда</h1>
<p class="lead">На {e(date_human)}. Исследование ещё не опубликовано — мест и баллов на этой странице нет.</p>
<section class="link-grid">
  <a class="card link-card" href="{e(href(1, "kaliningrad/zaprosy/"))}">
    <h2>Брендовые запросы</h2>
    <p>Рейтинг по поисковым запросам.</p>
  </a>
  <a class="card link-card" href="{e(href(1, "kaliningrad/otzyvy/"))}">
    <h2>Отзовики</h2>
    <p>Рейтинг по картам и отзывам.</p>
  </a>
  <a class="card link-card" href="{e(href(1, "metodika/"))}">
    <h2>Методика</h2>
    <p>Как считали запросы и отзовики.</p>
  </a>
</section>"""
    return page(1, "Калининград — рейтинги автопрокатов", "hub", date_human, body)


def build_metodika(date_human: str) -> str:
    wordstat = md_to_html((DATA / "wordstat-method-description.md").read_text(encoding="utf-8"))
    reviews = md_to_html((DATA / "reviews-method-description.md").read_text(encoding="utf-8"))
    body = f"""<p class="kicker">Методика</p>
<h1>Как считали</h1>
<p class="lead">На {e(date_human)}.</p>
<section class="card method" id="zaprosy">
{wordstat}
</section>
<section class="card method" id="otzyvy">
{reviews}
</section>
<section class="card method" id="issledovanie">
<h2>Исследование</h2>
<p>Исследование ещё не опубликовано.</p>
</section>"""
    return page(1, "Методика — рейтинги автопрокатов", "metodika", date_human, body)


def main() -> None:
    pkg = load_package()
    date_human = format_date(pkg["as_of"])
    tables = pkg.get("tables") or {}

    wordstat = normalize_rows(tables.get("wordstat"))
    reviews = normalize_rows(tables.get("reviews"))
    # tables.research may exist in JSON; do not publish places on pages.

    write(ROOT / "index.html", build_home(pkg, date_human))
    write(ROOT / "kaliningrad" / "index.html", build_hub(pkg, date_human))
    write(
        ROOT / "kaliningrad" / "zaprosy" / "index.html",
        page(
            2,
            "Рейтинг брендовых запросов — Калининград",
            "zaprosy",
            date_human,
            ranking_body(
                2,
                "Рейтинг брендовых запросов",
                "Калининград, брендовые запросы",
                f"На {date_human}.",
                wordstat,
                date_human,
            ),
        ),
    )
    write(
        ROOT / "kaliningrad" / "otzyvy" / "index.html",
        page(
            2,
            "Рейтинг по отзовикам — Калининград",
            "otzyvy",
            date_human,
            ranking_body(
                2,
                "Рейтинг по отзовикам",
                "Калининград, отзовики",
                f"На {date_human}.",
                reviews,
                date_human,
            ),
        ),
    )
    write(ROOT / "metodika" / "index.html", build_metodika(date_human))
    print("built", len(wordstat), "wordstat rows,", len(reviews), "reviews rows")


if __name__ == "__main__":
    main()
