
// Скрипт для отображения количества товаров в сравнении
document.addEventListener('DOMContentLoaded', function() {
    // Функция для обновления счетчика сравнения
    function updateCompareCount() {
        fetch('/compare/count')
            .then(response => response.json())
            .then(data => {
                const compareCountElement = document.getElementById('compareCount');
                if (compareCountElement) {
                    compareCountElement.textContent = data.count;
                    
                    // Если количество равно 0, скрываем счетчик
                    if (data.count === 0) {
                        compareCountElement.style.display = 'none';
                    } else {
                        compareCountElement.style.display = 'inline-block';
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка при получении данных сравнения:', error);
            });
    }
    
    // Инициализация счетчика при загрузке страницы
    updateCompareCount();
    
    // Обработчик для кнопок добавления в сравнение
    document.querySelectorAll('.add-to-compare, .toggle-compare').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            const productId = this.getAttribute('data-product-id');
            const isToggle = this.classList.contains('toggle-compare');
            
            let url = isToggle 
                ? `/compare/toggle/${productId}`
                : `/compare/add/${productId}`;
                
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем счетчик
                    updateCompareCount();
                    
                    // Обновляем иконку для кнопки переключения
                    if (isToggle) {
                        const icon = this.querySelector('i');
                        if (icon) {
                            if (icon.classList.contains('fa-balance-scale')) {
                                icon.classList.remove('fa-balance-scale');
                                icon.classList.add('fa-balance-scale-right');
                                this.classList.add('active');
                            } else {
                                icon.classList.remove('fa-balance-scale-right');
                                icon.classList.add('fa-balance-scale');
                                this.classList.remove('active');
                            }
                        }
                    }
                    
                    // Показываем уведомление
                    showNotification(data.message);
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Ошибка при добавлении в сравнение:', error);
                showNotification('Произошла ошибка при добавлении в сравнение', 'error');
            });
        });
    });
    
    // Функция для отображения уведомления
    function showNotification(message, type = 'success') {
        // Проверяем, есть ли уже контейнер для уведомлений
        let notificationContainer = document.querySelector('.notification-container');
        
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.className = 'notification-container';
            document.body.appendChild(notificationContainer);
        }
        
        // Создаем новое уведомление
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Добавляем уведомление в контейнер
        notificationContainer.appendChild(notification);
        
        // Автоматически удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.classList.add('hide');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    // Стили для уведомлений, если их еще нет
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
            }
            
            .notification {
                background-color: #28a745;
                color: white;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 4px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                opacity: 1;
                transition: opacity 0.3s;
            }
            
            .notification.error {
                background-color: #dc3545;
            }
            
            .notification.hide {
                opacity: 0;
            }
        `;
        document.head.appendChild(style);
    }
});
