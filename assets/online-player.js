'use strict';
let onlinePlayer;
let pendingSeek;
const onlineStatus = () => document.querySelector('#video-status');
async function playAt(seconds) {
  try {
    await onlinePlayer.seekTo(seconds);
    await onlinePlayer.play();
    onlineStatus().textContent = '';
  } catch {
    onlineStatus().textContent = 'Нужный момент выбран. Нажмите воспроизведение в плеере.';
  }
}
window.seekOnlineVideo = seconds => {
  pendingSeek = seconds;
  if (onlinePlayer) playAt(seconds);
  else onlineStatus().textContent = 'Плеер загружается. Если он не появился, откройте оригинальное видео по ссылке ниже.';
};
window.onKinescopeIframeAPIReady = factory => {
  factory.create('video', {
    url: 'https://kinescope.io/eHTc1UJ83wrTzEZL2kxKWz',
    size: {width: '100%', height: '100%'}
  }).then(player => {
    onlinePlayer = player;
    if (pendingSeek !== undefined) playAt(pendingSeek);
  }).catch(() => {
    onlineStatus().textContent = 'Управление таймкодами недоступно. Можно посмотреть запись в плеере или открыть оригинальное видео.';
  });
};
const sdk = document.createElement('script');
sdk.src = 'https://player.kinescope.io/latest/iframe.player.js';
sdk.async = true;
document.head.append(sdk);
