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

            const requestUrl = `/cart/add/${productId}`;
            console.log('[cart_handler.js] Add to cart request URL:', requestUrl); // DEBUG

            fetch(requestUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `quantity=${quantity}`
            })
            .then(response => {
                console.log('[cart_handler.js] Add to cart response status:', response.status); // DEBUG
                if (!response.ok) {
                    // Попытаемся извлечь JSON с ошибкой, если он есть
                    return response.json().then(errData => {
                        console.error('[cart_handler.js] Server error JSON:', errData); // DEBUG
                        throw new Error(errData.message || `Ошибка сервера: ${response.status}`);
                    }).catch(() => {
                        // Если JSON нет, или он не парсится, выбрасываем общую ошибку
                        throw new Error(`Ошибка сервера: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('[cart_handler.js] Add to cart AJAX success. Data:', data); // DEBUG
                if (data.message && data.count !== undefined) {
                    if (typeof showNotification === 'function') {
                        console.log('[cart_handler.js] Calling showNotification with type success. Message:', data.message); // DEBUG
                        showNotification(data.message, 'success');
                    }
                    const cartCount = document.getElementById('cart-count');
                    if (cartCount) {
                        cartCount.textContent = data.count;
                        cartCount.classList.add('has-items');
                    }
                } else {
                    console.error('[cart_handler.js] Add to cart AJAX success but data is not as expected:', data); // DEBUG
                    if (typeof showNotification === 'function') {
                        showNotification('Ответ от сервера не содержит ожидаемых данных.', 'error');
                    }
                }
                updateCartIndicator();
            })
            .catch(error => {
                console.error('[cart_handler.js] Add to cart AJAX error:', error.message); // DEBUG
                if (typeof showNotification === 'function') {
                    console.log('[cart_handler.js] Calling showNotification for error. Message:', error.message); // DEBUG
                    showNotification(`Ошибка: ${error.message}`, 'error');
                }
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
            console.log('[cart_handler.js] Remove from cart. ProductId:', productId); // DEBUG
            
            if (!this.closest('form')) {
                fetch(`/cart/remove/${productId}`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    console.log('[cart_handler.js] Remove from cart response status:', response.status); // DEBUG
                    if (!response.ok) {
                         return response.json().then(errData => {
                            console.error('[cart_handler.js] Server error JSON on remove:', errData); // DEBUG
                            throw new Error(errData.message || `Ошибка сервера: ${response.status}`);
                        }).catch(() => {
                            throw new Error(`Ошибка сервера: ${response.status}`);
                        });
                    }
                    // Предполагаем, что успешное удаление возвращает JSON с новым количеством или подтверждением
                    return response.json(); 
                })
                .then(data => {
                    console.log('[cart_handler.js] Remove from cart AJAX success. Data:', data); // DEBUG
                    if (data.success) { // Или другой флаг успеха от вашего API
                        const productRow = this.closest('.cart-item');
                        if (productRow) productRow.remove();
                        updateCartTotal();
                        
                        const cartCountEl = document.getElementById('cart-count');
                        if (cartCountEl && data.count !== undefined) {
                            cartCountEl.textContent = data.count;
                            if (data.count <= 0) cartCountEl.classList.remove('has-items');
                        }
                        if (typeof showNotification === 'function') {
                           console.log('[cart_handler.js] Calling showNotification for remove success. Message:', data.message || 'Товар удален'); // DEBUG
                           showNotification(data.message || 'Товар удален из корзины', 'success');
                        }
                    } else {
                        console.error('[cart_handler.js] Remove from cart success but server indicated failure:', data); // DEBUG
                        if (typeof showNotification === 'function') {
                            showNotification(data.message || 'Не удалось удалить товар.', 'error');
                        }
                    }
                })
                .catch(error => {
                    console.error('[cart_handler.js] Remove from cart AJAX error:', error.message); // DEBUG
                    if (typeof showNotification === 'function') {
                        console.log('[cart_handler.js] Calling showNotification for remove error. Message:', error.message); // DEBUG
                        showNotification(`Ошибка при удалении: ${error.message}`, 'error');
                    }
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
});