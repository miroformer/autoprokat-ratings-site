# autoprokat-ratings-site

Витрина рейтингов автопрокатов. Договорённости: [docs/project-context.md](docs/project-context.md).

Места и баллы — из полных markdown-таблиц: `docs/site-export/wordstat-ranking-table.md` (запросы) и `docs/site-export/reviews-ranking-table.md` (отзывы). `ranking-table.md` — тот же список отзывов, не читаем. 10-строчный `package-2026-09-26.json` не источник мест; дата среза из пакета. Исследование не публикуем.

Превью GitHub Pages закрыто от индекса: `noindex, nofollow` и `robots.txt` Disallow. Sitemap на этом хосте не публикуем.

## Страницы

- `/` — оглавление
- `/kaliningrad/` — хаб без мест
- `/kaliningrad/zaprosy/` — wordstat
- `/kaliningrad/otzyvy/` — reviews
- `/metodika/` — методика

Пересборка: `python3 build.py && python3 check_build.py`

## Открыть локально

Из корня репозитория:

```bash
python3 -m http.server 8765
```

http://127.0.0.1:8765/

Или `file://`: открыть `index.html` в браузере (ссылки относительные).
