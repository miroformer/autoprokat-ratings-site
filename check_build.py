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
    if "ranking-table.md" in src:
        fail("generator must not read ranking markdown")
    if "package-2026-09-26.json" not in src:
        fail("generator must keep package JSON as the data source")

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

    hub = (ROOT / "kaliningrad" / "index.html").read_text(encoding="utf-8")
    if "place-card" in hub or "table-block" in hub or "depth-pills" in hub:
        fail("hub must ignore unpublished research and not show ranking table")

    zaprosy = (ROOT / "kaliningrad" / "zaprosy" / "index.html").read_text(encoding="utf-8")
    otzyvy = (ROOT / "kaliningrad" / "otzyvy" / "index.html").read_text(encoding="utf-8")
    for name, html in (("zaprosy", zaprosy), ("otzyvy", otzyvy)):
        rows = re.findall(r"<tbody>\s*(.*?)\s*</tbody>", html, flags=re.S)
        if not rows:
            fail(f"no table on {name}")
        trs = re.findall(r"<tr\b", rows[0])
        if len(trs) != 10:
            fail(f"{name} must have 10 package JSON rows, got {len(trs)}")

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

    print("ok")


if __name__ == "__main__":
    main()
