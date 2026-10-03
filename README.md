# autoprokat-ratings-site

Витрина рейтингов автопрокатов. Договорённости: [docs/project-context.md](docs/project-context.md).

Живой срез: `docs/site-export/package-2026-10-01.json` (`as_of` 2026-10-01). Места — из `place`, баллы — `score` 0–100 как в пакете (research два знака, wordstat/reviews один). `score_raw` не показываем. Статья и авторы — markdown из пакета, не `pending-edits`. `package-2026-09-26.json` не источник.

- `/kaliningrad/` — исследование
- `/kaliningrad/zaprosy/` — wordstat (100 = наибольший спрос в этом срезе)
- `/kaliningrad/otzyvy/` — отзывы
- `/metodika/` — методика из `docs/site-export/`
- `/kontakty/` — контакты (футер, не pill-навигация)

`llms.txt` — индекс публичных страниц и факты среза. JSON-LD: Organization на страницах, Article на исследовании. Нет AggregateRating.

Превью GitHub Pages закрыто от индекса: `noindex, nofollow` и `robots.txt` Disallow. Sitemap на этом хосте не публикуем. Canonical/`og:url` нет: github.io не канон. Прод-домен позже: `topautoprokat.ru`. В опубликованное дерево (артефакт `public-site` и `_config.yml` exclude) не входят `data/`, `docs/`, JSON среза, `mockups/`.

Дизайн A, знак `assets/marks/shared.svg`. Счётчик Метрики 113370218 — официальный тег, CSP: `mc.yandex.ru` / `mc.yandex.com`. Ключи Yandex Cloud в репозиторий не кладём.

Пересборка: `python3 build.py && python3 check_build.py`

## Открыть локально

Из корня репозитория:

```bash
python3 -m http.server 8765
```

http://127.0.0.1:8765/
