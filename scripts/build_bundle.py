#!/usr/bin/env python3
"""
Постобработка экспорта из Claude Design в готовый к деплою index.html.

Зачем: Claude Design отдаёт самодостаточный бандл (см. src/raw-bundle.html),
но без осмысленного <title>, без SEO/OG-тегов и с именем-кириллицей. Этот
скрипт детерминированно и ИДЕМПОТЕНТНО приводит бандл к деплой-виду, чтобы
при каждом новом экспорте достаточно было заменить src/raw-bundle.html и
один раз запустить скрипт — а не повторять ручную правку <head>.

Использование:
    python3 scripts/build_bundle.py
    DOMAIN=example.com python3 scripts/build_bundle.py   # включить кастомный домен

Что делает:
  1. читает src/raw-bundle.html;
  2. проставляет <html lang="ru">;
  3. меняет <title> на осмысленный;
  4. инъектирует блок SEO/OpenGraph/Twitter-мета между маркерами
     <!-- dc-inject:start --> ... <!-- dc-inject:end --> (повторный запуск
     заменяет блок, а не дублирует);
  5. пишет результат в index.html в корне;
  6. при заданном DOMAIN пишет файл CNAME (для кастомного домена GitHub Pages)
     и использует https://DOMAIN как канонический origin; иначе берёт
     https://pyramidheadshark.github.io.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# --- Конфиг контента. Правь здесь — переживёт ре-экспорт из Claude Design. ---
SITE_TITLE = "Никита Смирнов — ML-инженер · Портфолио"
SITE_DESCRIPTION = (
    "Портфолио Никиты Смирнова: AI-инфраструктура TechCon, фреймворк Scaffold "
    "и ML-разработка. Проекты, метрики, достижения и публичные выступления."
)
SITE_AUTHOR = "Никита Смирнов"
THEME_COLOR = "#0D1117"
OG_IMAGE_FILE = "og-image.png"  # лежит рядом с index.html, деплоится вместе
DEFAULT_ORIGIN = "https://pyramidheadshark.github.io"

START = "<!-- dc-inject:start -->"
END = "<!-- dc-inject:end -->"

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src" / "raw-bundle.html"
OUT = REPO_ROOT / "index.html"
CNAME = REPO_ROOT / "CNAME"


def build_meta_block(origin: str) -> str:
    og_image = f"{origin}/{OG_IMAGE_FILE}"
    lines = [
        START,
        f'  <meta name="description" content="{SITE_DESCRIPTION}">',
        f'  <meta name="author" content="{SITE_AUTHOR}">',
        f'  <meta name="theme-color" content="{THEME_COLOR}">',
        f'  <link rel="canonical" href="{origin}/">',
        '  <meta property="og:type" content="website">',
        '  <meta property="og:locale" content="ru_RU">',
        f'  <meta property="og:site_name" content="{SITE_AUTHOR}">',
        f'  <meta property="og:title" content="{SITE_TITLE}">',
        f'  <meta property="og:description" content="{SITE_DESCRIPTION}">',
        f'  <meta property="og:url" content="{origin}/">',
        f'  <meta property="og:image" content="{og_image}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{SITE_TITLE}">',
        f'  <meta name="twitter:description" content="{SITE_DESCRIPTION}">',
        f'  <meta name="twitter:image" content="{og_image}">',
        END,
    ]
    return "\n".join(lines)


def main() -> int:
    if not SRC.exists():
        print(f"ОШИБКА: нет {SRC}. Положи свежий экспорт из Claude Design сюда.",
              file=sys.stderr)
        return 1

    domain = os.environ.get("DOMAIN", "").strip()
    origin = f"https://{domain}" if domain else DEFAULT_ORIGIN

    html = SRC.read_text(encoding="utf-8")

    # 1. lang
    html = re.sub(r"<html(?:\s+lang=\"[^\"]*\")?>", '<html lang="ru">', html, count=1)

    # 2. title
    html = re.sub(r"<title>.*?</title>",
                  f"<title>{SITE_TITLE}</title>", html, count=1, flags=re.S)

    # 3. meta-блок (идемпотентно)
    meta_block = build_meta_block(origin)
    if START in html and END in html:
        html = re.sub(re.escape(START) + r".*?" + re.escape(END),
                      meta_block, html, count=1, flags=re.S)
    else:
        # вставляем сразу после <title>...</title>
        html = re.sub(r"(</title>)", r"\1\n" + meta_block, html, count=1)

    OUT.write_text(html, encoding="utf-8")
    print(f"OK: {OUT.relative_to(REPO_ROOT)} собран (origin={origin})")

    # 4. CNAME
    if domain:
        CNAME.write_text(domain + "\n", encoding="utf-8")
        print(f"OK: CNAME = {domain}")
    elif CNAME.exists():
        print(f"ВНИМАНИЕ: {CNAME} существует, но DOMAIN не задан — оставлен без изменений.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
