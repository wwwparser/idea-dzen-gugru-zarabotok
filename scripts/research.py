"""Collect only a few searches; save every completed query for resume."""
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.services.xmlriver_client import search

ROOT = Path(__file__).resolve().parents[1]
for line in (ROOT / '.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
queries = ['site:code.claude.com/docs quickstart best practices',
           'site:developer.mozilla.org/ru HTML CSS JavaScript начало',
           'site:dzen.ru монетизация требования авторов справка']
out = ROOT / 'data/research'
out.mkdir(parents=True, exist_ok=True)
for i, query in enumerate(queries):
    results = search(query, out / f'search-{i+1}.xml')
    (out / f'search-{i+1}.json').write_text(json.dumps({'query': query, 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(query, len(results), flush=True)
