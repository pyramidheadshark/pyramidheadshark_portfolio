# Портфолио · Никита Смирнов

[![Deploy to GitHub Pages](https://github.com/pyramidheadshark/pyramidheadshark_portfolio/actions/workflows/deploy.yml/badge.svg)](https://github.com/pyramidheadshark/pyramidheadshark_portfolio/actions/workflows/deploy.yml)

Персональный сайт-портфолио ML-инженера. Спроектирован в Claude Design,
публикуется на GitHub Pages автоматически при каждом пуше в `main`.

🔗 **Живой сайт:** https://pyramidheadshark.github.io/pyramidheadshark_portfolio/

---

## Содержание

- [Архитектура](#архитектура)
- [Структура репозитория](#структура-репозитория)
- [Как обновить сайт](#как-обновить-сайт)
- [Build-скрипт](#build-скрипт)
- [Хостинг и CI/CD](#хостинг-и-cicd)
- [Кастомный домен](#кастомный-домен)
- [Известные ограничения](#известные-ограничения)

## Архитектура

Сайт собран в **Claude Design** и экспортируется как самодостаточный
HTML-бандл: внутри инлайн-React, dc-runtime и контент, которые
распаковываются и рендерятся в браузере. Внешних зависимостей при загрузке
ровно две — Google Fonts и ссылки на соцсети; никаких CDN.

Репозиторий хранит **и источник, и деплой-артефакт**:

- источник правды для дизайна — проект в Claude Design;
- его экспорты лежат в `src/` для истории и осмысленных диффов;
- готовый к публикации `index.html` детерминированно собирается из источника
  скриптом `scripts/build_bundle.py`.

## Структура репозитория

```
.
├── index.html              # деплой-артефакт (генерируется из src/raw-bundle.html)
├── og-image.png            # превью для соцсетей и мессенджеров
├── CNAME                   # кастомный домен (создаётся build-скриптом при DOMAIN)
├── scripts/
│   └── build_bundle.py     # идемпотентный пайплайн постобработки экспорта
├── src/                    # источник из Claude Design
│   ├── raw-bundle.html     # сырой экспорт (вход для сборки)
│   ├── Portfolio.dc.html   # dc-разметка (React-шаблон)
│   ├── support.js          # dc-runtime (generated, не редактировать вручную)
│   └── screenshots/        # ассеты проектов
└── .github/workflows/
    └── deploy.yml          # CI/CD: сборка и публикация в GitHub Pages
```

`src/Portfolio.dc.html` и `support.js` — «настоящий» источник Claude Design.
Локально без dc-bundler он не пересобирается, поэтому правки дизайна делаются
в Claude Design, а сюда коммитится свежий экспорт.

## Как обновить сайт

1. Внести правки в проекте **Claude Design** и экспортировать заново.
2. Перезаписать `src/raw-bundle.html` новым бандлом. По возможности обновить и
   `src/Portfolio.dc.html`, `src/support.js`, скриншоты.
3. Пересобрать артефакт:
   ```bash
   python3 scripts/build_bundle.py                       # origin = github.io
   DOMAIN=example.com python3 scripts/build_bundle.py     # с кастомным доменом
   ```
4. Закоммитить и запушить в `main` — деплой произойдёт автоматически.

## Build-скрипт

`scripts/build_bundle.py` делает экспорт пригодным к продакшену и **идемпотентен** —
повторный запуск не плодит дубли. На вход берёт `src/raw-bundle.html`, на выход
даёт `index.html`. Что он проставляет:

- `<html lang="ru">`;
- осмысленный `<title>`;
- блок SEO / OpenGraph / Twitter-мета между маркерами
  `<!-- dc-inject:start --> … <!-- dc-inject:end -->` (повторный запуск
  **заменяет** блок, а не дублирует);
- `CNAME` — при заданной переменной окружения `DOMAIN`.

Тексты мета-тегов (заголовок, описание, автор, OG-картинка) меняются в
константах в начале скрипта. Благодаря маркерам ручную правку `<head>` после
каждого ре-экспорта делать не нужно — достаточно одного запуска.

## Хостинг и CI/CD

Публикация на **GitHub Pages** через GitHub Actions. Пуш в `main` запускает
`.github/workflows/deploy.yml`:

1. устанавливает Python;
2. выполняет `build_bundle.py` (с `DOMAIN` из переменной репозитория);
3. собирает чистый каталог `_site` — только `index.html`, `og-image.png`, `CNAME`;
4. публикует артефакт через `actions/deploy-pages`.

Источник (`src/`) и скрипты в продакшен не попадают.

> Включить Pages: **Settings → Pages → Source: GitHub Actions** (один раз).

## Кастомный домен

1. В DNS добавить запись на домен (CNAME на `pyramidheadshark.github.io` для
   поддомена либо A/AAAA-записи GitHub Pages для апекса).
2. Задать переменную репозитория **`PAGES_DOMAIN`**
   (Settings → Secrets and variables → Actions → Variables → New variable).
3. Следующий деплой сам создаст файл `CNAME` и проставит канонический origin.

Без `PAGES_DOMAIN` сайт работает на адресе `*.github.io`.

## Известные ограничения

- Контент рендерится клиентом, поэтому в исходном HTML его нет — мета-теги в
  `<head>` нужны, чтобы ссылка корректно превьюилась и индексировалась.
- При загрузке кратко мелькает экран «Unpacking…» — штатное поведение
  самораспаковывающегося бандла.
