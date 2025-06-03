// Скрипт для автоматического скрытия flash-сообщений
document.addEventListener('DOMContentLoaded', function() {
    // Находим все flash-сообщения на странице
    const flashMessages = document.querySelectorAll('.alert');
    
    // Устанавливаем таймер для каждого сообщения
    flashMessages.forEach(function(message) {
        // Добавляем кнопку закрытия к каждому сообщению
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'alert-close';
        closeButton.setAttribute('aria-label', 'Закрыть');
        closeButton.addEventListener('click', function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.style.display = 'none';
            }, 300);
        });
        message.appendChild(closeButton);
        
        // Автоматически скрываем сообщение через 5 секунд
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });
}); 