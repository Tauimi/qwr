"""
Blueprint для избранных товаров
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from my_app.extensions import db
from my_app.models import Product

# Создаем Blueprint
favorites_bp = Blueprint('favorites', __name__, url_prefix='/favorites')

@favorites_bp.route('/')
def index():
    """Страница избранных товаров"""
    # Получаем избранные товары из сессии
    favorites_items = []
    
    if 'favorites' in session:
        # Получаем товары из сессии
        for product_id in session['favorites']:
            product = Product.query.get(product_id)
            if product:
                favorites_items.append(product)
    
    return render_template('favorites.html', 
                          favorites_items=favorites_items)

@favorites_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_favorites(product_id):
    """Добавляет товар в избранное"""
    # Инициализируем список избранного, если его нет
    if 'favorites' not in session:
        session['favorites'] = []
    
    # Проверяем, есть ли уже этот товар в избранном
    favorites = session['favorites']
    if product_id not in favorites:
        favorites.append(product_id)
        session['favorites'] = favorites
        flash('Товар добавлен в избранное', 'success')
    else:
        flash('Товар уже в избранном', 'info')
    
    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'favorites_count': len(favorites)
        })
    
    # Иначе перенаправляем обратно
    return redirect(request.referrer or url_for('shop.home'))

@favorites_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_favorites(product_id):
    """Удаляет товар из избранного"""
    if 'favorites' not in session:
        return redirect(url_for('favorites.index'))
    
    # Удаляем товар из избранного
    favorites = session['favorites']
    if product_id in favorites:
        favorites.remove(product_id)
        session['favorites'] = favorites
        flash('Товар удален из избранного', 'success')
    
    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'favorites_count': len(favorites)
        })
    
    # Иначе перенаправляем на страницу избранного
    return redirect(url_for('favorites.index'))

@favorites_bp.route('/toggle/<int:product_id>', methods=['POST'])
def toggle_favorite(product_id):
    """Переключает статус товара в избранном"""
    # Инициализируем список избранного, если его нет
    if 'favorites' not in session:
        session['favorites'] = []
    
    favorites = session['favorites']
    status = 'added'
    
    # Если товар уже в избранном, удаляем его
    if product_id in favorites:
        favorites.remove(product_id)
        status = 'removed'
    # Иначе добавляем
    else:
        favorites.append(product_id)
        status = 'added'
    
    # Обновляем сессию
    session['favorites'] = favorites
    
    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'action': status,
            'favorites_count': len(favorites)
        })
    
    # Иначе перенаправляем обратно
    return redirect(request.referrer or url_for('shop.home')) 