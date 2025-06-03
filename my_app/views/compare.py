"""
Blueprint для сравнения товаров
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from my_app.extensions import db
from my_app.models import Product, Category

# Создаем Blueprint
compare_bp = Blueprint('compare', __name__, url_prefix='/compare')

@compare_bp.route('/')
def index():
    """Страница сравнения товаров"""
    # Получаем товары для сравнения из сессии
    compare_items = []
    all_specs = {}
    categories = {}
    
    if 'compare' in session and session['compare']:
        # Получаем товары из сессии
        for product_id in session['compare']:
            product = Product.query.get(product_id)
            if product:
                compare_items.append(product)
                
                # Получаем категорию товара
                if product.category:
                    category_id = product.category.id
                    if category_id not in categories:
                        categories[category_id] = product.category
                
                # Собираем все характеристики
                for spec in product.specifications:
                    spec_name = spec.name
                    if spec_name not in all_specs:
                        all_specs[spec_name] = {
                            'name': spec_name,
                            'values': {}
                        }
                    all_specs[spec_name]['values'][product.id] = spec.value
    
    # Преобразуем словарь характеристик в список для удобства в шаблоне
    specs_list = []
    for spec_name, spec_data in all_specs.items():
        specs_list.append({
            'name': spec_name,
            'values': spec_data['values']
        })
    
    # Если в сессии есть только один товар, то показываем все товары той же категории
    related_products = []
    if len(compare_items) == 1 and compare_items[0].category:
        related_products = Product.query.filter(
            Product.category_id == compare_items[0].category_id,
            Product.id != compare_items[0].id
        ).limit(4).all()
    
    return render_template('compare.html', 
                          compare_items=compare_items,
                          specs=specs_list,
                          categories=list(categories.values()),
                          related_products=related_products)

@compare_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_compare(product_id):
    """Добавляет товар к сравнению"""
    # Получаем товар
    product = Product.query.get_or_404(product_id)
    
    # Инициализируем список сравнения, если его нет
    if 'compare' not in session:
        session['compare'] = []
    
    # Проверяем, есть ли уже этот товар в сравнении
    compare = session['compare']
    max_compare_items = 4  # Максимальное количество товаров в сравнении
    
    if product_id not in compare:
        # Проверяем, есть ли другие товары в сравнении
        if compare:
            # Проверяем, принадлежат ли товары к одной категории
            other_product = Product.query.get(compare[0])
            if other_product and other_product.category_id != product.category_id:
                flash('Можно сравнивать только товары из одной категории', 'warning')
                return redirect(request.referrer or url_for('shop.home'))
        
        # Проверяем, не превышено ли максимальное количество
        if len(compare) >= max_compare_items:
            flash(f'Вы можете сравнить максимум {max_compare_items} товаров', 'warning')
        else:
            compare.append(product_id)
            session['compare'] = compare
            flash('Товар добавлен к сравнению', 'success')
    else:
        flash('Товар уже добавлен к сравнению', 'info')
    
    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'compare_count': len(compare)
        })
    
    # Иначе перенаправляем обратно
    return redirect(request.referrer or url_for('shop.home'))

@compare_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_compare(product_id):
    """Удаляет товар из сравнения"""
    if 'compare' not in session:
        return redirect(url_for('compare.index'))
    
    # Удаляем товар из сравнения
    compare = session['compare']
    if product_id in compare:
        compare.remove(product_id)
        session['compare'] = compare
        flash('Товар удален из сравнения', 'success')
    
    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'compare_count': len(compare)
        })
    
    # Иначе перенаправляем на страницу сравнения
    return redirect(url_for('compare.index'))

@compare_bp.route('/clear', methods=['POST'])
def clear_compare():
    """Очищает список сравнения"""
    if 'compare' in session:
        session.pop('compare')
        flash('Список сравнения очищен', 'success')
    
    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'compare_count': 0
        })
    
    # Иначе перенаправляем на главную
    return redirect(url_for('shop.home'))

@compare_bp.route('/toggle/<int:product_id>', methods=['POST'])
def toggle_compare(product_id):
    """Переключает статус товара в сравнении"""
    # Получаем товар
    product = Product.query.get_or_404(product_id)
    
    # Инициализируем список сравнения, если его нет
    if 'compare' not in session:
        session['compare'] = []
    
    compare = session['compare']
    status = 'added'
    max_compare_items = 4  # Максимальное количество товаров в сравнении
    
    # Если товар уже в сравнении, удаляем его
    if product_id in compare:
        compare.remove(product_id)
        status = 'removed'
    # Иначе добавляем, если не превышено максимальное количество
    elif len(compare) < max_compare_items:
        # Проверяем, есть ли другие товары в сравнении
        if compare:
            # Проверяем, принадлежат ли товары к одной категории
            other_product = Product.query.get(compare[0])
            if other_product and other_product.category_id != product.category_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Можно сравнивать только товары из одной категории'
                })
        
        compare.append(product_id)
        status = 'added'
    else:
        return jsonify({
            'status': 'error',
            'message': f'Вы можете сравнить максимум {max_compare_items} товаров'
        })
    
    # Обновляем сессию
    session['compare'] = compare
    
    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'action': status,
            'compare_count': len(compare)
        })
    
    # Иначе перенаправляем обратно
    return redirect(request.referrer or url_for('shop.home'))

@compare_bp.route('/count')
def get_compare_count():
    """Возвращает количество товаров в сравнении"""
    count = 0
    if 'compare' in session:
        count = len(session['compare'])
    
    return jsonify({
        'count': count
    }) 