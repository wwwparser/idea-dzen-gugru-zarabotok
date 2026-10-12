"""Small, resumable XMLRiver client. Credentials never enter logs."""
import os
import time
import xml.etree.ElementTree as ET
from pathlib import Path
import requests


def search(query, cache):
    cache = Path(cache)
    if cache.exists():
        raw = cache.read_text(encoding='utf-8')
    else:
        user, key = os.getenv('XMLRIVER_USER'), os.getenv('XMLRIVER_KEY')
        if not user or not key:
            raise RuntimeError('Set XMLRIVER_USER and XMLRIVER_KEY in .env')
        for attempt in range(3):
            try:
                response = requests.get('https://xmlriver.com/search/xml', params={
                    'user': user, 'key': key, 'query': query, 'country': '2643',
                    'lr': 'ru', 'page': 1, 'groupby': 10}, timeout=75)
                response.raise_for_status()
            except requests.RequestException:
                if attempt == 2:
                    raise RuntimeError('XMLRiver network request failed') from None
                time.sleep(4)
                continue
            try:
                raw = response.content.decode('utf-8')
            except UnicodeDecodeError:
                raw = response.content.decode('cp1251')
            root = ET.fromstring(raw)
            error = root.find('.//error')
            if error is None:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(raw, encoding='utf-8')
                break
            message = ''.join(error.itertext())
            if any(s in message.lower() for s in ['баланс', 'превышено', 'средств']):
                raise RuntimeError(message)
            if attempt == 2:
                raise RuntimeError(message)
            time.sleep(15 if 'канал' in message else 4)
    root = ET.fromstring(raw)
    return [{'url': doc.findtext('url'), 'title': ''.join(doc.find('title').itertext()) if doc.find('title') is not None else '',
             'snippet': ' '.join(''.join(p.itertext()) for p in doc.findall('.//passage'))}
            for doc in root.findall('.//doc')]
