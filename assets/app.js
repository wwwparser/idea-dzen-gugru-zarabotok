'use strict';
const checks = [...document.querySelectorAll('[data-chapter]')];
const key = 'dzen-practicum-v1';
let saved = {};
let storageAvailable = true;
try { saved = JSON.parse(localStorage.getItem(key) || '{}') || {}; }
catch { storageAvailable = false; }
function updateProgress() {
  const count = checks.filter(check => check.checked).length;
  document.querySelector('#progress').value = count;
  document.querySelector('#progress-label').textContent = `${count} / ${checks.length}`;
  if (!storageAvailable) document.querySelector('#storage-note').textContent = 'Сохранение недоступно. Отметки действуют до закрытия страницы.';
}
checks.forEach(check => {
  check.checked = saved[check.dataset.chapter] === true;
  check.addEventListener('change', () => {
    saved[check.dataset.chapter] = check.checked;
    try { localStorage.setItem(key, JSON.stringify(saved)); }
    catch { storageAvailable = false; }
    updateProgress();
  });
});
document.querySelector('#reset').addEventListener('click', () => {
  saved = {};
  checks.forEach(check => { check.checked = false; });
  try { localStorage.removeItem(key); } catch { storageAvailable = false; }
  updateProgress();
});
updateProgress();
const video = document.querySelector('#video');
function seek(seconds) {
  if (video.tagName === 'IFRAME') {
    window.seekOnlineVideo(seconds);
    video.scrollIntoView({block: 'center'});
    return;
  }
  const jump = () => { video.currentTime = Math.min(seconds, Number.isFinite(video.duration) ? video.duration : seconds); };
  if (video.readyState >= 1) jump();
  else { video.addEventListener('loadedmetadata', jump, {once: true}); video.load(); }
  video.scrollIntoView({block: 'center'});
  video.play().catch(() => { document.querySelector('#video-status').textContent = 'Нужный момент выбран. Нажмите воспроизведение в плеере.'; });
}
video.addEventListener('error', () => {
  document.querySelector('#video-status').textContent = 'Видео не загрузилось. Проверьте data/media/lesson.mp4 или откройте источник в главе 08.';
});
document.addEventListener('click', event => {
  const button = event.target.closest('[data-time]');
  if (button) seek(Number(button.dataset.time));
});
function timestamp(seconds) {
  return `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${Math.floor(seconds % 60).toString().padStart(2, '0')}`;
}
function highlightedText(parent, text, query) {
  if (!query) { parent.textContent = text; return; }
  const lower = text.toLocaleLowerCase('ru');
  let offset = 0;
  let found;
  while ((found = lower.indexOf(query, offset)) >= 0) {
    parent.append(document.createTextNode(text.slice(offset, found)));
    const mark = document.createElement('mark');
    mark.textContent = text.slice(found, found + query.length);
    parent.append(mark);
    offset = found + query.length;
  }
  parent.append(document.createTextNode(text.slice(offset)));
}
const segments = Array.isArray(window.TRANSCRIPT) ? window.TRANSCRIPT : [];
function renderTranscript() {
  const query = document.querySelector('#search').value.trim().toLocaleLowerCase('ru');
  const filtered = segments.filter(segment => segment.text.toLocaleLowerCase('ru').includes(query));
  const container = document.querySelector('#segments');
  container.replaceChildren();
  document.querySelector('#search-count').textContent = filtered.length ? `${filtered.length} из ${segments.length} фрагментов` : 'Совпадений нет. Попробуйте другое слово: машинная расшифровка может искажать названия.';
  for (const segment of filtered) {
    const row = document.createElement('div');
    row.className = 'segment';
    const button = document.createElement('button');
    button.type = 'button'; button.dataset.time = String(segment.start);
    button.textContent = timestamp(segment.start);
    button.setAttribute('aria-label', `Смотреть с ${timestamp(segment.start)}`);
    const paragraph = document.createElement('p');
    highlightedText(paragraph, segment.text, query);
    row.append(button, paragraph); container.append(row);
  }
}
document.querySelector('#search').addEventListener('input', renderTranscript);
renderTranscript();
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) if (entry.isIntersecting) {
      document.querySelectorAll('nav a').forEach(link => {
        const active = link.hash === `#${entry.target.id}`;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
      });
    }
  }, {rootMargin: '-15% 0px -65% 0px'});
  document.querySelectorAll('.chapter').forEach(chapter => observer.observe(chapter));
}
