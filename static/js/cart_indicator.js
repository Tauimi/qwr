/**
 * Файл для работы с индикатором корзины
 */
document.addEventListener('DOMContentLoaded', function() {
    // Функция обновления счетчика корзины
    function updateCartCounter() {
        fetch('/cart/count', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        })
            .then(response => {
                // Проверяем, что ответ - успешный и содержит JSON
                if (!response.ok) {
                    throw new Error('Ошибка сервера: ' + response.status);
                }

                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Получен не JSON ответ');
                }

                return response.json();
            })
            .then(data => {
                const cartCountElement = document.getElementById('cart-count');
                if (cartCountElement) {
                    cartCountElement.textContent = data.count;

                    // Добавляем класс для анимации, если счетчик больше 0
                    if (data.count > 0) {
                        cartCountElement.classList.add('has-items');
                    } else {
                        cartCountElement.classList.remove('has-items');
                    }
                }
            })
            .catch(error => console.error('Ошибка при получении данных корзины:', error));
    }

    // Обновляем счетчик при загрузке страницы
    updateCartCounter();

    // Обработчик для форм добавления в корзину
    document.addEventListener('submit', function(e) {
        const form = e.target;

        // Проверяем, что это форма добавления в корзину
        if (form.classList.contains('ajax-cart-form') || form.classList.contains('ajax-add-to-cart')) {
            e.preventDefault();

            const productId = form.dataset.productId;
            const formData = new FormData(form);

            // Блокируем кнопку на время запроса
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.textContent;
                submitButton.textContent = 'Добавляем...';
                submitButton.disabled = true;

                // Восстановление кнопки через 2 секунды
                setTimeout(() => {
                    submitButton.textContent = originalText;
                    submitButton.disabled = false;
                }, 2000);
            }

            // Отправка запроса
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                // Проверяем, что ответ - успешный
                if (!response.ok) {
                    throw new Error('Ошибка сервера: ' + response.status);
                }

                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Получен не JSON ответ');
                }

                return response.json();
            })
            .then(data => {
                // Обновляем счетчик товаров в корзине
                updateCartCounter();

                // Показываем уведомление об успешном добавлении
                showCartNotification(data.message || 'Товар добавлен в корзину');
            })
            .catch(error => {
                console.error('Ошибка при добавлении в корзину:', error);

                // Показываем уведомление об ошибке
                showCartNotification('Произошла ошибка при добавлении товара', true);
            });
        }
    });

    // Функция для отображения уведомления о корзине
    function showCartNotification(message, isError = false) {
        // Создаем уведомление, если его нет
        let notification = document.getElementById('cart-notification');

        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'cart-notification';
            document.body.appendChild(notification);
        }

        // Добавляем класс ошибки, если это ошибка
        notification.className = isError ? 'error' : 'success';
        notification.textContent = message;

        // Показываем уведомление
        notification.classList.add('show');

        // Скрываем уведомление через 3 секунды
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
});
/**
 * Файл для работы с индикатором корзины
 */
document.addEventListener('DOMContentLoaded', function() {
    updateCartIndicator();
});

/**
 * Обновляет индикатор корзины
 */
function updateCartIndicator() {
    fetch('/cart/count', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        // Проверяем, что ответ - успешный и содержит JSON
        if (!response.ok) {
            throw new Error('Ошибка сервера: ' + response.status);
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Получен не JSON ответ');
        }

        return response.json();
    })
    .then(data => {
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = data.count;

            if (data.count > 0) {
                cartCount.classList.add('has-items');
            } else {
                cartCount.classList.remove('has-items');
            }
        }
    })
    .catch(error => {
        console.error('Ошибка при получении данных корзины:', error);
    });
}