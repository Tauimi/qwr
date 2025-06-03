document.addEventListener('DOMContentLoaded', function() {
    // Калькулятор доставки
    const calculateBtn = document.getElementById('calculate-delivery');
    
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function() {
            const city = document.getElementById('delivery-city').value;
            const weight = parseFloat(document.getElementById('delivery-weight').value);
            const orderSum = parseFloat(document.getElementById('delivery-sum').value);
            
            let cost = 0;
            let time = '';
            
            // Расчет стоимости доставки
            if (orderSum >= 5000 && (city === 'moscow' || city === 'spb')) {
                cost = 0; // Бесплатная доставка при заказе от 5000₽
            } else {
                switch (city) {
                    case 'moscow':
                        cost = 300;
                        time = '1-2 дня';
                        break;
                    case 'spb':
                        cost = 300;
                        time = '1-2 дня';
                        break;
                    case 'moscow-region':
                        cost = 500;
                        time = '1-3 дня';
                        break;
                    case 'other':
                        cost = 500 + (weight * 100); // Базовая стоимость + доплата за вес
                        time = '2-7 дней';
                        break;
                }
            }
            
            // Вывод результата
            document.querySelector('#delivery-cost span').textContent = cost + ' ₽';
            document.querySelector('#delivery-time span').textContent = time;
            
            // Показать результат
            document.querySelector('.delivery-result').style.display = 'block';
        });
    }
}); 