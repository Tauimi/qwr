document.addEventListener('DOMContentLoaded', function() {
    // Функционал калькулятора корзины будет использоваться из main.js
    
    // Обновление количества товаров в корзине
    const quantityInputs = document.querySelectorAll('.cart-quantity input');
    const decreaseButtons = document.querySelectorAll('.quantity-decrease');
    const increaseButtons = document.querySelectorAll('.quantity-increase');
    
    // Обработчик для поля ввода
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.getAttribute('data-product-id') || 
                             this.closest('tr').querySelector('a').getAttribute('href').split('/').pop();
            
            // Очищаем сохраненное в localStorage количество товара, так как товар уже в корзине
            if (productId) {
                localStorage.removeItem('product_quantity_' + productId);
            }
            
            updateCartItemOnServer(productId, this.value);
            updateCartItemSubtotal(this);
        });
    });
    
    // Обработчики для кнопок уменьшения/увеличения
    decreaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const currentValue = parseInt(input.value);
            if (currentValue > 1) {
                input.value = currentValue - 1;
                const productId = input.getAttribute('data-product-id') || 
                                 this.closest('tr').querySelector('a').getAttribute('href').split('/').pop();
                
                // Очищаем сохраненное в localStorage количество товара
                if (productId) {
                    localStorage.removeItem('product_quantity_' + productId);
                }
                
                updateCartItemOnServer(productId, input.value);
                updateCartItemSubtotal(input);
            }
        });
    });
    
    increaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const currentValue = parseInt(input.value);
            const maxValue = parseInt(input.getAttribute('max'));
            
            // Исправляем условие, чтобы можно было выбрать максимальное значение
            if (currentValue < maxValue) {
                input.value = currentValue + 1;  // Явно увеличиваем на 1
                const productId = input.getAttribute('data-product-id') || 
                                 this.closest('tr').querySelector('a').getAttribute('href').split('/').pop();
                
                // Очищаем сохраненное в localStorage количество товара
                if (productId) {
                    localStorage.removeItem('product_quantity_' + productId);
                }
                
                updateCartItemOnServer(productId, input.value);
                updateCartItemSubtotal(input);
            }
        });
    });
    
    // Функция для отправки обновленного количества на сервер
    function updateCartItemOnServer(productId, quantity) {
        const formData = new FormData();
        formData.append('quantity', quantity);
        
        fetch(`/cart/update/${productId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                console.error('Ошибка при обновлении корзины');
            }
        })
        .catch(error => {
            console.error('Ошибка при отправке запроса:', error);
        });
    }
    
    // Функция для обновления промежуточной суммы
    function updateCartItemSubtotal(input) {
        const row = input.closest('tr');
        const price = parseFloat(row.querySelector('.item-price').getAttribute('data-price'));
        const quantity = parseInt(input.value);
        const subtotal = price * quantity;
        
        const subtotalCell = row.querySelector('.item-subtotal');
        subtotalCell.textContent = subtotal.toFixed(2) + ' ₽';
        subtotalCell.setAttribute('data-subtotal', subtotal.toFixed(2));
        
        // Обновляем общую сумму корзины
        updateCartTotal();
    }
    
    // Функция для обновления общей суммы корзины
    function updateCartTotal() {
        const subtotals = document.querySelectorAll('.item-subtotal');
        let total = 0;
        
        subtotals.forEach(subtotal => {
            total += parseFloat(subtotal.getAttribute('data-subtotal'));
        });
        
        const totalElement = document.querySelector('.cart-total-value');
        if (totalElement) {
            totalElement.textContent = total.toFixed(2) + ' ₽';
        }
    }
}); 