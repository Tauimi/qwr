// Функция для инициализации карусели баннеров
function initBannerCarousel() {
    const carousel = document.querySelector('.carousel');
    if (!carousel) return;

    const carouselInner = carousel.querySelector('.carousel-inner');
    const carouselItems = carousel.querySelectorAll('.carousel-item');
    const indicators = carousel.querySelectorAll('.carousel-indicator');
    const prevBtn = carousel.querySelector('.carousel-control.prev');
    const nextBtn = carousel.querySelector('.carousel-control.next');

    let currentIndex = 0;
    const itemCount = carouselItems.length;

    // Функция для обновления отображения карусели
    function updateCarousel() {
        carouselInner.style.transform = `translateX(-${currentIndex * 100}%)`;

        indicators.forEach((indicator, index) => {
            if (index === currentIndex) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
    }

    // Переход к следующему слайду
    function nextSlide() {
        currentIndex = (currentIndex + 1) % itemCount;
        updateCarousel();
    }

    // Переход к предыдущему слайду
    function prevSlide() {
        currentIndex = (currentIndex - 1 + itemCount) % itemCount;
        updateCarousel();
    }

    // Назначение обработчиков событий
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);
    if (prevBtn) prevBtn.addEventListener('click', prevSlide);

    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            currentIndex = index;
            updateCarousel();
        });
    });

    // Автоматическая смена слайдов
    const autoplayInterval = setInterval(nextSlide, 5000);

    // Остановка автопрокрутки при наведении
    carousel.addEventListener('mouseenter', () => {
        clearInterval(autoplayInterval);
    });

    // Возобновление автопрокрутки при уходе курсора
    carousel.addEventListener('mouseleave', () => {
        autoplayInterval = setInterval(nextSlide, 5000);
    });

    // Поддержка свайпов для мобильных устройств
    let touchstartX = 0;
    let touchendX = 0;

    carousel.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    });

    carousel.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        const threshold = 50;
        if (touchendX < touchstartX - threshold) {
            nextSlide();
        }
        if (touchendX > touchstartX + threshold) {
            prevSlide();
        }
    }
}

// Функция для инициализации карусели товаров
function initProductCarousel() {
    // Получаем все карусели товаров на странице
    const productCarousels = document.querySelectorAll('.product-carousel');

    productCarousels.forEach(carousel => {
        const container = carousel.querySelector('.product-carousel-items');
        const prevBtn = carousel.querySelector('.product-carousel-control.prev-new');
        const nextBtn = carousel.querySelector('.product-carousel-control.next-new');

        if (!container || !prevBtn || !nextBtn) return;

        // Назначаем обработчики событий для кнопок
        prevBtn.addEventListener('click', () => {
            container.scrollBy({
                left: -300,
                behavior: 'smooth'
            });
        });

        nextBtn.addEventListener('click', () => {
            container.scrollBy({
                left: 300,
                behavior: 'smooth'
            });
        });

        // Оптимизация скролла для мобильных устройств
        let isDown = false;
        let startX;
        let scrollLeft;

        container.addEventListener('mousedown', (e) => {
            isDown = true;
            container.classList.add('active');
            startX = e.pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
        });

        container.addEventListener('mouseleave', () => {
            isDown = false;
            container.classList.remove('active');
        });

        container.addEventListener('mouseup', () => {
            isDown = false;
            container.classList.remove('active');
        });

        container.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const walk = (x - startX) * 2;
            container.scrollLeft = scrollLeft - walk;
        });
    });
}

// Функция для инициализации карусели на главной странице
document.addEventListener('DOMContentLoaded', function() {
    initModernCarousel();
});

function initModernCarousel() {
    // Получаем элементы карусели
    const slides = document.querySelectorAll('.carousel-slide');
    const indicators = document.querySelectorAll('.indicator');
    const prevBtn = document.querySelector('.carousel-arrow.prev');
    const nextBtn = document.querySelector('.carousel-arrow.next');

    if (!slides.length || !indicators.length) {
        console.log('Элементы карусели не найдены');
        return;
    }

    console.log('Инициализация карусели:', slides.length, 'слайдов');

    let currentIndex = 0;
    let interval;

    // Функция для переключения слайда
    function goToSlide(index) {
        // Отладка
        console.log('Переключение на слайд:', index);

        // Убираем активный класс со всех слайдов и индикаторов
        slides.forEach(slide => slide.classList.remove('active'));
        indicators.forEach(dot => dot.classList.remove('active'));

        // Добавляем активный класс нужному слайду и индикатору
        currentIndex = (index + slides.length) % slides.length;
        slides[currentIndex].classList.add('active');
        indicators[currentIndex].classList.add('active');
    }

    // Автоматическое переключение
    function startAutoSlide() {
        clearInterval(interval); // Предотвращаем множественный запуск
        interval = setInterval(() => {
            goToSlide(currentIndex + 1);
        }, 5000); // Меняем слайд каждые 5 секунд
    }

    // Останавливаем автоматическое переключение при наведении
    const carouselWrapper = document.querySelector('.carousel-wrapper');
    if (carouselWrapper) {
        carouselWrapper.addEventListener('mouseenter', () => {
            clearInterval(interval);
        });

        // Возобновляем при уходе курсора
        carouselWrapper.addEventListener('mouseleave', () => {
            startAutoSlide();
        });
    }

    // Обработчики для кнопок
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            goToSlide(currentIndex - 1);
            clearInterval(interval);
            startAutoSlide();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            goToSlide(currentIndex + 1);
            clearInterval(interval);
            startAutoSlide();
        });
    }

    // Обработчики для индикаторов
    indicators.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            goToSlide(index);
            clearInterval(interval);
            startAutoSlide();
        });
    });

    // Поддержка свайпов для мобильных устройств
    let touchStartX = 0;
    let touchEndX = 0;

    if (carouselWrapper) {
        carouselWrapper.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });

        carouselWrapper.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
    }

    function handleSwipe() {
        if (touchEndX < touchStartX - 50) {
            // Свайп влево - следующий слайд
            goToSlide(currentIndex + 1);
            clearInterval(interval);
            startAutoSlide();
        } else if (touchEndX > touchStartX + 50) {
            // Свайп вправо - предыдущий слайд
            goToSlide(currentIndex - 1);
            clearInterval(interval);
            startAutoSlide();
        }
    }

    // Инициализация первого слайда и запуск автопрокрутки
    goToSlide(0);
    startAutoSlide();

    console.log('Карусель успешно инициализирована');
}