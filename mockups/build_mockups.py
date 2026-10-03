#!/usr/bin/env python3
"""Design mockups. Same ranking markdown as production. Does not write live pages."""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build as site  # noqa: E402

MOCK = Path(__file__).resolve().parent
DATE = "26 сентября 2026"
CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'"
)

A_TILE = (
    '<svg width="36" height="36" viewBox="0 0 32 32" aria-hidden="true">'
    '<rect width="32" height="32" rx="8" fill="#efb656"/>'
    '<g fill="#160d07">'
    '<path d="M10 7h12v1.15c0 3.55-1.85 6.2-4.55 6.95L17.7 17.4h1.85a.7.7 0 0 1 0 1.4h-7.1a.7.7 0 0 1 0-1.4h1.85l.25-2.3C11.85 14.35 10 11.7 10 8.15V7z"/>'
    '<path d="M10 8.1H7.55A2.7 2.7 0 0 0 7.6 13.4c.95.45 2.05.75 3.2.9A6.4 6.4 0 0 1 10 8.15V8.1z"/>'
    '<path d="M22 8.1h2.45a2.7 2.7 0 0 1-.05 5.3c.95.45 2.05.75 3.2.9A6.4 6.4 0 0 0 22 8.15V8.1z"/>'
    '<rect x="14.35" y="18.55" width="3.3" height="3.35" rx=".45"/>'
    '<path d="M11.1 22.7h9.8c.55 0 1 .4 1.08.94l.12.7A1.55 1.55 0 0 1 20.6 26H11.4a1.55 1.55 0 0 1-1.5-1.66l.12-.7c.08-.54.53-.94 1.08-.94z"/>'
    "</g></svg>"
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
STAR_SM = (
    '<svg width="11" height="11" viewBox="0 0 24 24" aria-hidden="true">'
    '<path fill="currentColor" d="M12 2.6 14.4 9H21l-5.3 4.1 2 6.5L12 16.4 6.3 19.6l2-6.5L3 9h6.6z"/>'
    "</svg>"
)
SEARCH = (
    '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">'
    '<circle cx="10.5" cy="10.5" r="6.2" fill="none" stroke="currentColor" stroke-width="2"/>'
    '<path fill="currentColor" d="M15.2 16.3 20 21.1l1.1-1.1-4.8-4.8z"/>'
    "</svg>"
)
REVIEWS = (
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
PAUSE = (
    '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">'
    '<circle cx="12" cy="12" r="8.2" fill="none" stroke="currentColor" stroke-width="1.8"/>'
    '<path fill="currentColor" d="M11 8h2v8h-2z"/>'
    "</svg>"
)


def e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def up(from_dir: Path) -> str:
    return "../" * len(from_dir.relative_to(MOCK).parts)


def page(variant: str, dest: Path, title: str, description: str, active: str, body: str) -> None:
    depth_from_variant = len(dest.parent.relative_to(MOCK / variant).parts)
    css = "../" * depth_from_variant + "style.css"
    marks = up(dest.parent) + "marks/"
    brand_href = "../" * depth_from_variant + "kaliningrad/"
    items = [
        ("hub", "../" * depth_from_variant + "kaliningrad/", "Калининград"),
        ("zaprosy", "../" * depth_from_variant + "kaliningrad/zaprosy/", "Запросы"),
        ("otzyvy", "../" * depth_from_variant + "kaliningrad/otzyvy/", "Отзывы"),
    ]
    pills = []
    for key, url, label in items:
        cls = "pill is-active" if key == active else "pill"
        pills.append(f'<a class="{cls}" href="{e(url)}">{e(label)}</a>')

    if variant == "a":
        logo = f'<span class="logo-tile">{A_TILE}</span>'
        icon_links = (
            f'  <link rel="icon" href="{e(marks + "a-tile.svg")}" type="image/svg+xml">\n'
            f'  <link rel="icon" href="{e(marks + "a-32.png")}" sizes="32x32" type="image/png">\n'
            f'  <link rel="apple-touch-icon" href="{e(marks + "a-180.png")}">'
        )
    elif variant == "b":
        logo = f'<span class="logo-mark">{CUP}</span>'
        icon_links = f'  <link rel="icon" href="{e(marks + "shared.svg")}" type="image/svg+xml">'
    else:
        logo = f'<span class="logo-tile">{CUP}</span>'
        icon_links = f'  <link rel="icon" href="{e(marks + "shared.svg")}" type="image/svg+xml">'

    html_out = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="{CSP}">
  <meta name="robots" content="noindex, nofollow">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
{icon_links}
  <link rel="stylesheet" href="{e(css)}">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{e(brand_href)}">
      {logo}
      <span class="brand-text">
        <span class="brand-name">Рейтинги автопрокатов</span>
        <span class="brand-sub">на {DATE}</span>
      </span>
    </a>
    <nav class="pill-nav" aria-label="Разделы">{"".join(pills)}</nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    Витрина публикует готовые рейтинги, здесь их не считает.
  </div>
</footer>
</body>
</html>
"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html_out, encoding="utf-8")


def hub_body(variant: str) -> str:
    lead = "На 26 сентября 2026. Исследование ещё не опубликовано — мест и баллов на этой странице нет."
    cards = [
        ("zaprosy/", "Брендовые запросы", "Рейтинг по поисковым запросам.", SEARCH),
        ("otzyvy/", "Отзовики", "Рейтинг по картам и отзывам.", REVIEWS),
        ("../../../metodika/", "Методика", "Как считали запросы и отзовики.", BOOK),
    ]
    if variant == "a":
        facts = f"""<ul class="facts">
  <li>{CAL} Срез {DATE}</li>
  <li>{LIST} Два рейтинга открыты</li>
  <li>{PAUSE} Исследования ещё нет</li>
</ul>"""
        links = []
        for href, title, text, ico in cards:
            links.append(
                f'<a class="card link-card" href="{e(href)}">'
                f'<span class="link-ico">{ico}</span>'
                f"<span><h2>{e(title)}</h2><p>{e(text)}</p></span>"
                f'<span class="go" aria-hidden="true">→</span></a>'
            )
        return f"""<p class="kicker">Калининград</p>
<h1>Автопрокаты Калининграда</h1>
<p class="lead">{e(lead)}</p>
{facts}
<section class="link-grid">
  {"".join(links)}
</section>"""
    if variant == "b":
        facts = f"""<ul class="facts">
  <li><b>Срез</b>{DATE}</li>
  <li><b>Открыто</b>запросы и отзовики</li>
  <li><b>Исследование</b>ещё не опубликовано</li>
</ul>"""
        links = []
        for i, (href, title, text, _ico) in enumerate(cards, start=1):
            links.append(
                f'<a class="link-card" href="{e(href)}">'
                f'<span class="idx">{i:02d}</span>'
                f"<span><h2>{e(title)}</h2><p>{e(text)}</p></span>"
                f'<span class="go">открыть</span></a>'
            )
        return f"""<p class="kicker">Калининград</p>
<h1>Автопрокаты Калининграда</h1>
<p class="lead">{e(lead)}</p>
{facts}
<section class="link-grid">
  {"".join(links)}
</section>"""
    facts = f"""<ul class="facts">
  <li>Срез {DATE}</li>
  <li>Запросы и отзовики открыты</li>
  <li>Исследования нет</li>
</ul>"""
    links = []
    for href, title, text, ico in cards:
        links.append(
            f'<a class="link-card" href="{e(href)}">'
            f'<span class="link-ico">{ico}</span>'
            f"<span><h2>{e(title)}</h2><p>{e(text)}</p></span>"
            f'<span class="go" aria-hidden="true">→</span></a>'
        )
    return f"""<p class="kicker">Калининград</p>
<h1>Автопрокаты Калининграда</h1>
<p class="lead">{e(lead)}</p>
{facts}
<section class="link-grid">
  {"".join(links)}
</section>"""


def stars(n: int) -> str:
    return '<span class="stars" aria-hidden="true">' + (STAR * n) + "</span>"


def top3_a(rows: list[dict]) -> str:
    cards = []
    for row in rows[:3]:
        score = site.format_score(row["score"])
        p = int(row["place"])
        extra = stars(3) if p == 1 else ""
        cards.append(
            f'<article class="card place-card" data-p="{p}">'
            f'<div class="place-head"><div class="place-num">Место {e(p)}</div>'
            f'<span class="trophy">{CUP}</span></div>'
            f'<div class="place-name">{e(row["name"])}</div>{extra}'
            f'<div class="place-score">{e(score)}</div>'
            f'<div class="score-label">балл</div></article>'
        )
    return f'<section id="top-3" class="top3">{"".join(cards)}</section>'


def top3_b(rows: list[dict]) -> str:
    cards = []
    for row in rows[:3]:
        score = site.format_score(row["score"])
        p = int(row["place"])
        cards.append(
            f'<article class="place-card" data-p="{p}">'
            f'<div class="place-num">{e(p)}</div>'
            f'<div><div class="place-name">{e(row["name"])}</div>'
            f'<div class="place-meta">место {e(p)}</div></div>'
            f'<div class="place-score">{e(score)}</div></article>'
        )
    return f'<section id="top-3" class="top3">{"".join(cards)}</section>'


def top3_c(rows: list[dict]) -> str:
    cards = []
    for row in rows[:3]:
        score = site.format_score(row["score"])
        p = int(row["place"])
        star = STAR if p == 1 else ""
        cards.append(
            f'<article class="place-card" data-p="{p}">'
            f'<div class="place-num">{e(p)}</div>'
            f'<div class="place-name">{e(row["name"])}</div>'
            f'<div class="place-score">{star}{e(score)}</div></article>'
        )
    return f'<section id="top-3" class="card top3">{"".join(cards)}</section>'


def trust(variant: str) -> str:
    if variant == "a":
        return f"""<section class="card trust">
  <div class="trust-row">
    <div class="trust-item">{CAL}<p>На {DATE}.</p></div>
    <div class="trust-item">{SHIELD}<p>Места в таблице не продаются. Таблица — не реклама.</p></div>
    <div class="trust-item">{BOOK}<p>Как считали — в методике на сайте.</p></div>
  </div>
</section>"""
    if variant == "b":
        return f"""<section class="trust">
  <p>На {DATE}.</p>
  <p>Места в таблице не продаются. Таблица — не реклама.</p>
</section>"""
    return f"""<section class="card trust">
  <p>На {DATE}.</p>
  <p>Места в таблице не продаются. Таблица — не реклама.</p>
</section>"""


def table_html(variant: str, rows: list[dict]) -> str:
    body_rows = []
    for row in rows:
        place = int(row["place"])
        row_id = ""
        if place == 5:
            row_id = ' id="top-5"'
        elif place == 10:
            row_id = ' id="top-10"'
        cls = ' class="is-top"' if place <= 3 else ""
        score = site.format_score(row["score"])
        mark = ""
        if variant == "a" and place <= 3:
            mark = CUP
        elif variant == "b" and place == 1:
            mark = f'<span class="rank-cup">{CUP}</span>'
        elif variant == "c" and place <= 3:
            mark = f'<span class="star">{STAR_SM}</span>'
        if variant == "a":
            place_html = f'<span class="rank">{mark}{e(place)}</span>'
        elif variant == "b":
            place_html = f"{mark}{e(place)}"
        else:
            place_html = f"{mark}{e(place)}"
        body_rows.append(
            f"<tr{cls}{row_id}><td class=\"num\">{place_html}</td>"
            f"<td>{e(row['name'])}</td>"
            f"<td class=\"num\">{e(score)}</td></tr>"
        )
    heading = "Полный список"
    wrap_a = ' class="card table-block"' if variant != "b" else ' class="table-block"'
    return f"""<section{wrap_a} id="full-list">
  <h2>{(CUP + " ") if variant == "a" else ""}{heading}</h2>
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


def ranking_body(variant: str, kicker: str, heading: str, rows: list[dict]) -> str:
    first = rows[0]
    score = site.format_score(first["score"])
    lead = f"На {DATE}. {kicker}, 1-е место: {first['name']}, балл {score}."
    if variant == "a":
        top = top3_a(rows)
        depth = f"""<nav class="depth-pills" aria-label="Глубина списка">
  <a class="pill" href="#top-3">{CUP}Топ-3</a>
  <a class="pill" href="#top-5">Топ-5</a>
  <a class="pill" href="#top-10">Топ-10</a>
</nav>"""
        head = f'<p class="kicker-row">{SEARCH}<span>{e(kicker)}</span></p>'
    elif variant == "b":
        top = top3_b(rows)
        depth = """<nav class="depth-pills" aria-label="Глубина списка">
  <a class="pill" href="#top-3">Топ-3</a>
  <a class="pill" href="#top-5">Топ-5</a>
  <a class="pill" href="#top-10">Топ-10</a>
</nav>"""
        head = f'<p class="kicker">{e(kicker)}</p>'
    else:
        top = top3_c(rows)
        depth = """<nav class="depth-pills" aria-label="Глубина списка">
  <a class="pill" href="#top-3">Топ-3</a>
  <a class="pill" href="#top-5">Топ-5</a>
  <a class="pill" href="#top-10">Топ-10</a>
</nav>"""
        head = f'<p class="kicker">{e(kicker)}</p>'
    return f"""{head}
<h1>{e(heading)}</h1>
<p class="lead">{e(lead)}</p>
{depth}
{top}
{trust(variant)}
{table_html(variant, rows)}"""


def write_chooser() -> None:
    (MOCK / "chooser.css").write_text(
        """body{margin:0;background:#120e0b;color:#f7f1e3;font-family:"Segoe UI",system-ui,sans-serif}
main{max-width:42rem;margin:0 auto;padding:2.5rem 1rem 4rem}
h1{font-size:1.6rem}
p{color:#bcaf9c}
a{color:#efb656}
ol{padding-left:1.2rem;line-height:1.7}
""",
        encoding="utf-8",
    )
    text = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <meta http-equiv="Content-Security-Policy" content="{CSP}">
  <title>Макеты витрины</title>
  <link rel="icon" href="marks/shared.svg" type="image/svg+xml">
  <link rel="stylesheet" href="chooser.css">
</head>
<body>
<main>
  <h1>Три макета витрины</h1>
  <p>Не прод. Места и баллы те же, что на живых страницах. Баннер не показан.</p>
  <ol>
    <li><a href="a/kaliningrad/">A — текущий, с деталями</a> · <a href="a/kaliningrad/zaprosy/">запросы</a></li>
    <li><a href="b/kaliningrad/">B — реестр</a> · <a href="b/kaliningrad/zaprosy/">запросы</a></li>
    <li><a href="c/kaliningrad/">C — табло</a> · <a href="c/kaliningrad/zaprosy/">запросы</a></li>
  </ol>
  <p>Знаки: <a href="marks/preview.html">плитка и фавикон</a>.</p>
</main>
</body>
</html>
"""
    (MOCK / "index.html").write_text(text, encoding="utf-8")


def write_marks_preview() -> None:
    css = """body{margin:0;background:#120e0b;color:#f7f1e3;font-family:"Segoe UI",system-ui,sans-serif}
main{max-width:56rem;margin:0 auto;padding:2.5rem 1rem 4rem}
h1{font-size:1.5rem;margin:0 0 .6rem}
p,figcaption{color:#bcaf9c}
.row{display:flex;flex-wrap:wrap;gap:1.25rem;margin:1.5rem 0}
figure{margin:0;background:#221810;border:1px solid #4c4035;border-radius:1rem;padding:1rem 1.1rem;min-width:11rem;text-align:center}
.light{background:#f3efe6;color:#160d07}
.light figcaption{color:#5c5348}
img{display:block;margin:0 auto .6rem}
"""
    (MOCK / "marks" / "preview.css").write_text(css, encoding="utf-8")
    text = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <meta http-equiv="Content-Security-Policy" content="{CSP}">
  <title>Знаки витрины</title>
  <link rel="stylesheet" href="preview.css">
  <link rel="icon" href="a-tile.svg" type="image/svg+xml">
</head>
<body>
<main>
  <h1>Знаки</h1>
  <p>A — золотая плитка с кубком. Общий знак — тёмная плитка, тот же кубок: на светлой вкладке и на любом из трёх макетов.</p>
  <div class="row">
    <figure>
      <img src="a-180.png" width="180" height="180" alt="Плитка A, 180">
      <figcaption>A · PNG 180 (есть SVG)</figcaption>
    </figure>
    <figure>
      <img src="a-32.png" width="32" height="32" alt="Фавикон A 32">
      <figcaption>A · PNG 32</figcaption>
    </figure>
    <figure>
      <img src="shared-180.png" width="180" height="180" alt="Общий знак 180">
      <figcaption>Общий · PNG 180 (есть SVG)</figcaption>
    </figure>
    <figure class="light">
      <img src="shared-32.png" width="32" height="32" alt="Общий 32 на светлом">
      <figcaption>Общий · PNG 32 на светлом</figcaption>
    </figure>
  </div>
</main>
</body>
</html>
"""
    (MOCK / "marks" / "preview.html").write_text(text, encoding="utf-8")


def main() -> None:
    wordstat = site.parse_ranking_table(site.WORDSTAT_RANKING_MD)
    reviews = site.parse_ranking_table(site.REVIEWS_RANKING_MD)
    if len(wordstat) != 45 or len(reviews) != 36:
        raise SystemExit("ranking length mismatch")
    if wordstat[0]["name"] != "Амиго" or reviews[1]["name"] != "Carplus":
        raise SystemExit("ranking names mismatch")

    pages = {
        "zaprosy": (
            "Рейтинг брендовых запросов",
            "Калининград, брендовые запросы",
            "Рейтинг автопрокатов Калининграда по брендовым поисковым запросам. На 26 сентября 2026.",
            wordstat,
        ),
        "otzyvy": (
            "Рейтинг по отзовикам",
            "Калининград, отзовики",
            "Рейтинг автопрокатов Калининграда по картам и отзывам. На 26 сентября 2026.",
            reviews,
        ),
    }

    write_chooser()
    write_marks_preview()

    for variant in ("a", "b", "c"):
        page(
            variant,
            MOCK / variant / "kaliningrad" / "index.html",
            f"Автопрокаты Калининграда — {DATE}",
            "Рейтинги автопрокатов Калининграда на 26 сентября 2026. Исследование ещё не опубликовано.",
            "hub",
            hub_body(variant),
        )
        for slug, (kicker, heading, desc, rows) in pages.items():
            page(
                variant,
                MOCK / variant / "kaliningrad" / slug / "index.html",
                f"{kicker} — Калининград, {DATE}",
                desc,
                slug,
                ranking_body(variant, kicker, heading, rows),
            )
    print("mockups", len(wordstat), "wordstat", len(reviews), "reviews")


if __name__ == "__main__":
    main()
