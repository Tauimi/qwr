/**
 * Скрипт для обновления счетчика посетителей
 */
document.addEventListener('DOMContentLoaded', function() {
    // Находим элемент счетчика посетителей
    const visitorCounter = document.getElementById('visitor-count');
    
    // Если элемент найден, обновляем его
    if (visitorCounter) {
        // Получаем текущее значение из атрибута data-count или из шаблона
        let currentValue = parseInt(visitorCounter.dataset.count || visitorCounter.textContent) || 0;
        
        // Обновляем счетчик с сервера
        updateVisitorCount();
        
        // Периодически обновляем счетчик (каждые 5 минут)
        setInterval(updateVisitorCount, 5 * 60 * 1000);
        
        // Функция для обновления счетчика
        function updateVisitorCount() {
            fetch('/api/visitors/count')
                .then(response => response.json())
                .then(data => {
                    // Проверяем, изменилось ли значение
                    if (data.count > currentValue) {
                        // Анимируем изменение счетчика
                        animateCounter(currentValue, data.count);
                        currentValue = data.count;
                    }
                })
                .catch(error => console.error('Ошибка при получении данных о посетителях:', error));
        }
        
        // Функция для анимации счетчика
        function animateCounter(start, end) {
            // Если счетчик первый раз загружается, просто устанавливаем значение
            if (start === 0 && parseInt(visitorCounter.textContent) === 0) {
                visitorCounter.textContent = end;
                visitorCounter.classList.add('updated');
                setTimeout(() => visitorCounter.classList.remove('updated'), 1000);
                return;
            }
            
            // Прирост за один шаг
            const step = 1;
            // Время между обновлениями (в мс)
            const interval = 100;
            // Текущее значение
            let current = start;
            
            // Анимация счетчика
            const timer = setInterval(() => {
                current += step;
                visitorCounter.textContent = current;
                visitorCounter.classList.add('updated');
                
                if (current >= end) {
                    clearInterval(timer);
                    visitorCounter.textContent = end;
                    setTimeout(() => visitorCounter.classList.remove('updated'), 1000);
                }
            }, interval);
        }
    }
}); 