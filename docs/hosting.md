---
cursor:
  subagentId: "bc-02e4bff4-af66-5d09-82d8-3b988261fbd0"
---

# Хостинг витрины

Статус: **решение принято, внедрение не начато.** Ничего не покупать, не деплоить, бакет не создавать. Стек генератора (Astro/Hugo/Next и т.п.) не фиксировать.

Дата сверки REG.RU и webhost1: **29 сентября 2026**. Факты Yandex / Timeweb / Cloudflare Pages — с 26 сентября 2026, в этой сверке не перепроверялись.

Опора: [контекст](project-context.md), [ветки](workstreams.md). Издатель: ООО «Рентпрог». Калининград — первый регион. Один хост, регионы папками. Статика из файла среза, не SPA. Агент пересобирает HTML при новом срезе; предыдущий — в архиве индекса. Канал: органика, Яндекс + Google. Слот баннера — позже. Счётчики — когда будет прод-URL.

## Решение (принято)

| | Факт |
|---|---|
| Прод | **Yandex Object Storage**, режим **Hosting** (бакет как сайт). |
| Превью | **GitHub Pages**. Не прод. На прод не переносить. |
| Домен / DNS | Регистратор **REG.RU**. Зона остаётся там. DNS на бакет: apex — **ANAME** на `<домен>.website.yandexcloud.net`; 3+ уровень — **CNAME**. Shared-хостинг REG.RU **не** берём. |
| Не выбрано | REG.RU shared Linux, webhost1 NVMe, Timeweb App Platform, Cloudflare Pages как прод. |

Внедрение **ждёт**: платёжный аккаунт Yandex Cloud и **имя домена**. Имя домена, ID облака / каталога / бакета — **нет данных, не выдумываем**.

**Нет данных (не выдумываем):** имя домена, ID облака Yandex Cloud, бюджет в ₽, объём трафика, частота обхода роботами, размер будущего архива в файлах. НДС на карточках REG.RU и webhost1 в публичном тексте не подписан.

## Класс хостинга

Нужен **статический файловый хостинг**: отдача готового HTML/CSS/JS (папки регионов + архив дат). Сервер приложения (PHP/Node на проде) не обязателен: сборка — у агента/CI, хост только раздаёт файлы.

Подходит: object storage в режиме website **или** pages-платформа под уже собранную статику. Не подходит как основной класс: SPA-хостинг с fallback всех URL на `/`, VPS «на всякий случай», CMS.

**Shared Linux (REG.RU, webhost1)** — соседний класс: Apache/Nginx + PHP + почта. Статический HTML там открывается, но стек и лимиты CPU/RPS/inode заточены под CMS, не под «только файлы». Git из коробки (push → сайт) нет. Для этой витрины это не лучше object storage / pages. Сверка ниже; **не выбраны.**

## Сверка (архив подбора)

Ниже — факты сверки. Прод уже выбран: § «Решение». Внедрение не начато.

### 1. Yandex Object Storage, режим Hosting — выбран как прод

РФ-облако, бакет как сайт. Документация: [хостинг](https://yandex.cloud/ru/docs/storage/operations/hosting/setup), [свой домен](https://yandex.cloud/ru/docs/storage/operations/hosting/own-domain), [HTTPS](https://yandex.cloud/ru/docs/storage/operations/hosting/certificate), [тарифы](https://docs.yandex.cloud/ru/ru/storage/pricing.md).

| Критерий | Факт |
|---|---|
| Яндекс-краулер | Хостинг в `ru-central1`. Отдельного «бонуса в ранжировании за Яндекс Cloud» в справке Вебмастера нет. Индексация иностранных хостов у Яндекса разрешена; блокировок робота самой платформой в документации нет. |
| SSL | Let's Encrypt через Certificate Manager; для своего домена — загрузка сертификата в бакет. HTTP→HTTPS после настройки HTTPS включается сам. TLS 1.0/1.1 с 1 августа 2025 не поддерживаются. |
| Деплой git/CI | Нативного git-автодеплоя нет. Выгрузка через S3 API / AWS CLI (`endpoint` `https://storage.yandexcloud.net`, регион `ru-central1`) из CI или агента. Генератор не фиксируется: на хост уходят уже собранные файлы. |
| Цена (публичная, РФ, с НДС в ₽) | Стандарт: первый **1 ГБ** хранения/мес бесплатно, далее **0,0033 ₽ за ГБ·час** (в примере документации ≈ **2,376 ₽/ГБ·мес**). Первые **10 000** PUT/POST/PATCH/LIST и **100 000** GET/HEAD/OPTIONS/мес бесплатно; далее GET **0,46 ₽ / 10 тыс.** Первые **100 ГБ** исходящего трафика/мес бесплатно; далее от **1,67994 ₽/ГБ** (ступень 100 ГБ–1 ТБ). DELETE не тарифицируется. Остаток free tier в конце месяца сгорает. |
| Логи | [Server logs](https://yandex.cloud/ru/docs/storage/concepts/server-logs): по умолчанию выкл.; пишутся в **другой** бакет ~раз в час, JSON. Полнота не гарантируется (не для полного учёта запросов). |
| Регион серверов | Object Storage: **ru-central1**. |
| Ограничения | Имя бакета = FQDN домена. Apex: DNS **ANAME** на `<домен>.website.yandexcloud.net`; 3+ уровень: **CNAME**. Публичный доступ к бакету. Запрос к папке без `/` → **302** на `/` + `index.html` — совпадает с сеткой `/kaliningrad/`. Error document — один файл на 4xx; **не** ставить `index.html` как error (это SPA-режим). Нужен платёжный аккаунт Yandex Cloud. |

### 2. Timeweb Cloud App Platform, Frontend HTML/CSS/JS — не выбран

РФ-провайдер. Тип «уже собранная статика» (в доке: Hugo/Astro/Jekyll и т.п. как пример сборки **до** деплоя, не как выбор стека). Документация: [HTML/CSS/JS](https://timeweb.cloud/docs/apps/deploying-frontend-apps/static-website), [деплой frontend](https://timeweb.cloud/docs/apps/deploying-frontend-apps), [тариф frontend](https://timeweb.cloud/docs/apps/frontend-pricing), [панель](https://timeweb.cloud/docs/apps/upravlenie-apps-v-paneli), [зоны](https://timeweb.cloud/docs/zony-dostupnosti/servisy-i-zony-dostupnosti).

| Критерий | Факт |
|---|---|
| Яндекс-краулер | Серверы в РФ (для витрины — **MSK-1** или **SPB-3**). Блокировок YandexBot платформой в документации нет. |
| SSL | Let's Encrypt на технический и на свой домен, автопродление. **Свой/платный сертификат загрузить нельзя** (документация App Platform). |
| Деплой git/CI | GitHub / GitLab / Bitbucket: автодеплой по push (опция «сборка по последнему коммиту»). Репозиторий по URL — **без** автодеплоя, ручной запуск. Для HTML/CSS/JS платформа **не** собирает проект: отдаёт готовую папку (`public` / `dist` / корень). |
| Цена (публичная) | **0,000495 ₽** за входящий HTTP-запрос (в т.ч. CSS/JS/картинки; метод не важен) = **4,95 ₽ / 10 000**. Списание почасовое; нет денег → приложение **останавливается**. Диск **2 ГБ NVMe**, конфиг сервера не выбирается. На сайте сервиса также «от 1 ₽»; это маркетинговая вилка, рабочая модель — pay-per-request. Можно поставить лимит запросов — после лимита сайт **останавливается**. |
| Логи | Frontend: вкладка «Логи доступа», **только последние сутки**; скачивание до **10 000** строк. Логи деплоя — отдельно. В доке панели: счётчик запросов frontend «появится позже»; в доке тарифа — дашборд с графиком запросов. На дату сверки это **расхождение в документации**, что именно видно в панели — не проверялось живым аккаунтом. |
| Регион серверов | App Platform frontend: **SPB-3, MSK-1, NSK-1** (только frontend), также AMS-1 / FRA-1 / ALA-1. Для этой витрины — РФ-зона. |
| Ограничения | Свой домен: A-запись; для домена *в панели* Timeweb в одной из док указаны **их NS**. Роботы и баннеры дают те же платные запросы, что и люди. Остановка по лимиту/нулевому балансу для органики вредна. Заявлен 152-ФЗ на уровне компании. |

### 3. Cloudflare Pages (Free) — не выбран как прод

Глобальный static CDN. Документация: [лимиты](https://developers.cloudflare.com/pages/platform/limits/), [раздача страниц](https://developers.cloudflare.com/pages/configuration/serving-pages/), [Web Analytics](https://developers.cloudflare.com/pages/how-to/web-analytics/).

| Критерий | Факт |
|---|---|
| Яндекс-краулер | Яндекс индексирует сайты вне РФ. **Bot Fight Mode / WAF** в сообществах Cloudflare неоднократно режут YandexBot (в т.ч. «фейковый Яндекс»). На Free нет полноценных access-логов, чтобы это увидеть. Стабильность PoP и доступа из РФ на дату документа **официально не подтверждалась** — нет данных. |
| SSL | Universal SSL, свой домен. До **100** custom domains / проект (Free). |
| Деплой git/CI | GitHub/GitLab, до **500** сборок/мес, 1 параллельная, таймаут 20 мин. Можно отдавать уже собранную статику (генератор не фиксируется). |
| Цена (публичная) | **$0**: безлимит запросов и трафика статики на Free. |
| Логи | Web Analytics (JS-маяк) + базовая edge-сводка. Persistent HTTP access logs / Logpush — не Free (в справке — Enterprise / платные analytics). Логи Pages Functions — live-only, для чистой статики не нужны. |
| Регион серверов | Anycast CDN. Гарантированного «сервер в РФ» нет. |
| Ограничения | До **20 000 файлов** на Free, файл ≤ **25 MiB**. `/folder/index.html` → канон `/folder/` (сетке с папками регионов подходит). **Без** корневого `404.html` Pages считает сайт SPA и отдаёт `/` на любой путь — для этой витрины это запрещённый класс. Превью-деплои по умолчанию `noindex`. Не РФ-юрлицо. |

### 4. REG.RU, виртуальный хостинг Linux (ispmanager) — не выбран

Shared, не object storage и не pages. Статика заливается в каталог сайта. Документация: [тарифы](https://www.reg.ru/hosting/), [лимиты](https://www.reg.ru/hosting/restrictions), [серверы](https://help.reg.ru/support/hosting/zakaz-hostinga-rabota-s-uslugoy/gde-raspolozheny-servery-reg-ru-i-kakoye-po-na-nikh-ustanovleno), [Git](https://help.reg.ru/support/hosting/razmeshcheniye-sayta-otobrazheniye-v-brauzere/rabota-s-git-na-hostinge), [SSH](https://help.reg.ru/support/hosting/dostupy-i-podklyucheniye-panel-upravleniya-ftp-ssh/rabota-po-ssh-na-virtualnom-hostinge), [Let's Encrypt](https://help.reg.ru/support/ssl-sertifikaty/3-etap-ustanovka-ssl-sertifikata/rasshireniye-let-encrypt-v-ispmanager), [логи](https://help.reg.ru/support/hosting/razmeshcheniye-sayta-otobrazheniye-v-brauzere/logi-servera), [тест](https://help.reg.ru/support/hosting/zakaz-hostinga-rabota-s-uslugoy/besplatnyy-testovyy-period-hostinga), [домен](https://help.reg.ru/support/hosting/privyazka-domena-k-hostingu/kak-privyazat-domen-k-hostingu), [152-ФЗ](https://help.reg.ru/support/pravovyye-voprosy/personalnyye-dannyye/mery-zashchity-personalnykh-dannykh-v-reg-ru), [DDoS](https://help.reg.ru/support/hosting/zakaz-hostinga-rabota-s-uslugoy/kak-izmenit-rezim-zashiti-ddos-isp).

| Критерий | Факт |
|---|---|
| Яндекс-краулер | Виртуальный хостинг — Москва, пл. Академика Курчатова, д. 1. Блокировок YandexBot платформой в документации нет. В справке о лимите CPU прямо сказано, что всплеск может быть от поисковых роботов (в т.ч. YandexBot) — тогда сайт упирается в CPU, не в «запрет робота». Маркетинг: базовая защита DDoS **L3/L4 и L7** на всех тарифах ispmanager. Справка: бесплатно L3/L4 (DDoS-Guard); **расширенная L7** — отдельная услуга с чёрным/белым списком IP. Живой проверки YandexBot нет. |
| SSL | На всех тарифах заявлен бесплатный SSL (GlobalSign или Let's Encrypt). LE в ispmanager для домена, направленного на хостинг; HTTP→HTTPS — галочка в панели. Wildcard LE — проверка DNS (`ns1.hosting.reg.ru` / `ns2.hosting.reg.ru` или TXT вручную). Платный сертификат ставится в панели. |
| Деплой git/CI | Нативного автодеплоя GitHub/GitLab **нет**. Git на сервере есть (по умолчанию 1.7.1; алиас `git2192` → 2.19.2): SSH → `git clone` / `git pull` в корень сайта. **Host-Lite: SSH нет** (только FTP). CI агента: FTP/SFTP или SSH+git pull — со стороны агента, не продукт REG.RU. Генератор не фиксируется. |
| Цена (публичная, ₽/мес) | Карточки: **Host-0 420 ₽/мес** (5 038 ₽ / 12 мес, −15%); Host-1 658; Host-3 964. Сравнительная таблица «от»: Host-Lite **от 130**, Host-A **от 214**, Host-B **от 323**, Host-0 **от 272** (это вилка «от», не отдельная помесячная карточка). НДС в карточке не подписан. Тест-драйв **14 дней**, один раз, техдомен `u….*.regruhosting.ru`. Для юрлиц на сайте: ЭДО, оферта/индивидуальный договор, безнал. |
| Логи | Папка `logs` в корне услуги: ispmanager / FTP, в т.ч. access_log. Срок хранения архивов ротации в справке REG.RU не указан. |
| Регион серверов | Виртуальный хостинг: **Москва**, Курчатовский (Tier-III в маркетинге). Другие площадки REG.RU (СПб, Тольятти) к виртуальному хостингу в справке не относятся. |
| Ограничения | Nginx + Apache, AlmaLinux, `.htaccess`. Трафик «безлимит». Host-Lite: 15 сайтов, **7 ГБ**, 150k inode (уведомление >100k, блок >150k), **150 HTTP req/s** на домен; PHP/MySQL/SSH в блоке «в каждом тарифе» — **кроме Host-Lite**. Host-A: 1 сайт, 7 ГБ файлов, **2,5% CPU**. Рекомендуемые посетители при статическом HTML: Lite/A/B ~**1000/сутки**, Host-0/1 ~2000, Host-3 ~3000. Домен: NS `ns1.hosting.reg.ru` / `ns2.hosting.reg.ru` или A-запись на IP. Отдельной доки про 302 trailing slash как у Yandex Storage нет; типичный DirectoryIndex отдаёт `/kaliningrad/index.html` по `/kaliningrad/` — живьём не проверялось. Юрлицо хостера: ООО «Регистратор доменных имен РЕГ.РУ», серверы в РФ, оператор ПДн, УЗ-3. |

### 5. webhost1.ru, виртуальный хостинг NVMe — не выбран

Shared того же класса, что REG.RU. Провайдер: **ООО «Вебхост»** ([оферта](https://webhost1.ru/terms.pdf)). Документация: [NVMe](https://webhost1.ru/hosting), [виртуальный](https://webhost1.ru/hosting/virtual), [нагрузка](https://webhost1.ru/hosting/load/hosting), [Let's Encrypt](https://webhost1.ru/help/faq/hosting/www-domains/ssl_le), [SSL платный](https://webhost1.ru/services/ssl), [ЦОД](https://webhost1.ru/data-centers/datapro).

| Критерий | Факт |
|---|---|
| Яндекс-краулер | Серверы: Москва, ЦОД **DataPro**, Tier III, канал до ММТС-9. Заявлено соответствие 152-ФЗ за счёт размещения в РФ. На тарифе: защита ботов **BitNinja** + DDoS L3–L4. Блог BitNinja (2022): Google / Yandex / Bing crawlers в дефолтном whitelist. Cheatsheet BitNinja: часть краулеров всё же может попасть в greylist (CAPTCHA); глобальный whitelist «любых» ботов вендор на себя не берёт. Как именно webhost1 настроил shared NVMe — **нет публичных данных**. Живой проверки YandexBot нет. |
| SSL | Бесплатный Let's Encrypt в ispmanager (WWW-домен → «Новый Let's Encrypt сертификат»). Домен должен резолвиться на IP хостинга или на NS webhost1. Выпуск 10–30 мин, редко до 24 ч. HSTS и редирект HTTP→HTTPS при выпуске **не включать** (риск цикла). Платный GlobalSign — отдельный прайс (AlphaSSL от 1300 ₽/год и т.д.). |
| Деплой git/CI | Нативного автодеплоя GitHub **нет**. В составе тарифа: **SSH**, FTP, cron, `.htaccess`. Статья про `git clone` с GitHub на сайте — про VDS/сервер как среду разработки, не про продукт shared. Git на shared: нет отдельной инструкции; SSH заявлен, наличие бинаря git на NVMe **не подтверждено докой**. CI агента: FTP/SFTP или SSH — со стороны агента. Генератор не фиксируется. |
| Цена (публичная, ₽/мес) | Карточки: **NVME 15 GB — 236,25 ₽/мес** (15 ГБ, сайтов «неограниченно»); NVME 25 — 322,88; NVME 35 — 433,13. Периоды 1 / 6 / 12 / 24 мес; для 24 мес на 15 ГБ показаны 7 560 ₽ и 5 670 ₽ (−25%). Цена за 1 мес без скидки в вёрстке не отделена от «цены за месяц» 236,25. НДС не подписан. Тест **30 дней**. Работа с РФ ООО/ИП — да (договор, счета, акты; только РФ-регистрация). |
| Логи | Отдельной справки webhost1 «где access.log на NVMe» нет. Панель — ispmanager, у ispmanager логи WWW обычно есть; **на этом хосте не проверялось**. |
| Регион серверов | **Москва, DataPro.** |
| Ограничения | Трафик «неограниченно». SSH, cron, `.htaccess`, ежедневные бэкапы — в списке тарифа. Таблица нагрузки ([load](https://webhost1.ru/hosting/load/hosting)) — имена **SSD 3/10/15/20/30 GB и VIP**, не **NVME 15/25/35**. Соответствие текущих SKU старым лимитам CPU/PIDS/inode **не опубликовано**. При превышении нагрузки с нарушением работы сервера аккаунт **блокируют**. NS: `ns1.webhost1.com`, `ns2.webhost1.com`, `ns3.webhost1.org`, `ns4.webhost1.org` (обновление ~24 ч). Поведение `/folder/` → `index.html` живьём не проверялось. |

## Сводка

| | Yandex Object Storage | Timeweb App (статика) | Cloudflare Pages Free | REG.RU shared | webhost1 NVMe |
|---|---|---|---|---|---|
| Класс | object storage website | pages, готовые файлы | static CDN | shared Linux (PHP/почта) | shared Linux (PHP/почта) |
| Яндекс-робот | РФ, без WAF платформы | РФ, без WAF платформы | риск WAF/Bot Fight | РФ; CPU-лимит; L7 — отдельная услуга vs маркетинг | РФ; BitNinja (вендор: Yandex в whitelist; живьём нет) |
| SSL | LE / Certificate Manager | LE, чужой сертификат нельзя | Universal SSL | LE или GlobalSign | LE; платный GlobalSign отдельно |
| Git из коробки | нет (CI → S3) | да (GitHub/GitLab/Bitbucket) | да | нет (SSH `git pull`; Lite без SSH) | нет (SSH есть; git-бинарь в доке нет) |
| Цена | free tier + pay-as-you-go | 0,000495 ₽/запрос | $0 | от 130 ₽/мес (Lite) / Host-0 420 | NVME 15: 236,25 ₽/мес |
| Логи | JSON в бакет, неполные | access 24 ч / 10k строк | analytics, не access-log | `logs/` в панели/FTP | нет отдельной доки |
| Регион | ru-central1 | MSK/SPB (выбор) | CDN, не РФ-гарантия | Москва, Курчатовский | Москва, DataPro |
| РФ-юр. хостинг | да (Yandex Cloud) | да | нет | да (ООО РЕГ.РУ) | да (ООО «Вебхост») |
| Лимиты, важные витрине | бакет=FQDN, не SPA error | стоп при 0 ₽ / лимите запросов | 20k файлов; нужен 404.html | 150 req/s, 150k inode, CPU%; Lite без SSH | блок при нагрузке; лимиты NVMe ≠ таблица SSD |

Не сравнивались отдельно: Beget, Timeweb shared, Selectel/VK S3, GitHub Pages (превью уже есть), Netlify.

## Итог решения

Владелец выбрал **прод: Yandex Object Storage, режим Hosting.** Класс совпадает: файлы, папки регионов, trailing slash в доке, РФ, робот без WAF-прослойки, GET после free tier не гасит сайт, выгрузка собранного HTML из CI без привязки к генератору.

**REG.RU shared Linux — не выбран.** Домен остаётся у REG.RU только как регистратор/DNS, не как хостинг сайта.

**webhost1 — не выбран.**

Timeweb App Platform и Cloudflare Pages как прод — не выбраны. GitHub Pages остаётся **превью**, не прод.

Счётчики и баннер на выбор хоста не влияют.

## Внедрение (не начато)

Ждёт, не делать без фактов ниже. Ничего не покупать, не деплоить, бакет не создавать.

| Ждёт | Статус |
|---|---|
| Аккаунт Yandex Cloud (платёжный) | нет данных, ID облака не выдумывать |
| Имя домена | нет данных, FQDN не выдумывать; зона на REG.RU, DNS на бакет |
| Бакет, сертификат, выгрузка | не начинать до аккаунта и имени домена |
