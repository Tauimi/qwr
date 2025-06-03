
// Home page specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Обработка кнопок избранного
    document.querySelectorAll('.btn-toggle-favorite, .favorite-button').forEach(button => {
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
                    // Обновление визуального состояния кнопки
                    this.classList.toggle('active');
                    if (this.dataset.inFavorites === "true") {
                        this.dataset.inFavorites = "false";
                        this.title = "Добавить в избранное";
                    } else {
                        this.dataset.inFavorites = "true";
                        this.title = "Удалить из избранного";
                    }

                    // Обновить счетчик в шапке
                    const favoritesCount = document.querySelector('.favorites-count');
                    if (favoritesCount) {
                        favoritesCount.textContent = data.count;
                    }
                }
            })
            .catch(error => console.error('Ошибка:', error));
        });
    });

    // Обработка кнопок сравнения
    document.querySelectorAll('.btn-toggle-compare, .compare-button').forEach(button => {
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
                    // Обновление визуального состояния кнопки
                    this.classList.toggle('active');
                    if (this.dataset.inCompare === "true") {
                        this.dataset.inCompare = "false";
                        this.title = "Добавить к сравнению";
                    } else {
                        this.dataset.inCompare = "true";
                        this.title = "Удалить из сравнения";
                    }

                    // Обновить счетчик в шапке
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
