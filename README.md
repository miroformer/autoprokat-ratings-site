# autoprokat-ratings-site

Витрина рейтингов автопрокатов. Договорённости: [docs/project-context.md](docs/project-context.md).

Пробная статика из `data/site-export/package-2026-09-26.json`. Исследование в JSON не публикуем.

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
