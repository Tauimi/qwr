document.addEventListener('DOMContentLoaded', function() {
    // Обновление стоимости доставки при изменении способа доставки
    const deliveryMethods = document.querySelectorAll('input[name="delivery_method"]');
    
    deliveryMethods.forEach(method => {
        method.addEventListener('change', updateDeliveryAndTotal);
    });
    
    function updateDeliveryAndTotal() {
        const deliveryMethod = document.querySelector('input[name="delivery_method"]:checked').value;
        const totalProductsPrice = parseFloat(document.getElementById('products-total').dataset.total);
        
        let deliveryCost = 0;
        let deliveryText = '';
        
        if (deliveryMethod === 'courier') {
            if (totalProductsPrice >= 5000) {
                deliveryText = '0 ₽ (бесплатно)';
            } else {
                deliveryCost = 500;
                deliveryText = '500 ₽';
            }
        } else if (deliveryMethod === 'pickup') {
            deliveryText = '0 ₽ (бесплатно)';
        }
        
        // Обновляем отображение стоимости доставки
        document.getElementById('delivery-cost').textContent = deliveryText;
        
        // Обновляем итоговую сумму
        const grandTotal = totalProductsPrice + deliveryCost;
        document.getElementById('grand-total').textContent = grandTotal.toFixed(2) + ' ₽';
    }
    
    // Валидация формы оформления заказа
    const checkoutForm = document.getElementById('checkout-form');
    
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(event) {
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const city = document.getElementById('city').value.trim();
            const address = document.getElementById('address').value.trim();
            const postalCode = document.getElementById('postal_code').value.trim();
            
            let isValid = true;
            let errorMessage = '';
            
            // Проверка имени
            if (name.length < 3) {
                isValid = false;
                errorMessage += 'Пожалуйста, введите корректное имя (минимум 3 символа).\n';
            }
            
            // Проверка email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                isValid = false;
                errorMessage += 'Пожалуйста, введите корректный email адрес.\n';
            }
            
            // Проверка телефона
            const phoneRegex = /^(\+7|8)[0-9]{10}$/;
            if (!phoneRegex.test(phone)) {
                isValid = false;
                errorMessage += 'Пожалуйста, введите корректный номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX.\n';
            }
            
            // Проверка города
            if (city.length < 2) {
                isValid = false;
                errorMessage += 'Пожалуйста, введите корректное название города.\n';
            }
            
            // Проверка адреса
            if (address.length < 5) {
                isValid = false;
                errorMessage += 'Пожалуйста, введите корректный адрес (минимум 5 символов).\n';
            }
            
            // Проверка почтового индекса
            const postalCodeRegex = /^[0-9]{6}$/;
            if (!postalCodeRegex.test(postalCode)) {
                isValid = false;
                errorMessage += 'Пожалуйста, введите корректный почтовый индекс (6 цифр).\n';
            }
            
            if (!isValid) {
                event.preventDefault();
                alert(errorMessage);
            }
        });
    }
}); 