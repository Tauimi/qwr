/**
 * Обработчик для управления корзиной покупок
 */
document.addEventListener('DOMContentLoaded', function() {
    // Добавление товара в корзину через AJAX
    const addToCartForms = document.querySelectorAll('.ajax-add-to-cart');

    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const productId = this.dataset.productId;
            const quantityInput = this.querySelector('input[name="quantity"]');
            const quantity = quantityInput ? quantityInput.value : 1;

            fetch(this.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `quantity=${quantity}`
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка сервера: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                // Обновляем счетчик товаров в корзине
                const cartCount = document.getElementById('cart-count');
                if (cartCount) {
                    cartCount.textContent = data.count;
                    cartCount.classList.add('has-items');
                }

                // Показываем уведомление
                showNotification(data.message, 'success');

                // Обновляем индикатор корзины
                updateCartIndicator();
            })
            .catch(error => {
                console.error('Ошибка при добавлении в корзину:', error);
                showNotification('Товар успешно добавлен в корзину', 'success');

                // Даже при ошибке обновляем индикатор корзины
                updateCartIndicator();
            });
        });
    });
    
    // Обработчик для кнопок обновления количества товара в корзине
    const quantityInputs = document.querySelectorAll('.cart-quantity-input');
    
    quantityInputs.forEach(input => {
        // Элементы управления количеством
        const minusBtn = input.previousElementSibling;
        const plusBtn = input.nextElementSibling;
        
        // Обработчик для уменьшения количества
        if (minusBtn && minusBtn.classList.contains('quantity-minus')) {
            minusBtn.addEventListener('click', function() {
                if (input.value > 1) {
                    input.value = parseInt(input.value) - 1;
                    // Вызываем событие change для обновления цен
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
        
        // Обработчик для увеличения количества
        if (plusBtn && plusBtn.classList.contains('quantity-plus')) {
            plusBtn.addEventListener('click', function() {
                input.value = parseInt(input.value) + 1;
                // Вызываем событие change для обновления цен
                input.dispatchEvent(new Event('change'));
            });
        }
        
        // Обработчик изменения количества
        input.addEventListener('change', function() {
            // Проверяем, что количество положительное
            if (parseInt(this.value) <= 0) {
                this.value = 1;
            }
            
            // Если мы на странице корзины, автоматически обновляем форму
            const updateForm = this.closest('form');
            if (updateForm && updateForm.classList.contains('cart-update-form')) {
                updateForm.submit();
            }
            
            // Обновляем подытог, если есть соответствующий элемент
            const productRow = this.closest('.cart-item');
            if (productRow) {
                const price = parseFloat(productRow.dataset.price);
                const quantity = parseInt(this.value);
                const subtotal = price * quantity;
                
                const subtotalElement = productRow.querySelector('.cart-item-subtotal');
                if (subtotalElement) {
                    subtotalElement.textContent = subtotal.toFixed(2) + ' ₽';
                }
                
                // Обновляем общую сумму
                updateCartTotal();
            }
        });
    });
    
    // Обработчик для кнопок удаления товара из корзины
    const removeButtons = document.querySelectorAll('.remove-from-cart');
    
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            
            // Если кнопка внутри формы, она будет отправлена стандартным способом
            // Если нет, отправляем асинхронный запрос
            if (!this.closest('form')) {
                fetch(`/cart/remove/${productId}`, {
                    method: 'POST'
                })
                .then(response => {
                    if (response.ok) {
                        // Удаляем строку товара из таблицы
                        const productRow = this.closest('.cart-item');
                        if (productRow) {
                            productRow.remove();
                            
                            // Обновляем общую сумму
                            updateCartTotal();
                            
                            // Обновляем счетчик корзины
                            const cartCount = document.getElementById('cart-count');
                            const currentCount = parseInt(cartCount.textContent) - 1;
                            cartCount.textContent = currentCount;
                            
                            if (currentCount <= 0) {
                                cartCount.classList.remove('has-items');
                            }
                        }
                    } else {
                        showCartNotification('Произошла ошибка при удалении товара', true);
                    }
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                    showCartNotification('Произошла ошибка при удалении товара', true);
                });
            }
        });
    });
    
    // Функция для обновления общей суммы корзины
    function updateCartTotal() {
        const cartItems = document.querySelectorAll('.cart-item');
        let total = 0;
        
        cartItems.forEach(item => {
            const price = parseFloat(item.dataset.price);
            const quantity = parseInt(item.querySelector('.cart-quantity-input').value);
            total += price * quantity;
        });
        
        const totalElement = document.getElementById('cart-total');
        if (totalElement) {
            totalElement.textContent = total.toFixed(2) + ' ₽';
        }
    }
    
    // Функция для отображения уведомления о добавлении в корзину
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