#!/usr/bin/env python3
"""Guards for the generated preview. Run after build.py."""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PAGES = [
    ROOT / "index.html",
    ROOT / "kaliningrad" / "index.html",
    ROOT / "kaliningrad" / "zaprosy" / "index.html",
    ROOT / "kaliningrad" / "otzyvy" / "index.html",
    ROOT / "metodika" / "index.html",
    ROOT / "kontakty" / "index.html",
    ROOT / "404.html",
]
LEGAL_NAME_PAGES = {
    ROOT / "kaliningrad" / "index.html",
    ROOT / "kontakty" / "index.html",
}


def fail(msg: str) -> None:
    print("FAIL:", msg, file=sys.stderr)
    raise SystemExit(1)


def visible_text(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


def html_table_name_cells(html: str) -> list[tuple[str, str]]:
    bodies = re.findall(r"<tbody>\s*(.*?)\s*</tbody>", html, flags=re.S)
    if not bodies:
        return []
    return re.findall(
        r'<tr(?:\s[^>]*)?><td class="num"><span class="rank">(?:<svg[\s\S]*?</svg>)?(\d+)</span></td>'
        r"<td>(.*?)</td>",
        bodies[0],
    )


def html_table_rows(html: str) -> list[tuple[str, str, str]]:
    bodies = re.findall(r"<tbody>\s*(.*?)\s*</tbody>", html, flags=re.S)
    if not bodies:
        return []
    # First table on ranking pages is the published list.
    rows = re.findall(
        r'<tr(?:\s[^>]*)?><td class="num"><span class="rank">(?:<svg[\s\S]*?</svg>)?(\d+)</span></td>'
        r"<td>(.*?)</td>"
        r'<td class="num">(.*?)</td></tr>',
        bodies[0],
    )
    return [(place, visible_text(name), score) for place, name, score in rows]


def podium_name_html(html: str, place: int) -> str | None:
    m = re.search(
        rf'<article class="card place-card" data-p="{place}">'
        r'.*?<div class="place-name">(.*?)</div>',
        html,
        flags=re.S,
    )
    return m.group(1) if m else None


def resolve_href(site, page: Path, href: str) -> Path | None:
    path_part = href.split("#", 1)[0]
    if not path_part or path_part.startswith(("http://", "https://", "mailto:")):
        return None
    root = ROOT.resolve()
    if path_part.startswith("/"):
        base = site.url_base_path()
        if base:
            if path_part in (base, f"{base}/"):
                rel = ""
            elif path_part.startswith(base + "/"):
                rel = path_part[len(base) + 1 :]
            else:
                fail(f"{page.relative_to(ROOT)} href {href} misses preview base path")
        else:
            rel = path_part.lstrip("/")
        candidate = (ROOT / rel).resolve()
    else:
        candidate = (page.parent / path_part).resolve()
    if candidate != root and root not in candidate.parents:
        fail(f"{page.relative_to(ROOT)} href {href} leaves the repo")
    if candidate.is_dir() or path_part.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def main() -> None:
    sys.path.insert(0, str(ROOT))
    import build as site

    if site.PACKAGE_PATH.name != "package-2026-10-01.json":
        fail("generator must read package-2026-10-01.json")
    if "package-2026-09-26.json" in (ROOT / "build.py").read_text(encoding="utf-8"):
        fail("generator must stop using package-2026-09-26.json")
    if site.e('<img src=x onerror=alert(1)>') == '<img src=x onerror=alert(1)>':
        fail("names must be HTML-escaped")
    if site.format_score("<script>") is not None:
        fail("score must not pass through a raw string")
    if site.format_score(None) is not None:
        fail("null score must be empty")
    if site.format_score(93.15, 2) != "93.15":
        fail("research score must keep two decimals")
    if site.format_score("99.3", 1) != "99.3":
        fail("reviews/wordstat score must keep one decimal")
    if site.format_score("100.0", 1) != "100.0":
        fail("wordstat 100 must stay 100.0")
    if site.company_id_of({"id": "../evil"}) is not None:
        fail("company_id must be kebab latin")
    if site.company_id_of({"company_id": "amigo"}) != "amigo":
        fail("valid company_id rejected")
    if site.place_of({"place": "first"}) is not None:
        fail("place must be an integer")
    if site.place_of({"place": 3}) != 3:
        fail("integer place rejected")
    if site.card_of({"card": {"pros": [], "cons": []}}) is not None:
        fail("empty card must not render")
    if not site.is_preview():
        fail("GitHub Pages host must be treated as preview")
    xss_table = site.table_html(
        [{"company_id": "x", "name": "<b>xss</b>", "place": 1, "score": 1, "card": None, "kind": "research"}],
        "research",
    )
    if "<b>xss</b>" in xss_table or "&lt;b&gt;xss&lt;/b&gt;" not in xss_table:
        fail("snapshot name must be escaped in the table")
    xss_cards = site.cards_html(
        [
            {
                "company_id": "x",
                "name": "n",
                "place": 1,
                "score": 1,
                "card": {"pros": ['<img src=x onerror=alert(1)>'], "cons": []},
            }
        ]
    )
    if "<img" in xss_cards.lower():
        fail("card.pros must be escaped")

    src = (ROOT / "build.py").read_text(encoding="utf-8")
    if re.search(r'''['"]ranking-table\.md['"]''', src) and "same reviews list" not in src:
        fail("generator must not read ranking-table.md (same reviews list)")
    if "score_raw" in src:
        fail("generator must not read or show score_raw")

    pkg = site.load_package()
    if pkg.get("as_of") != "2026-10-01":
        fail(f"package as_of must be 2026-10-01, got {pkg.get('as_of')}")
    research = site.normalize_rows(pkg["tables"]["research"], "research")
    wordstat = site.normalize_rows(pkg["tables"]["wordstat"], "wordstat")
    reviews = site.normalize_rows(pkg["tables"]["reviews"], "reviews")
    if len(research) != 20:
        fail(f"research must have 20 rows, got {len(research)}")
    if len(wordstat) != 43:
        fail(f"wordstat must have 43 rows, got {len(wordstat)}")
    if len(reviews) != 36:
        fail(f"reviews must have 36 rows, got {len(reviews)}")
    if [r["place"] for r in research] != list(range(1, 21)):
        fail("research places must stay package order, not score order")
    if [r["place"] for r in wordstat] != list(range(1, 44)):
        fail("wordstat places must stay package order")
    if wordstat[0]["score"] not in (100, "100", "100.0", 100.0):
        fail("wordstat place 1 must be 100")

    research_md = site.parse_ranking_table(site.RESEARCH_RANKING_MD)
    wordstat_md = site.parse_ranking_table(site.WORDSTAT_RANKING_MD)
    reviews_md = site.parse_ranking_table(site.REVIEWS_RANKING_MD)
    if len(research_md) != 20 or len(wordstat_md) != 43 or len(reviews_md) != 36:
        fail("markdown tables must match package row counts")
    try:
        site.parse_ranking_table(site.DOCS_EXPORT / "ranking-table.md")
        fail("ranking-table.md must be rejected")
    except ValueError:
        pass

    if not (ROOT / "assets" / "og-image.png").is_file():
        fail("missing assets/og-image.png")
    if not (ROOT / "assets" / "marks" / "shared.svg").is_file():
        fail("missing shared.svg")
    if not (ROOT / "assets" / "marks" / "shared-32.png").is_file():
        fail("missing shared-32.png")
    if not (ROOT / "assets" / "marks" / "shared-180.png").is_file():
        fail("missing shared-180.png")
    if (ROOT / "assets" / "marks" / "a-tile.svg").exists():
        fail("do not publish a-tile as the site mark")

    for path in PAGES:
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        if 'name="robots" content="noindex, nofollow"' not in text:
            fail(f"no noindex on {path.relative_to(ROOT)}")
        if 'http-equiv="Content-Security-Policy"' not in text:
            fail(f"no CSP on {path.relative_to(ROOT)}")
        if "default-src 'self'" not in text or "object-src 'none'" not in text or "base-uri 'self'" not in text:
            fail(f"CSP too weak on {path.relative_to(ROOT)}")
        if "mc.yandex.ru" not in text or "mc.yandex.com" not in text:
            fail(f"CSP must allow Metrika hosts on {path.relative_to(ROOT)}")
        if "unsafe-inline" in text:
            fail(f"unsafe-inline on {path.relative_to(ROOT)}")
        if 'rel="canonical"' in text:
            fail(f"preview must not advertise canonical {path.relative_to(ROOT)}")
        if 'property="og:url"' in text:
            fail(f"preview must not set og:url {path.relative_to(ROOT)}")
        if 'property="og:image"' not in text or 'name="twitter:image"' not in text:
            fail(f"og:image/twitter:image missing on {path.relative_to(ROOT)}")
        if "assets/og-image.png" not in text:
            fail(f"share image path missing on {path.relative_to(ROOT)}")
        if "schema.org" in text.lower() or "application/ld+json" in text.lower():
            fail(f"JSON-LD/schema.org on {path.relative_to(ROOT)}")
        if "aggregaterating" in text.lower() or 'itemprop="review' in text.lower():
            fail(f"review schema on {path.relative_to(ROOT)}")
        title_m = re.search(r"<title>(.*?)</title>", text)
        if title_m and "лучший прокат в" in title_m.group(1).lower():
            fail(f"invented SEO slogan in title on {path.relative_to(ROOT)}")
        if "gtag" in text.lower() or "googletagmanager" in text.lower():
            fail(f"counter stub on {path.relative_to(ROOT)}")
        if "Rentprog" in text:
            fail(f"informal Rentprog on {path.relative_to(ROOT)}")
        if re.search(r"Лок\s+\d{4}-\d{2}-\d{2}", text):
            fail(f"lock note on {path.relative_to(ROOT)}")
        if path not in LEGAL_NAME_PAGES and ("ООО" in text or "Рентпрог" in text):
            fail(f"publisher legal name on {path.relative_to(ROOT)}")
        pills = re.search(r'<nav class="pill-nav"[^>]*>(.*?)</nav>', text, flags=re.S)
        if pills and ("kontakty" in pills.group(1) or "Контакты" in pills.group(1)):
            fail(f"kontakty must not be in pill nav on {path.relative_to(ROOT)}")
        foot = re.search(r'<footer class="site-footer">(.*?)</footer>', text, flags=re.S)
        if not foot or "kontakty" not in foot.group(1) or "Контакты" not in foot.group(1):
            fail(f"footer must link to kontakty on {path.relative_to(ROOT)}")
        if "ваша реклама" in text.lower() or 'class="banner"' in text or 'id="banner"' in text:
            fail(f"empty banner rendered on {path.relative_to(ROOT)}")
        if "base href" in text.lower() or "<base " in text.lower():
            fail(f"base href on {path.relative_to(ROOT)}")
        if "pending-edits" in text:
            fail(f"pending-edits on {path.relative_to(ROOT)}")
        if path.name != "index.html" or "metodika" not in str(path):
            if "score_raw" in text and path != ROOT / "metodika" / "index.html":
                fail(f"score_raw leaked on {path.relative_to(ROOT)}")
        if "a-tile" in text or "marks/a-32" in text or "marks/a-180" in text:
            fail(f"a-tile favicon on {path.relative_to(ROOT)}")
        if "assets/marks/shared.svg" not in text:
            fail(f"shared favicon missing on {path.relative_to(ROOT)}")
        if f"ym/{site.METRIKA_ID}" in text.replace("watch/", "ym/"):
            pass
        if f"watch/{site.METRIKA_ID}" not in text or "assets/metrika.js" not in text:
            fail(f"official Metrika tag missing on {path.relative_to(ROOT)}")
        scripts = re.findall(r"<script[^>]*src=\"([^\"]+)\"", text, flags=re.I)
        if not scripts or any("metrika.js" not in s for s in scripts):
            fail(f"unexpected script on {path.relative_to(ROOT)}: {scripts}")
        if re.search(r"<script(?![^>]*src=)", text, flags=re.I):
            fail(f"inline script on {path.relative_to(ROOT)}")

        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://")):
                continue
            target = resolve_href(site, path, href)
            if target is None:
                continue
            if not target.is_file():
                fail(f"broken link {href} on {path.relative_to(ROOT)} -> {target}")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if 'href="assets/style.css"' not in home:
        fail("index must keep relative CSS")

    notfound = (ROOT / "404.html").read_text(encoding="utf-8")
    css_rooted = site.root_href("assets/style.css")
    if f'href="{css_rooted}"' not in notfound:
        fail("404 CSS must be site-root so nested unknown URLs still load styles")
    if re.search(r'href="(?:\./)?assets/style\.css"', notfound):
        fail("404 must not use depth-0 relative CSS")
    if "toc-grid" in notfound or 'class="top3"' in notfound or 'class="table-block"' in notfound:
        fail("404 must not be an index.html fallback")
    if "Страница не найдена" not in notfound:
        fail("404 must stay an error page")
    home_rooted = site.root_href("")
    if f'href="{home_rooted}"' not in notfound:
        fail("404 nav must use site-root links")

    config = (ROOT / "_config.yml").read_text(encoding="utf-8")
    for name in ("data", "docs", "media"):
        if not re.search(rf"(?m)^\s*-\s*{name}\s*$", config):
            fail(f"_config.yml must exclude {name} from GitHub Pages")
    if not re.search(r"(?m)^theme:\s*null\s*$", config):
        fail("_config.yml must disable a Jekyll theme")
    if "layout: null" not in config:
        fail("_config.yml must not wrap pages in a layout")
    if (ROOT / ".nojekyll").exists():
        fail(".nojekyll skips Jekyll exclude; snapshot JSON would stay a Pages URL")

    titles = []
    descriptions = []
    for path in PAGES:
        text = path.read_text(encoding="utf-8")
        title_m = re.search(r"<title>(.*?)</title>", text)
        desc_m = re.search(r'<meta name="description" content="([^"]*)">', text)
        og_title_m = re.search(r'<meta property="og:title" content="([^"]*)">', text)
        og_desc_m = re.search(r'<meta property="og:description" content="([^"]*)">', text)
        tw_title_m = re.search(r'<meta name="twitter:title" content="([^"]*)">', text)
        tw_desc_m = re.search(r'<meta name="twitter:description" content="([^"]*)">', text)
        if not title_m or not desc_m:
            fail(f"missing title/description on {path.relative_to(ROOT)}")
        title, desc = title_m.group(1), desc_m.group(1)
        if not title.strip() or not desc.strip():
            fail(f"empty title/description on {path.relative_to(ROOT)}")
        if not og_title_m or og_title_m.group(1) != title:
            fail(f"og:title must match title on {path.relative_to(ROOT)}")
        if not og_desc_m or og_desc_m.group(1) != desc:
            fail(f"og:description must match description on {path.relative_to(ROOT)}")
        if 'property="og:type" content="website"' not in text:
            fail(f"missing og:type on {path.relative_to(ROOT)}")
        if 'property="og:locale" content="ru_RU"' not in text:
            fail(f"missing og:locale on {path.relative_to(ROOT)}")
        if f'property="og:site_name" content="{site.SITE_NAME}"' not in text:
            fail(f"missing og:site_name on {path.relative_to(ROOT)}")
        if 'name="twitter:card" content="summary_large_image"' not in text:
            fail(f"twitter:card must be summary_large_image on {path.relative_to(ROOT)}")
        if not tw_title_m or tw_title_m.group(1) != title:
            fail(f"twitter:title must match title on {path.relative_to(ROOT)}")
        if not tw_desc_m or tw_desc_m.group(1) != desc:
            fail(f"twitter:description must match description on {path.relative_to(ROOT)}")
        titles.append(title)
        descriptions.append(desc)
    if len(set(titles)) != len(titles):
        fail(f"titles must be unique per URL, got {titles}")
    if len(set(descriptions)) != len(descriptions):
        fail(f"descriptions must be unique per URL, got {descriptions}")

    hub = (ROOT / "kaliningrad" / "index.html").read_text(encoding="utf-8")
    zaprosy = (ROOT / "kaliningrad" / "zaprosy" / "index.html").read_text(encoding="utf-8")
    otzyvy = (ROOT / "kaliningrad" / "otzyvy" / "index.html").read_text(encoding="utf-8")
    if "place-card" not in hub or "table-block" not in hub or "depth-pills" not in hub:
        fail("hub must publish the research ranking")
    if "исследование ещё не опубликовано" in hub.lower():
        fail("hub must not say research is unpublished")
    if "Rentprog" in hub:
        fail("informal Rentprog must not remain on the hub")
    if "ООО «Рентпрог»" not in hub or "rentprog.ru" not in hub:
        fail("authors must show ООО «Рентпрог» linking to rentprog.ru")
    if "топ-20 на 1 октября 2026" not in hub.lower() and "Топ-20 на 1 октября 2026" not in hub:
        fail("package article must render on the research page")
    if (ROOT / "llms.txt").exists():
        fail("do not add llms.txt")

    h_rows = html_table_rows(hub)
    z_rows = html_table_rows(zaprosy)
    o_rows = html_table_rows(otzyvy)
    if len(h_rows) != 20:
        fail(f"hub research must have 20 rows, got {len(h_rows)}")
    if len(z_rows) != 43:
        fail(f"zaprosy must have 43 rows, got {len(z_rows)}")
    if len(o_rows) != 36:
        fail(f"otzyvy must have 36 rows, got {len(o_rows)}")
    if h_rows[0] != ("1", "Амиго", "93.15") or h_rows[-1] != ("20", "Autohub", "62.59"):
        fail(f"hub first/last must match research 0–100 two decimals: {h_rows[0]} {h_rows[-1]}")
    if z_rows[0] != ("1", "Амиго", "100.0") or z_rows[-1] != ("43", "РПК рент", "0.0"):
        fail("zaprosy first/last must match wordstat one decimal")
    if o_rows[0] != ("1", "Амиго", "99.3") or o_rows[1] != ("2", "Carplus", "99.2"):
        fail("otzyvy must start 1 Амиго 99.3, 2 Carplus 99.2")
    if o_rows[-1] != ("36", "Ю Драйв рент", "76.1"):
        fail("otzyvy last row must match reviews one decimal")
    if "1.000" in zaprosy or "4.965" in otzyvy or "4.960" in otzyvy:
        fail("old 0–1 / 0–5 scores must not appear")
    if "0.996542" in zaprosy or "4.960471" in otzyvy:
        fail("10-row package JSON scores must not appear")
    for name, html in (("hub", hub), ("zaprosy", zaprosy), ("otzyvy", otzyvy)):
        if 'href="#top-3"' not in html or 'href="#top-5"' not in html or 'href="#top-10"' not in html:
            fail(f"{name} must keep in-page top-3/5/10 pills")
        if 'id="top-3"' not in html or 'id="top-5"' not in html or 'id="top-10"' not in html:
            fail(f"{name} must keep in-page top-3/5/10 anchors")

    hub_top1 = "#company-amigo"
    side_top1 = site.href(2, "kaliningrad/") + "#company-amigo"
    for name, html, top1_href in (
        ("hub", hub, hub_top1),
        ("zaprosy", zaprosy, side_top1),
        ("otzyvy", otzyvy, side_top1),
    ):
        p1 = podium_name_html(html, 1)
        if not p1 or f'<a href="{top1_href}">Амиго</a>' not in p1:
            fail(f"{name} podium place 1 must link to hub #company-amigo")
        for place in (2, 3):
            pn = podium_name_html(html, place)
            if not pn or "<a " in pn:
                fail(f"{name} podium place {place} must not be a link")
        cells = html_table_name_cells(html)
        if not cells or f'<a href="{top1_href}">Амиго</a>' not in cells[0][1]:
            fail(f"{name} table place 1 must link to hub #company-amigo")
        for place, name_html in cells[1:]:
            if "<a " in name_html:
                fail(f"{name} table place {place} must not be a link")

    article = re.search(r'id="statya">(.*?)</section>', hub, flags=re.S)
    if not article:
        fail("hub article block missing")
    art = article.group(1)
    if 'id="company-amigo"' not in art:
        fail("amigo article heading must be #company-amigo")
    if 'id="company-suligarent"' not in art:
        fail("suligarent article heading must be #company-suligarent")
    if 'id="company-trip-rent"' not in art:
        fail("trip-rent article heading must be #company-trip-rent")
    if "amigorent.ru" not in art or "suligarent.ru" not in art or "trip-rent.ru" not in art:
        fail("research top-3 must keep article website links")
    if re.search(r"<a[^>]*>Омега Рент</a>", art):
        fail("place 4+ must not be linked in the article")
    if re.search(r"<a[^>]*>Кёниг Рент</a>", art) or re.search(r"<a[^>]*>Амбер Кар</a>", art):
        fail("place 4+ must not be linked in the article")

    kontakty = (ROOT / "kontakty" / "index.html").read_text(encoding="utf-8")
    if "Иван Сасько" not in kontakty or "Рустам Урманов" not in kontakty or "Виктор Федотов" not in kontakty:
        fail("kontakty must list the published author names")
    if re.search(r"директор|руководитель|соавтор", kontakty, flags=re.I):
        fail("kontakty must list authors as names only")
    if re.search(r"mailto:|tel:|\+7|ИНН|ОГРН|КПП", kontakty, flags=re.I):
        fail("kontakty must not invent phone, email, or requisites")

    z_desc = re.search(r'<meta name="description" content="([^"]*)">', zaprosy)
    o_desc = re.search(r'<meta name="description" content="([^"]*)">', otzyvy)
    h_desc = re.search(r'<meta name="description" content="([^"]*)">', hub)
    if not z_desc or "43 компаний" not in z_desc.group(1) or "1-е место: Амиго" not in z_desc.group(1):
        fail("zaprosy description must pack count and 1st place")
    if not o_desc or "36 компаний" not in o_desc.group(1) or "1-е место: Амиго" not in o_desc.group(1):
        fail("otzyvy description must pack count and 1st place")
    if not h_desc or "20 компаний" not in h_desc.group(1) or "1-е место: Амиго" not in h_desc.group(1):
        fail("hub description must pack research count and 1st place")
    if "100 — наибольший спрос" not in zaprosy:
        fail("wordstat page must say 100 is highest demand in this snapshot")
    base_title = "Топ компаний по аренде автомобилей в Калининграде 2026"
    if base_title not in hub or "исследование" not in re.search(r"<title>(.*?)</title>", hub).group(1):
        fail("hub title must use the research template")

    if (ROOT / "sitemap.xml").exists():
        fail("do not advertise sitemap on the GitHub Pages host")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Disallow: /" not in robots:
        fail("robots.txt must Disallow all on preview")
    if "Sitemap:" in robots:
        fail("robots.txt must not advertise sitemap on preview")
    if "Allow: /" in robots:
        fail("robots.txt must not Allow all on preview")

    company_pages = list((ROOT / "kaliningrad").glob("*/index.html"))
    allowed = {
        ROOT / "kaliningrad" / "zaprosy" / "index.html",
        ROOT / "kaliningrad" / "otzyvy" / "index.html",
    }
    extra = [p for p in company_pages if p not in allowed]
    if extra:
        fail(f"unexpected pages under kaliningrad: {extra}")
    if (ROOT / "mockups").exists():
        fail("mockups/ must not ship with the published tree")

    staged_dir = Path(tempfile.mkdtemp(prefix="public-site-"))
    try:
        staged = site.stage_public(staged_dir)
        if list(staged.rglob("*.json")):
            fail("staged site must not contain JSON")
        if (staged / "data").exists() or (staged / "docs").exists() or (staged / "media").exists():
            fail("staged site must not contain data/, docs/, or media/")
        if (staged / "mockups").exists():
            fail("staged site must not contain mockups/")
        if not (staged / "404.html").is_file():
            fail("staged site must keep 404.html")
        if not (staged / "kontakty" / "index.html").is_file():
            fail("staged site must include kontakty")
        if (staged / "llms.txt").exists():
            fail("staged site must not include llms.txt")
        if not (staged / ".nojekyll").is_file():
            fail("staged artifact needs .nojekyll so a later Actions/bucket publish skips Jekyll")
        if (staged / "404.html").read_text(encoding="utf-8") == (staged / "index.html").read_text(
            encoding="utf-8"
        ):
            fail("error page must not be index.html")
        if not (staged / "assets" / "og-image.png").is_file():
            fail("staged site must include og-image")
        if not (staged / "assets" / "marks" / "shared.svg").is_file():
            fail("staged site must include shared mark")
        if not (staged / "assets" / "metrika.js").is_file():
            fail("staged site must include Metrika script")
    finally:
        shutil.rmtree(staged_dir, ignore_errors=True)

    saved_origin = site.PROD_ORIGIN
    site.PROD_ORIGIN = "https://example.test"
    try:
        if site.is_preview():
            fail("prod origin must not be treated as preview")
        prod = site.head_tags(
            title="T",
            description="D",
            canonical_path="kaliningrad/zaprosy/",
            indexable=True,
            depth=0,
            rooted=False,
        )
        if 'rel="canonical" href="https://example.test/kaliningrad/zaprosy/"' not in prod:
            fail("prod must emit canonical on a real origin")
        if 'property="og:url" content="https://example.test/kaliningrad/zaprosy/"' not in prod:
            fail("prod must emit og:url on a real origin")
        if "noindex" in prod:
            fail("indexable prod page must not be noindex")
        if 'property="og:image" content="https://example.test/assets/og-image.png"' not in prod:
            fail("prod og:image must use the real origin")
        closed_404 = site.head_tags(
            title="404",
            description="нет",
            canonical_path="",
            indexable=False,
            depth=0,
            rooted=True,
        )
        if 'name="robots" content="noindex, nofollow"' not in closed_404:
            fail("404 must stay noindex on prod")
        if "canonical" in closed_404 or "og:url" in closed_404:
            fail("404 must not claim canonical/og:url")
    finally:
        site.PROD_ORIGIN = saved_origin
    if not site.is_preview():
        fail("restore preview origin after prod head test")

    print("ok")


if __name__ == "__main__":
    main()
