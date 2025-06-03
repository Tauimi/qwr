// Функции для специальных возможностей
document.addEventListener('DOMContentLoaded', function() {
    // Проверка на необходимость сброса настроек (для тестирования)
    // Можно закомментировать эту строку в продакшн
    // resetSettings();
    
    // Удаляем класс default-theme, так как он нужен только для начальной загрузки
    document.body.classList.remove('default-theme');
    
    // Проверяем, первое ли это посещение и инициализируем настройки по умолчанию
    initDefaultSettings();
    
    // Загружаем сохраненные настройки из localStorage
    loadAccessibilitySettings();
    
    // Обработчики для кнопок управления специальными возможностями
    const easyReadingBtn = document.getElementById('increase-font');
    const darkThemeBtn = document.getElementById('dark-theme');
    
    if (easyReadingBtn) {
        easyReadingBtn.addEventListener('click', function() {
            toggleEasyReadingMode();
        });
    } else {
        console.error('Кнопка режима для слабовидящих не найдена');
    }
    
    if (darkThemeBtn) {
        darkThemeBtn.addEventListener('click', function() {
            toggleDarkTheme();
        });
    } else {
        console.error('Кнопка темной темы не найдена');
    }
    
    // Добавляем обработчик для голосового управления, если браузер поддерживает Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        initVoiceControl();
    }

    // Логирование для отладки
    console.log('Accessibility settings loaded:');
    console.log('Dark theme:', localStorage.getItem('dark-theme'));
    console.log('Easy reading mode:', localStorage.getItem('easy-reading-mode'));
    console.log('Current classes on body:', document.body.className);
    
    // Добавляем тестовую функцию для проверки работы режима для слабовидящих в консоли
    window.testAccessibility = function() {
        console.log('Testing accessibility...');
        console.log('Current classes on body:', document.body.className);
        console.log('large-font applied:', document.body.classList.contains('large-font'));
        console.log('high-contrast applied:', document.body.classList.contains('high-contrast'));
        console.log('Font size of body:', window.getComputedStyle(document.body).fontSize);
        console.log('Color of body:', window.getComputedStyle(document.body).color);
        console.log('Background of body:', window.getComputedStyle(document.body).backgroundColor);
    };
});

// Функция для инициализации настроек по умолчанию при первом посещении
function initDefaultSettings() {
    // Метка, которая указывает, что настройки уже были установлены
    if (localStorage.getItem('settings-initialized') === null) {
        console.log('Первый запуск: инициализация настроек по умолчанию');
        
        // Устанавливаем светлую тему и отключенный режим для слабовидящих по умолчанию
        localStorage.setItem('dark-theme', 'false');
        localStorage.setItem('easy-reading-mode', 'false');
        
        // Устанавливаем метку, что настройки инициализированы
        localStorage.setItem('settings-initialized', 'true');
        
        // Принудительно удаляем классы тем и доступности
        document.body.classList.remove('dark-theme', 'large-font', 'high-contrast');
        document.documentElement.classList.remove('dark-theme', 'large-font', 'high-contrast');
        document.documentElement.style.fontSize = '';
    } else {
        console.log('Настройки уже инициализированы');
        
        // Дополнительная проверка корректности настроек
        if (localStorage.getItem('dark-theme') === null) {
            localStorage.setItem('dark-theme', 'false');
        }
        
        if (localStorage.getItem('easy-reading-mode') === null) {
            localStorage.setItem('easy-reading-mode', 'false');
        }
    }
}

// Функция для переключения режима удобного чтения (комбинированный режим большого шрифта и высокого контраста)
function toggleEasyReadingMode() {
    console.log('Переключение режима для слабовидящих');
    
    // Проверяем текущее состояние режима
    const hadLargeFont = document.body.classList.contains('large-font');
    
    // Переключаем классы как для body, так и для html
    document.body.classList.toggle('large-font');
    document.body.classList.toggle('high-contrast');
    document.documentElement.classList.toggle('large-font');
    document.documentElement.classList.toggle('high-contrast');
    
    // Проверяем новое состояние
    const hasLargeFont = document.body.classList.contains('large-font');
    
    console.log('Режим для слабовидящих переключен:', hasLargeFont);
    
    // Принудительно обновляем стили и запускаем перерисовку
    if (hasLargeFont) {
        // Если включаем режим, устанавливаем больший размер
        document.documentElement.style.fontSize = '150%';
        // Принудительная перерисовка
        document.body.style.display = 'none';
        setTimeout(() => document.body.style.display = '', 5);
    } else {
        // Если выключаем режим, возвращаем исходный размер
        document.documentElement.style.fontSize = '';
        // Принудительная перерисовка
        document.body.style.display = 'none';
        setTimeout(() => document.body.style.display = '', 5);
    }
    
    // Сохраняем настройку в localStorage
    localStorage.setItem('easy-reading-mode', hasLargeFont);
    
    // Обновляем иконку и текст на кнопке
    const easyReadingBtn = document.getElementById('increase-font');
    if (easyReadingBtn) {
        const textSpan = easyReadingBtn.querySelector('.button-text');
        const iconElement = easyReadingBtn.querySelector('i');
        
        if (hasLargeFont) {
            easyReadingBtn.title = 'Выключить режим для слабовидящих';
            easyReadingBtn.setAttribute('aria-pressed', 'true');
            easyReadingBtn.classList.add('active');
            
            if (textSpan) {
                textSpan.textContent = 'Обычный режим';
            }
            
            if (iconElement) {
                iconElement.className = 'fas fa-eye';
            }
        } else {
            easyReadingBtn.title = 'Режим для слабовидящих';
            easyReadingBtn.setAttribute('aria-pressed', 'false');
            easyReadingBtn.classList.remove('active');
            
            if (textSpan) {
                textSpan.textContent = 'Доступность';
            }
            
            if (iconElement) {
                iconElement.className = 'fas fa-glasses';
            }
        }
    }
}

// Функция для переключения темной темы
function toggleDarkTheme() {
    // Добавляем плавное переключение темы
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    
    // Переключаем класс для обоих элементов
    document.body.classList.toggle('dark-theme');
    document.documentElement.classList.toggle('dark-theme');
    
    // Сохраняем настройку в localStorage
    const isDarkTheme = document.body.classList.contains('dark-theme');
    localStorage.setItem('dark-theme', isDarkTheme);
    
    console.log('Dark theme toggled:', isDarkTheme);
    
    // Обновляем иконку на кнопке
    const darkThemeBtn = document.getElementById('dark-theme');
    if (darkThemeBtn) {
        const iconElement = darkThemeBtn.querySelector('i');
        const textSpan = darkThemeBtn.querySelector('.button-text');
        
        if (isDarkTheme) {
            darkThemeBtn.title = 'Светлая тема';
            darkThemeBtn.classList.add('active');
            
            if (iconElement) {
                iconElement.className = 'fas fa-sun';
            }
            
            if (textSpan) {
                textSpan.textContent = 'Тема';
            }
        } else {
            darkThemeBtn.title = 'Тёмная тема';
            darkThemeBtn.classList.remove('active');
            
            if (iconElement) {
                iconElement.className = 'fas fa-moon';
            }
            
            if (textSpan) {
                textSpan.textContent = 'Тема';
            }
        }
    }
    
    // Принудительная перерисовка для применения изменений
    document.body.style.display = 'none';
    setTimeout(() => {
        document.body.style.display = '';
        
        // Сбрасываем transition после анимации
        setTimeout(() => {
            document.body.style.transition = '';
            document.documentElement.style.transition = '';
        }, 300);
    }, 5);
}

// Функция для загрузки сохраненных настроек
function loadAccessibilitySettings() {
    // Проверяем, было ли уже первое посещение
    if (localStorage.getItem('settings-initialized') === null) {
        // Инициализируем настройки по умолчанию
        initDefaultSettings();
    }
    
    // Проверяем значения в localStorage (должны быть true или false)
    const easyReadingMode = localStorage.getItem('easy-reading-mode') === 'true';
    const darkTheme = localStorage.getItem('dark-theme') === 'true';
    
    console.log('Загружаем настройки:', { easyReadingMode, darkTheme });
    
    // Сначала удаляем все классы, чтобы вернуться к состоянию по умолчанию
    document.body.classList.remove('dark-theme', 'large-font', 'high-contrast');
    document.documentElement.classList.remove('dark-theme', 'large-font', 'high-contrast');
    
    // Применяем классы только если настройки явно включены
    if (easyReadingMode) {
        document.body.classList.add('large-font', 'high-contrast');
        document.documentElement.classList.add('large-font', 'high-contrast');
        document.documentElement.style.fontSize = '150%';
    } else {
        document.documentElement.style.fontSize = '';
    }
    
    if (darkTheme) {
        document.body.classList.add('dark-theme');
        document.documentElement.classList.add('dark-theme');
    }
    
    // Обновляем состояние кнопок в соответствии с текущими настройками
    updateButtonsAppearance();
}

// Функция для обновления внешнего вида кнопок в соответствии с текущими настройками
function updateButtonsAppearance() {
    const easyReadingBtn = document.getElementById('increase-font');
    const darkThemeBtn = document.getElementById('dark-theme');
    
    if (easyReadingBtn) {
        const isEasyReadingMode = document.body.classList.contains('large-font');
        const textSpan = easyReadingBtn.querySelector('.button-text');
        const iconElement = easyReadingBtn.querySelector('i');
        
        if (isEasyReadingMode) {
            easyReadingBtn.title = 'Выключить режим для слабовидящих';
            easyReadingBtn.setAttribute('aria-pressed', 'true');
            easyReadingBtn.classList.add('active');
            
            if (textSpan) {
                textSpan.textContent = 'Обычный режим';
            }
            
            if (iconElement) {
                iconElement.className = 'fas fa-eye';
            }
        } else {
            easyReadingBtn.title = 'Режим для слабовидящих';
            easyReadingBtn.setAttribute('aria-pressed', 'false');
            easyReadingBtn.classList.remove('active');
            
            if (textSpan) {
                textSpan.textContent = 'Доступность';
            }
            
            if (iconElement) {
                iconElement.className = 'fas fa-glasses';
            }
        }
    }
    
    if (darkThemeBtn) {
        const isDarkTheme = document.body.classList.contains('dark-theme');
        const iconElement = darkThemeBtn.querySelector('i');
        const textSpan = darkThemeBtn.querySelector('.button-text');
        
        if (isDarkTheme) {
            darkThemeBtn.title = 'Светлая тема';
            darkThemeBtn.classList.add('active');
            
            if (iconElement) {
                iconElement.className = 'fas fa-sun';
            }
            
            if (textSpan) {
                textSpan.textContent = 'Тема';
            }
        } else {
            darkThemeBtn.title = 'Тёмная тема';
            darkThemeBtn.classList.remove('active');
            
            if (iconElement) {
                iconElement.className = 'fas fa-moon';
            }
            
            if (textSpan) {
                textSpan.textContent = 'Тема';
            }
        }
    }
}

// Функция для инициализации голосового управления
function initVoiceControl() {
    // Создаем экземпляр распознавания речи
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // Настройка распознавания
    recognition.lang = 'ru-RU';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    // Добавляем элемент для активации голосового управления
    const voiceControlBtn = document.createElement('button');
    voiceControlBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    voiceControlBtn.className = 'voice-control-button';
    voiceControlBtn.title = 'Голосовое управление';
    document.body.appendChild(voiceControlBtn);
    
    // Обработчик для кнопки голосового управления
    voiceControlBtn.addEventListener('click', function() {
        try {
            recognition.start();
            voiceControlBtn.classList.add('active');
        } catch (e) {
            console.error('Ошибка при запуске распознавания речи:', e);
        }
    });
    
    // Обработчик результатов распознавания
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript.toLowerCase();
        console.log('Распознанный текст:', transcript);
        
        // Обработка команд
        if (transcript.includes('главная') || transcript.includes('домой')) {
            window.location.href = '/';
        } else if (transcript.includes('каталог')) {
            window.location.href = '/catalog';
        } else if (transcript.includes('корзина')) {
            window.location.href = '/cart';
        } else if (transcript.includes('контакты')) {
            window.location.href = '/contact';
        } else if (transcript.includes('о компании')) {
            window.location.href = '/about';
        } else if (transcript.includes('доставка') || transcript.includes('оплата')) {
            window.location.href = '/delivery';
        } else if (transcript.includes('поиск')) {
            // Извлекаем поисковый запрос
            const searchQuery = transcript.replace('поиск', '').trim();
            if (searchQuery) {
                window.location.href = '/search?query=' + encodeURIComponent(searchQuery);
            } else {
                // Фокусируемся на поле поиска
                const searchInput = document.querySelector('.search-form input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        } else if (transcript.includes('режим для слабовидящих') || transcript.includes('увеличить шрифт') || transcript.includes('контраст')) {
            toggleEasyReadingMode();
        } else if (transcript.includes('темная тема') || transcript.includes('тёмная тема')) {
            toggleDarkTheme();
        }
    };
    
    // Обработчик окончания распознавания
    recognition.onend = function() {
        voiceControlBtn.classList.remove('active');
    };
    
    // Обработчик ошибок распознавания
    recognition.onerror = function(event) {
        console.error('Ошибка распознавания речи:', event.error);
        voiceControlBtn.classList.remove('active');
    };
}

// Функция для сброса настроек к состоянию по умолчанию (светлая тема, режим для слабовидящих отключен)
function resetSettings() {
    console.log('Сброс настроек к состоянию по умолчанию');
    
    // Сбрасываем настройки в localStorage
    localStorage.removeItem('settings-initialized');
    localStorage.setItem('dark-theme', 'false');
    localStorage.setItem('easy-reading-mode', 'false');
    
    // Удаляем все классы, связанные с темой и режимом для слабовидящих
    document.body.classList.remove('dark-theme', 'large-font', 'high-contrast');
    document.documentElement.classList.remove('dark-theme', 'large-font', 'high-contrast');
    document.documentElement.style.fontSize = '';
    
    // Для отладки добавляем в localStorage
    localStorage.setItem('settings-reset', new Date().toISOString());
} 