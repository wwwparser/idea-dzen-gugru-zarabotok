const button = document.querySelector('#complete');
const result = document.querySelector('#result');
button.addEventListener('click', () => {
  const complete = button.getAttribute('aria-pressed') !== 'true';
  button.setAttribute('aria-pressed', String(complete));
  button.textContent = complete ? 'Вернуть задание в работу' : 'Отметить задание выполненным';
  result.textContent = complete ? 'Готово! Теперь проверьте страницу на телефоне и с клавиатуры.' : 'Задание снова в работе.';
});
