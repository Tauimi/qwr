
// Функция для инициализации карусели баннеров
function initBannersCarousel() {
    const slides = document.querySelectorAll('.banner-slide');
    const indicators = document.querySelectorAll('.carousel-indicator');
    const prevBtn = document.querySelector('.carousel-arrow.prev');
    const nextBtn = document.querySelector('.carousel-arrow.next');
    
    if (!slides.length) return;
    
    let currentSlide = 0;
    const slideCount = slides.length;
    
    // Функция для показа слайда
    function showSlide(index) {
        // Скрываем все слайды и индикаторы
        slides.forEach(slide => slide.classList.remove('active'));
        indicators.forEach(dot => dot.classList.remove('active'));
        
        // Показываем нужный слайд и индикатор
        slides[index].classList.add('active');
        if (indicators[index]) {
            indicators[index].classList.add('active');
        }
    }
    
    // Следующий слайд
    function nextSlide() {
        currentSlide = (currentSlide + 1) % slideCount;
        showSlide(currentSlide);
    }
    
    // Предыдущий слайд
    function prevSlide() {
        currentSlide = (currentSlide - 1 + slideCount) % slideCount;
        showSlide(currentSlide);
    }
    
    // Назначаем обработчики событий
    if (prevBtn) prevBtn.addEventListener('click', prevSlide);
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);
    
    // Привязываем индикаторы
    indicators.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentSlide = index;
            showSlide(currentSlide);
        });
    });
    
    // Автоматическая смена слайдов
    setInterval(nextSlide, 5000);
    
    // Показываем первый слайд
    showSlide(0);
}

// Функция для анимации появления карточек товаров
function animateProducts() {
    const products = document.querySelectorAll('.product-card');
    
    if (!products.length) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    products.forEach(product => {
        product.style.opacity = '0';
        product.style.transform = 'translateY(20px)';
        product.style.transition = 'all 0.4s ease';
        observer.observe(product);
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initBannersCarousel();
    animateProducts();
    
    // Фиксация z-index в шапке для лучшей кликабельности
    const headerLinks = document.querySelectorAll('header a, nav a, .header-icon');
    headerLinks.forEach(link => {
        link.style.zIndex = '20';
        link.style.position = 'relative';
    });
});

// Основной JavaScript файл

document.addEventListener('DOMContentLoaded', function() {
    console.log('Сайт загружен и готов к работе!');
    
    // Пример простой анимации для заголовка
    const heading = document.querySelector('h1');
    if (heading) {
        heading.style.opacity = '0';
        heading.style.transform = 'translateY(20px)';
        heading.style.transition = 'opacity 0.5s, transform 0.5s';
        
        setTimeout(() => {
            heading.style.opacity = '1';
            heading.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Инициализация часов
    initClock();
    
    // Инициализация счетчика посещений
    initVisitorCounter();
    
    // Функционал специальных возможностей
    initAccessibilityFeatures();
    
    // Инициализация количества товаров в корзине
    updateCartItemCount();
    
    // Инициализация элементов управления количеством товара
    initQuantityControls();
    
    // Инициализация калькулятора корзины, если находимся на странице корзины
    if (document.querySelector('.cart-table')) {
        initCartCalculator();
    }
    
    // Инициализация предварительного просмотра изображений
    initImagePreviews();
});

// Функция для инициализации часов
function initClock() {
    const clockElement = document.getElementById('clock');
    if (!clockElement) return;
    
    function updateClock() {
        const now = new Date();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        let seconds = now.getSeconds();
        
        // Добавляем ведущий ноль, если значение меньше 10
        hours = hours < 10 ? '0' + hours : hours;
        minutes = minutes < 10 ? '0' + minutes : minutes;
        seconds = seconds < 10 ? '0' + seconds : seconds;
        
        const timeString = `${hours}:${minutes}:${seconds}`;
        clockElement.textContent = timeString;
    }
    
    // Обновляем время каждую секунду
    updateClock();
    setInterval(updateClock, 1000);
}

// Функция для инициализации счетчика посещений
function initVisitorCounter() {
    const counterElement = document.getElementById('visitor-count');
    if (!counterElement) return;
    
    // Получаем количество посещений с сервера
    fetch('/get_visitors_count')
        .then(response => response.json())
        .then(data => {
            counterElement.textContent = data.count;
        })
        .catch(error => console.error('Ошибка при получении счетчика посещений:', error));
}

// Функции для специальных возможностей
function initAccessibilityFeatures() {
    // Эта функция теперь пустая, так как вся функциональность управления доступностью
    // перенесена в отдельный файл accessibility.js, который подключается в layout.html
    
    // Если нужно, можно добавить дополнительные функции доступности, не связанные с основными настройками
    console.log('Инициализация дополнительных функций доступности из main.js');
    
    // Пример добавления функциональности: увеличение отдельных изображений при наведении
    const productImages = document.querySelectorAll('.product-image img');
    productImages.forEach(img => {
        img.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease';
            this.style.transform = 'scale(1.05)';
        });
        
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Функция для обновления счетчика товаров в корзине
function updateCartItemCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (!cartCountElement) return;
    
    // Получаем данные корзины из localStorage или используем пустой массив
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    // Подсчитываем общее количество товаров в корзине
    const itemCount = cart.reduce((total, item) => total + item.quantity, 0);
    
    // Обновляем отображение
    cartCountElement.textContent = itemCount;
    
    // Скрываем счетчик, если корзина пуста
    if (itemCount === 0) {
        cartCountElement.style.display = 'none';
    } else {
        cartCountElement.style.display = 'flex';
    }
}

// Функция для инициализации элементов управления количеством товара
function initQuantityControls() {
    const decreaseButtons = document.querySelectorAll('.quantity-decrease');
    const increaseButtons = document.querySelectorAll('.quantity-increase');
    
    decreaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const currentValue = parseInt(input.value);
            if (currentValue > 1) {
                input.value = currentValue - 1;
                
                // Если мы на странице корзины, обновляем итоговую сумму и отправляем данные на сервер
                if (document.querySelector('.cart-table')) {
                    updateCartItemSubtotal(input);
                    
                    // Если есть функция обновления корзины на сервере, вызываем её
                    if (typeof updateCartItemOnServer === 'function') {
                        const productId = input.getAttribute('data-product-id') || 
                                        input.closest('tr').querySelector('a')?.getAttribute('href')?.split('/').pop();
                        if (productId) {
                            updateCartItemOnServer(productId, input.value);
                        }
                    }
                }
            }
        });
    });
    
    increaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const currentValue = parseInt(input.value);
            // Добавляем проверку на максимальное значение
            const maxValue = parseInt(input.getAttribute('max') || Number.MAX_SAFE_INTEGER);
            
            if (currentValue < maxValue) {
                input.value = currentValue + 1;
                
                // Если мы на странице корзины, обновляем итоговую сумму и отправляем данные на сервер
                if (document.querySelector('.cart-table')) {
                    updateCartItemSubtotal(input);
                    
                    // Если есть функция обновления корзины на сервере, вызываем её
                    if (typeof updateCartItemOnServer === 'function') {
                        const productId = input.getAttribute('data-product-id') || 
                                        input.closest('tr').querySelector('a')?.getAttribute('href')?.split('/').pop();
                        if (productId) {
                            updateCartItemOnServer(productId, input.value);
                        }
                    }
                }
            }
        });
    });
}

// Функция для инициализации калькулятора корзины
function initCartCalculator() {
    const quantityInputs = document.querySelectorAll('.cart-quantity input');
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Проверяем и корректируем введенное значение
            let currentValue = parseInt(this.value);
            let maxValue = parseInt(this.getAttribute('max') || Number.MAX_SAFE_INTEGER);
            
            if (isNaN(currentValue) || currentValue < 1) {
                this.value = 1;
            } else if (currentValue > maxValue) {
                this.value = maxValue;
            }
            
            updateCartItemSubtotal(this);
            
            // Если есть функция обновления корзины на сервере, вызываем её
            if (typeof updateCartItemOnServer === 'function') {
                const productId = this.getAttribute('data-product-id') || 
                                this.closest('tr').querySelector('a')?.getAttribute('href')?.split('/').pop();
                if (productId) {
                    updateCartItemOnServer(productId, this.value);
                }
            }
        });
    });
    
    // Начальный расчет
    calculateCartTotal();
}

// Функция для обновления промежуточной суммы товара в корзине
function updateCartItemSubtotal(input) {
    const row = input.closest('tr');
    const priceElement = row.querySelector('.item-price');
    const subtotalElement = row.querySelector('.item-subtotal');
    
    if (!priceElement || !subtotalElement) return;
    
    const price = parseFloat(priceElement.dataset.price);
    const quantity = parseInt(input.value);
    
    const subtotal = price * quantity;
    subtotalElement.textContent = subtotal.toFixed(2) + ' ₽';
    subtotalElement.dataset.subtotal = subtotal;
    
    // Пересчитываем общую сумму корзины
    calculateCartTotal();
}

// Функция для расчета общей суммы корзины
function calculateCartTotal() {
    const subtotalElements = document.querySelectorAll('.item-subtotal');
    const totalElement = document.getElementById('cart-total-value');
    
    if (!totalElement) return;
    
    let total = 0;
    
    subtotalElements.forEach(element => {
        total += parseFloat(element.dataset.subtotal);
    });
    
    totalElement.textContent = total.toFixed(2) + ' ₽';
}

// Функция для инициализации предварительного просмотра изображений
function initImagePreviews() {
    const thumbnails = document.querySelectorAll('.thumbnail');
    
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            const fullImageSrc = this.dataset.fullImage;
            const fullImageAlt = this.alt;
            
            // Создаем модальное окно для просмотра полного изображения
            const modal = document.createElement('div');
            modal.classList.add('image-modal');
            
            const modalContent = document.createElement('div');
            modalContent.classList.add('image-modal-content');
            
            const image = document.createElement('img');
            image.src = fullImageSrc;
            image.alt = fullImageAlt;
            
            const closeButton = document.createElement('span');
            closeButton.classList.add('modal-close');
            closeButton.innerHTML = '&times;';
            closeButton.addEventListener('click', function() {
                document.body.removeChild(modal);
            });
            
            modalContent.appendChild(image);
            modalContent.appendChild(closeButton);
            modal.appendChild(modalContent);
            
            // Закрытие модального окна при клике вне изображения
            modal.addEventListener('click', function(event) {
                if (event.target === modal) {
                    document.body.removeChild(modal);
                }
            });
            
            document.body.appendChild(modal);
        });
    });
}

// Функция для добавления товара в корзину
function addToCart(productId, productName, productPrice, quantity = 1) {
    // Получаем текущую корзину из localStorage или создаем новую
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    // Проверяем, есть ли уже этот товар в корзине
    const existingItemIndex = cart.findIndex(item => item.productId === productId);
    
    if (existingItemIndex !== -1) {
        // Если товар уже есть, увеличиваем количество
        cart[existingItemIndex].quantity += quantity;
    } else {
        // Если товара еще нет, добавляем его
        cart.push({
            productId: productId,
            name: productName,
            price: productPrice,
            quantity: quantity
        });
    }
    
    // Сохраняем обновленную корзину
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Обновляем отображение количества товаров в корзине
    updateCartItemCount();
    
    // Показываем сообщение об успешном добавлении
    showNotification('Товар добавлен в корзину');
}

// Функция для отображения уведомления
function showNotification(message) {
    // Проверяем, существует ли уже уведомление
    let notification = document.querySelector('.notification');
    
    if (!notification) {
        // Создаем элемент уведомления
        notification = document.createElement('div');
        notification.classList.add('notification');
        document.body.appendChild(notification);
    }
    
    // Обновляем текст и показываем уведомление
    notification.textContent = message;
    notification.classList.add('show');
    
    // Скрываем уведомление через 3 секунды
    setTimeout(function() {
        notification.classList.remove('show');
    }, 3000);
} 

// Инициализация дополнительных функций доступности
console.log("Инициализация дополнительных функций доступности из main.js");
console.log("Применение сохраненных настроек");

// Обработчики для кнопок избранного и сравнения
document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для кнопок избранного
    const favoriteButtons = document.querySelectorAll('.btn-toggle-favorite');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;

            fetch(`/favorites/toggle/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновление текста кнопки
                    if (this.dataset.inFavorites === "true") {
                        this.innerHTML = '<i class="far fa-heart"></i> В избранное';
                        this.dataset.inFavorites = "false";
                    } else {
                        this.innerHTML = '<i class="fas fa-heart"></i> Убрать из избранного';
                        this.dataset.inFavorites = "true";
                    }

                    // Обновить счетчик в шапке, если он есть
                    const favoritesCount = document.querySelector('.favorites-count');
                    if (favoritesCount) {
                        favoritesCount.textContent = data.count;
                    }
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });

    // Обработчики для кнопок сравнения
    const compareButtons = document.querySelectorAll('.btn-toggle-compare');
    compareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;

            fetch(`/compare/toggle/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновление текста кнопки
                    if (this.dataset.inCompare === "true") {
                        this.innerHTML = '<i class="far fa-balance-scale"></i> Сравнить';
                        this.dataset.inCompare = "false";
                    } else {
                        this.innerHTML = '<i class="fas fa-balance-scale"></i> Убрать из сравнения';
                        this.dataset.inCompare = "true";
                    }

                    // Обновить счетчик в шапке, если он есть
                    const compareCount = document.querySelector('.compare-count');
                    if (compareCount) {
                        compareCount.textContent = data.count;
                    }
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });
});

// Визуальное оформление активной страницы в навигации
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;

    // Находим все ссылки в основной навигации
    const navLinks = document.querySelectorAll('nav a');

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');

        // Проверяем, совпадает ли путь ссылки с текущим путем
        if (linkPath === currentPath || 
            (linkPath !== '/' && currentPath.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });