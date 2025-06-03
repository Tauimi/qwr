
// Скрипт обработки авторизации
document.addEventListener('DOMContentLoaded', function() {
  // Проверяем, авторизован ли пользователь
  const isLoggedIn = document.body.classList.contains('logged-in');
  
  // Обновляем элементы интерфейса при авторизации
  if (isLoggedIn) {
    console.log('Пользователь авторизован');
    
    // Устанавливаем обработчики для элементов, доступных только авторизованным пользователям
    const userMenuItems = document.querySelectorAll('.user-menu-item');
    userMenuItems.forEach(item => {
      item.addEventListener('click', function(e) {
        // Предотвращаем возможную проблему с блокировкой интерфейса
        e.stopPropagation();
      });
    });
  }
  
  // Обработчик для формы логина
  const loginForm = document.querySelector('#login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
      // Дополнительная валидация перед отправкой формы
      const username = loginForm.querySelector('[name="username"]').value;
      const password = loginForm.querySelector('[name="password"]').value;
      
      if (!username || !password) {
        e.preventDefault();
        alert('Пожалуйста, заполните все поля');
      }
    });
  }
  
  // Исправляем проблему с навигацией - добавляем обработчики для всех ссылок в шапке
  const headerLinks = document.querySelectorAll('header a, nav a');
  headerLinks.forEach(link => {
    // Удаляем все существующие обработчики, чтобы избежать дублирования
    const newLink = link.cloneNode(true);
    link.parentNode.replaceChild(newLink, link);
    
    newLink.addEventListener('click', function(e) {
      // Улучшаем обработку кликов
      if (this.getAttribute('href')) {
        // Предотвращаем отмену события кликов другими обработчиками
        e.stopPropagation();
        console.log('Переход по ссылке:', this.getAttribute('href'));
      }
    });
  });
  
  // Убеждаемся, что все клики в шапке обрабатываются корректно
  document.querySelector('header').addEventListener('click', function(e) {
    // Потенциально интерактивный элемент, но клик был не на ссылке
    if (!e.target.closest('a') && !e.target.closest('button')) {
      e.stopPropagation();
    }
  }, true);
});
