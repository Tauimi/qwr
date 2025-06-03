document.addEventListener('DOMContentLoaded', function() {
    // Функционал для кнопок количества на основной форме
    const decreaseBtn = document.querySelector('.quantity-decrease');
    const increaseBtn = document.querySelector('.quantity-increase');
    const quantityInput = document.querySelector('.product-details input[name="quantity"]');
    
    // Элементы управления количеством в корзине
    const cartControls = document.querySelector('.cart-controls');
    const addToCartBtn = document.querySelector('.add-to-cart-large');
    const cartQuantityControls = document.querySelector('.cart-quantity-controls');
    const cartQuantityValue = document.querySelector('.cart-quantity-value');
    const cartQuantityDecrease = document.querySelector('.cart-quantity-decrease');
    const cartQuantityIncrease = document.querySelector('.cart-quantity-increase');
    
    if (decreaseBtn && increaseBtn && quantityInput) {
        // Получаем ID товара для использования в localStorage
        const productId = quantityInput.closest('form').getAttribute('data-product-id') || 
                          quantityInput.closest('form').querySelector('input[name="product_id"]')?.value ||
                          window.location.pathname.split('/').pop();
        
        // Проверяем, есть ли товар в корзине
        function checkCartItem() {
            fetch(`/cart/check/${productId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.in_cart) {
                        // Показываем элементы управления количеством
                        addToCartBtn.style.display = 'none';
                        cartQuantityControls.style.display = 'flex';
                        cartQuantityValue.textContent = data.quantity;
                    } else {
                        // Показываем кнопку "В корзину"
                        addToCartBtn.style.display = 'block';
                        cartQuantityControls.style.display = 'none';
                    }
                });
        }
        
        // Проверяем состояние корзины при загрузке страницы
        checkCartItem();
        
        // Обработчик для уменьшения количества в корзине
        cartQuantityDecrease.addEventListener('click', function() {
            const currentQuantity = parseInt(cartQuantityValue.textContent);
            if (currentQuantity > 1) {
                updateCartQuantity(productId, currentQuantity - 1);
            } else {
                // Если количество 1, удаляем товар из корзины
                removeFromCart(productId);
            }
        });
        
        // Обработчик для увеличения количества в корзине
        cartQuantityIncrease.addEventListener('click', function() {
            const currentQuantity = parseInt(cartQuantityValue.textContent);
            const maxValue = parseInt(quantityInput.getAttribute('max'));
            if (currentQuantity < maxValue) {
                updateCartQuantity(productId, currentQuantity + 1);
            }
        });
        
        // Функция обновления количества товара в корзине
        function updateCartQuantity(productId, quantity) {
            const formData = new FormData();
            formData.append('quantity', quantity);
            
            fetch(`/cart/update/${productId}`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cartQuantityValue.textContent = quantity;
                    showNotification('Количество товара обновлено', 'success');
                }
            })
            .catch(error => {
                console.error('Ошибка при обновлении количества:', error);
                showNotification('Ошибка при обновлении количества', 'error');
            });
        }
        
        // Функция удаления товара из корзины
        function removeFromCart(productId) {
            fetch(`/cart/remove/${productId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Показываем кнопку "В корзину"
                    addToCartBtn.style.display = 'block';
                    cartQuantityControls.style.display = 'none';
                    showNotification('Товар удален из корзины', 'success');
                }
            })
            .catch(error => {
                console.error('Ошибка при удалении товара:', error);
                showNotification('Ошибка при удалении товара', 'error');
            });
        }
    }
    
    // Обработка всех форм добавления в корзину
    document.querySelectorAll('.ajax-add-to-cart').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const url = form.getAttribute('action');
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Показываем элементы управления количеством
                    addToCartBtn.style.display = 'none';
                    cartQuantityControls.style.display = 'flex';
                    cartQuantityValue.textContent = data.quantity;
                    
                    showNotification(data.message, 'success');
                } else {
                    showNotification(data.message, 'warning');
                }
            })
            .catch(error => {
                console.error('Ошибка при добавлении в корзину:', error);
                showNotification('Произошла ошибка при добавлении товара в корзину', 'error');
            });
        });
    });

    // Функция обновления счетчика корзины
    function updateCartCounter(count) {
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = count;
            
            // Добавляем класс для анимации, если счетчик больше 0
            if (count > 0) {
                cartCountElement.classList.add('has-items');
            } else {
                cartCountElement.classList.remove('has-items');
            }
        }
    }

    // Функция для показа уведомления
    function showNotification(message, type = 'success') {
        // Проверяем, существует ли контейнер для уведомлений
        let notificationContainer = document.getElementById('notification-container');
        
        if (!notificationContainer) {
            // Если контейнер не существует, создаем его
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            document.body.appendChild(notificationContainer);
        }
        
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        // Выбираем иконку в зависимости от типа уведомления
        let icon = 'fa-check-circle';
        if (type === 'warning') icon = 'fa-exclamation-circle';
        if (type === 'error') icon = 'fa-times-circle';
        
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${icon}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Добавляем уведомление в контейнер
        notificationContainer.appendChild(notification);
        
        // Добавляем класс для анимации появления
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Функция для анимации кнопки добавления в корзину
    function animateAddToCartButton(button) {
        if (button) {
            button.classList.add('added');
            setTimeout(() => {
                button.classList.remove('added');
            }, 1000);
        }
    }

    // Обработка избранного
    const favoriteBtn = document.querySelector('.favorite-btn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            toggleFavorite(productId, this);
        });
    }

    // Обработка сравнения
    const compareBtn = document.querySelector('.compare-btn');
    if (compareBtn) {
        compareBtn.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            toggleCompare(productId, this);
        });
    }

    // Функция для работы с избранным
    function toggleFavorite(productId, button) {
        fetch(`/favorites/toggle/${productId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                button.classList.toggle('active');
                const countElement = button.querySelector('.favorite-count');
                countElement.textContent = data.favorites_count;
                
                if (button.classList.contains('active')) {
                    showNotification('Товар добавлен в избранное', 'success');
                } else {
                    showNotification('Товар удален из избранного', 'info');
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при работе с избранным:', error);
            showNotification('Произошла ошибка', 'error');
        });
    }

    // Функция для работы со сравнением
    function toggleCompare(productId, button) {
        fetch(`/compare/toggle/${productId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                button.classList.toggle('active');
                
                if (button.classList.contains('active')) {
                    showNotification('Товар добавлен к сравнению', 'success');
                } else {
                    showNotification('Товар удален из сравнения', 'info');
                }
            } else {
                showNotification(data.message, 'warning');
            }
        })
        .catch(error => {
            console.error('Ошибка при работе со сравнением:', error);
            showNotification('Произошла ошибка', 'error');
        });
    }
}); 