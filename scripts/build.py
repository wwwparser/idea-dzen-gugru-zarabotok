"""Build a portable HTML handbook from local, trusted content."""
import html
import json
import argparse
import shutil
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
chapters = json.loads((ROOT / 'content/chapters.json').read_text(encoding='utf-8'))
segments = json.loads((ROOT / 'data/transcript/lesson.json').read_text(encoding='utf-8'))
nav = ''.join(f'<a href="#{c["id"]}"><span>{i:02d}</span>{html.escape(c["title"])}</a>' for i, c in enumerate(chapters, 1))
sections = []
for c in chapters:
    watch = f'<button class="watch" data-time="{c["time"]}">Смотреть этот шаг в видео ↗</button>' if c['time'] is not None else ''
    sections.append(f'<section class="chapter" id="{c["id"]}"><p class="eyebrow">{c["label"]}</p><h2>{html.escape(c["title"])}</h2>{watch}{c["html"]}<label class="done"><input type="checkbox" data-chapter="{c["id"]}"> Задание главы выполнено</label></section>')
page = '''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Практическое пособие: разбор видео о Claude Code и Дзене, проверка фактов и создание HTML-сайта.">
<title>От видео к своему проекту — практический учебник</title>
<link rel="stylesheet" href="assets/style.css"><script src="assets/transcript.js" defer></script><script src="assets/app.js" defer></script></head>
<body><a class="skip" href="#main">Перейти к содержанию</a>
<header class="topbar"><a class="brand" href="#main"><span class="brand-mark">П</span> Практикум<span class="edition"> / Дзен и AI</span></a><a class="top-link" href="#transcript">Видео и расшифровка ↗</a></header>
<div class="layout"><aside><div class="aside-inner"><p class="eyebrow">Ваш маршрут</p><nav aria-label="Главы учебника">NAV</nav><a class="transcript-link" href="#transcript">09 &nbsp; Расшифровка видео</a><div class="progress-box"><div><span>Пройдено глав</span><b id="progress-label">0 / 8</b></div><progress id="progress" max="8" value="0">0</progress><small id="storage-note">Прогресс сохраняется в этом браузере</small><button id="reset" type="button">Сбросить отметки</button></div><p class="aside-note">Локальное пособие<br>Подготовлено 12.10.2026</p></div></aside>
<main id="main"><section class="hero"><p class="eyebrow">Самостоятельная работа · 8 глав</p><h1>От видео<br>к своему <em>проекту.</em></h1><p class="hero-text">Разберите систему автора, подготовьте свой материал и соберите понятный HTML-сайт. Шаг за шагом, с заданиями и проверкой результата.</p><div class="hero-actions"><a class="primary" href="#start">Начать практикум <span>→</span></a><a class="secondary" href="examples/first-site/index.html">Открыть пример сайта ↗</a></div><div class="hero-meta"><span><b>23:35</b> исходного видео</span><span><b>8</b> практических глав</span><span><b>Локально</b> без регистрации</span></div></section>
<div class="editor-note"><span>На полях</span><p>Ролик посвящён статьям для Дзена. Задание по HTML добавлено отдельно. Заявления автора о доходах не подтверждены независимой проверкой.</p></div>
SECTIONS
<section class="chapter" id="transcript"><p class="eyebrow">09 · Исходный материал</p><h2>Видео и расшифровка</h2><p>Машинная расшифровка GigaAM. Названия, числа и отдельные слова могут быть распознаны неверно. Нажмите таймкод, чтобы сверить фрагмент с записью.</p><video id="video" controls preload="metadata" aria-label="Исходный ролик Claude Code и Дзен"><source src="data/media/lesson.mp4" type="video/mp4">Откройте видео по ссылке ниже.</video><p id="video-status" role="status"></p><div class="downloads"><a href="data/media/lesson.mp4">Видео MP4 ↗</a><a href="data/media/lesson.flac">Аудио FLAC ↗</a><a href="data/transcript/lesson.txt" download>Текст TXT ↓</a><a href="data/transcript/lesson.srt" download>Субтитры SRT ↓</a><a href="data/transcript/lesson.json" download>Сегменты JSON ↓</a></div><label class="search-label" for="search">Найти фразу в расшифровке</label><input id="search" type="search" placeholder="Например: заголовки, публикация, монетизация"><p id="search-count" class="search-count" role="status"></p><div id="segments"></div><noscript>Для поиска нужен JavaScript. Полную расшифровку можно открыть по ссылке «Текст TXT» выше.</noscript></section>
<footer>Материалы для личной практики · источники и ограничения указаны в главе 08.<br><a href="#main">Вернуться к началу ↑</a></footer></main></div></body></html>'''
page = page.replace('NAV', nav).replace('SECTIONS', '\n'.join(sections))
(ROOT / 'index.html').write_text(page, encoding='utf-8')
(ROOT / 'assets').mkdir(exist_ok=True)
safe_json = json.dumps(segments, ensure_ascii=False).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
(ROOT / 'assets/transcript.js').write_text('window.TRANSCRIPT = ' + safe_json + ';\n', encoding='utf-8')
print(f'Built {len(chapters)} chapters and {len(segments)} transcript segments')

parser = argparse.ArgumentParser()
parser.add_argument('--github-pages', action='store_true')
args = parser.parse_args()
if args.github_pages:
    public = ROOT / 'docs'
    public.mkdir(exist_ok=True)
    for folder in ['assets', 'examples', 'templates']:
        shutil.copytree(ROOT / folder, public / folder, dirs_exist_ok=True)
    (public / 'data/transcript').mkdir(parents=True, exist_ok=True)
    for suffix in ['txt', 'json', 'srt']:
        shutil.copy2(ROOT / f'data/transcript/lesson.{suffix}', public / f'data/transcript/lesson.{suffix}')
    shutil.copy2(ROOT / 'PROJECT_PLAN.md', public / 'PROJECT_PLAN.md')
    embed = '<iframe id="video" title="Исходный ролик Claude Code и Дзен" src="https://kinescope.io/embed/eHTc1UJ83wrTzEZL2kxKWz" allow="autoplay; fullscreen; picture-in-picture; encrypted-media" allowfullscreen loading="lazy"></iframe>'
    online = re.sub(r'<video id="video".*?</video>', embed, page, flags=re.S)
    online = online.replace('<script src="assets/app.js" defer></script>', '<script src="assets/online-player.js" defer></script><script src="assets/app.js" defer></script>')
    online = online.replace('<a href="data/media/lesson.mp4">Видео MP4 ↗</a><a href="data/media/lesson.flac">Аудио FLAC ↗</a>', '<a href="https://kinescope.io/eHTc1UJ83wrTzEZL2kxKWz" target="_blank" rel="noopener">Открыть оригинальное видео ↗</a>')
    online = online.replace('Локальное пособие', 'Открытый учебник').replace('<b>Локально</b>', '<b>Онлайн</b>')
    online = online.replace('В этом проекте создан локальный прототип; публикация на хостинге не выполнялась.', 'Этот учебник опубликован через GitHub Pages. Вы можете использовать его структуру для своего проекта.')
    (public / 'index.html').write_text(online, encoding='utf-8')
    (public / '.nojekyll').touch()
    (public / 'README.md').write_text('# Практикум\n\nОткрытый учебник по работе с материалами для Дзена и созданию HTML-сайта. Восемь глав, задания, пример сайта и машинная расшифровка видео. Видео воспроизводится через исходный плеер Kinescope и требует интернета.\n\nДля самостоятельной работы начните с главы 01. JavaScript необязателен.\n', encoding='utf-8')
    print('GitHub Pages files ready in docs/')
