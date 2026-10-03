#!/usr/bin/env python3
"""Guards for the generated preview. Run after build.py."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PAGES = [
    ROOT / "index.html",
    ROOT / "kaliningrad" / "index.html",
    ROOT / "kaliningrad" / "zaprosy" / "index.html",
    ROOT / "kaliningrad" / "otzyvy" / "index.html",
    ROOT / "metodika" / "index.html",
    ROOT / "404.html",
]


def fail(msg: str) -> None:
    print("FAIL:", msg, file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    sys.path.insert(0, str(ROOT))
    import build as site

    if site.e('<img src=x onerror=alert(1)>') == '<img src=x onerror=alert(1)>':
        fail("names must be HTML-escaped")
    if site.format_score("<script>") is not None:
        fail("score must not pass through a raw string")
    if site.format_score(None) is not None:
        fail("null score must be empty")
    if site.company_id_of({"id": "../evil"}) is not None:
        fail("company_id must be kebab latin")
    if site.company_id_of({"id": "amigo"}) != "amigo":
        fail("valid company_id rejected")
    if site.place_of({"rank": "first"}) is not None:
        fail("place must be an integer")
    if site.place_of({"rank": 3}) != 3:
        fail("integer place rejected")
    if site.card_of({"card": {"pros": [], "cons": []}}) is not None:
        fail("empty card must not render")
    if not site.is_preview():
        fail("GitHub Pages host must be treated as preview")
    xss_table = site.table_html(
        [{"company_id": "x", "name": "<b>xss</b>", "place": 1, "score": 1, "card": None}]
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
    if "wordstat-ranking-table.md" not in src or "reviews-ranking-table.md" not in src:
        fail("generator must read full ranking markdown")
    if 'tables.get("wordstat")' in src or "tables.get('wordstat')" in src:
        fail("generator must not use package JSON wordstat as ranking source")
    if 'tables.get("reviews")' in src or "tables.get('reviews')" in src:
        fail("generator must not use package JSON reviews as ranking source")

    wordstat_md = site.parse_ranking_table(site.WORDSTAT_RANKING_MD)
    reviews_md = site.parse_ranking_table(site.REVIEWS_RANKING_MD)
    if len(wordstat_md) != 45:
        fail(f"wordstat markdown must have 45 rows, got {len(wordstat_md)}")
    if len(reviews_md) != 36:
        fail(f"reviews markdown must have 36 rows, got {len(reviews_md)}")
    if wordstat_md[0]["name"] != "Амиго" or wordstat_md[-1]["name"] != "РПК рент":
        fail("wordstat markdown first/last names mismatch")
    if reviews_md[0]["name"] != "Амиго" or reviews_md[1]["name"] != "Carplus":
        fail("reviews markdown must start Амиго, Carplus")
    if reviews_md[-1]["name"] != "Ю Драйв рент":
        fail("reviews markdown last name mismatch")
    try:
        site.parse_ranking_table(site.DOCS_EXPORT / "ranking-table.md")
        fail("ranking-table.md must be rejected")
    except ValueError:
        pass

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
        if "unsafe-inline" in text:
            fail(f"unsafe-inline on {path.relative_to(ROOT)}")
        if "rel=\"canonical\"" in text:
            fail(f"preview must not advertise canonical {path.relative_to(ROOT)}")
        if 'property="og:url"' in text:
            fail(f"preview must not set og:url {path.relative_to(ROOT)}")
        if 'property="og:image"' in text or 'name="twitter:image"' in text:
            fail(f"no share image — do not emit og:image on {path.relative_to(ROOT)}")
        if "schema.org" in text.lower() or "application/ld+json" in text.lower():
            fail(f"JSON-LD/schema.org on {path.relative_to(ROOT)}")
        if "aggregaterating" in text.lower() or 'itemprop="review' in text.lower():
            fail(f"review schema on {path.relative_to(ROOT)}")
        if "лучший прокат" in text.lower():
            fail(f"invented SEO slogan on {path.relative_to(ROOT)}")
        if "<script" in text.lower():
            fail(f"unexpected script on {path.relative_to(ROOT)}")
        if "mc.yandex" in text or "metrika" in text.lower():
            fail(f"Metrika stub on {path.relative_to(ROOT)}")
        if "gtag" in text.lower() or "googletagmanager" in text.lower():
            fail(f"counter stub on {path.relative_to(ROOT)}")
        if "ООО" in text or "Рентпрог" in text:
            fail(f"publisher legal name on {path.relative_to(ROOT)}")
        if "ваша реклама" in text.lower() or 'class="banner"' in text or "id=\"banner\"" in text:
            fail(f"empty banner rendered on {path.relative_to(ROOT)}")
        if "<base " in text.lower():
            fail(f"base href on {path.relative_to(ROOT)}")

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
        if 'name="twitter:card" content="summary"' not in text:
            fail(f"missing twitter:card on {path.relative_to(ROOT)}")
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
    if "place-card" in hub or "table-block" in hub or "depth-pills" in hub:
        fail("hub must ignore unpublished research and not show ranking table")

    zaprosy = (ROOT / "kaliningrad" / "zaprosy" / "index.html").read_text(encoding="utf-8")
    otzyvy = (ROOT / "kaliningrad" / "otzyvy" / "index.html").read_text(encoding="utf-8")

    def html_table_rows(html: str) -> list[tuple[str, str, str]]:
        bodies = re.findall(r"<tbody>\s*(.*?)\s*</tbody>", html, flags=re.S)
        if not bodies:
            return []
        return re.findall(
            r'<tr(?:\s[^>]*)?><td class="num">(\d+)</td><td>(.*?)</td>'
            r'<td class="num">(.*?)</td></tr>',
            bodies[0],
        )

    z_rows = html_table_rows(zaprosy)
    o_rows = html_table_rows(otzyvy)
    if len(z_rows) != 45:
        fail(f"zaprosy must have 45 markdown rows, got {len(z_rows)}")
    if len(o_rows) != 36:
        fail(f"otzyvy must have 36 markdown rows, got {len(o_rows)}")
    if z_rows[0] != ("1", "Амиго", "1.000") or z_rows[-1] != ("45", "РПК рент", "0.000"):
        fail("zaprosy first/last row must match wordstat markdown")
    if o_rows[0] != ("1", "Амиго", "4.965") or o_rows[1] != ("2", "Carplus", "4.960"):
        fail("otzyvy must start 1 Амиго, 2 Carplus")
    if o_rows[-1] != ("36", "Ю Драйв рент", "3.806"):
        fail("otzyvy last row must match reviews markdown")
    for md_row, html_row in zip(wordstat_md, z_rows):
        if html_row != (str(md_row["place"]), md_row["name"], md_row["score"]):
            fail(f"zaprosy HTML diverges from markdown at place {md_row['place']}")
    for md_row, html_row in zip(reviews_md, o_rows):
        if html_row != (str(md_row["place"]), md_row["name"], md_row["score"]):
            fail(f"otzyvy HTML diverges from markdown at place {md_row['place']}")
    if "0.996542" in zaprosy or "4.960471" in otzyvy:
        fail("10-row package JSON scores must not appear")
    for name, html in (("zaprosy", zaprosy), ("otzyvy", otzyvy)):
        if 'href="#top-3"' not in html or 'href="#top-5"' not in html or 'href="#top-10"' not in html:
            fail(f"{name} must keep in-page top-3/5/10 pills")
        if 'id="top-3"' not in html or 'id="top-5"' not in html or 'id="top-10"' not in html:
            fail(f"{name} must keep in-page top-3/5/10 anchors")

    z_desc = re.search(r'<meta name="description" content="([^"]*)">', zaprosy)
    o_desc = re.search(r'<meta name="description" content="([^"]*)">', otzyvy)
    if not z_desc or "45 компаний" not in z_desc.group(1) or "1-е место: Амиго" not in z_desc.group(1):
        fail("zaprosy description must pack markdown count and 1st place")
    if not o_desc or "36 компаний" not in o_desc.group(1) or "1-е место: Амиго" not in o_desc.group(1):
        fail("otzyvy description must pack markdown count and 1st place")
    if "Carplus" in (z_desc.group(1) if z_desc else ""):
        fail("zaprosy description must not take reviews 2nd place")

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
        )
        if 'rel="canonical" href="https://example.test/kaliningrad/zaprosy/"' not in prod:
            fail("prod must emit canonical on a real origin")
        if 'property="og:url" content="https://example.test/kaliningrad/zaprosy/"' not in prod:
            fail("prod must emit og:url on a real origin")
        if "noindex" in prod:
            fail("indexable prod page must not be noindex")
        closed_404 = site.head_tags(
            title="404",
            description="нет",
            canonical_path="",
            indexable=False,
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
