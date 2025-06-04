"""
Blueprint для корзины и оформления заказа
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from my_app.extensions import db
from my_app.models import Product, Order
from datetime import datetime
import uuid

# Создаем Blueprint
cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/', methods=['GET', 'POST'])
def index():
    """Страница корзины"""
    cart_items = []
    total = 0
    
    if 'cart' in session:
        # Получаем товары из сессии
        for item in session['cart']:
            product = Product.query.get(item['product_id'])
            if product:
                quantity = item['quantity']
                price = product.price
                subtotal = price * quantity
                
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': price,
                    'subtotal': subtotal
                })
                
                total += subtotal
    
    # Проверяем, был ли применен промокод
    discount = 0
    if 'discount' in session:
        discount = session['discount']
        total = total - (total * discount / 100)
    
    return render_template('cart.html', 
                          cart_items=cart_items, 
                          total=total,
                          discount=discount)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Добавляет товар в корзину"""
    product = Product.query.get_or_404(product_id)
    
    # Получаем количество из формы
    quantity = int(request.form.get('quantity', 1))
    
    # Проверяем, что количество положительное
    if quantity <= 0:
        quantity = 1
    
    # Проверяем наличие товара на складе
    if product.stock < quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'error',
                'message': 'Недостаточно товара на складе',
                'product_id': product.id
            }), 400 # Возвращаем статус 400 Bad Request
        else:
            flash('Недостаточно товара на складе', 'danger')
            return redirect(url_for('shop.product', product_id=product.id))
    
    # Инициализируем корзину, если её нет
    if 'cart' not in session:
        session['cart'] = []
    
    # Проверяем, есть ли уже этот товар в корзине
    cart = session['cart']
    found = False
    
    for item in cart:
        if item['product_id'] == product_id:
            # Увеличиваем количество
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        # Добавляем новый товар в корзину
        cart.append({
            'product_id': product_id,
            'quantity': quantity
        })
    
    # Обновляем сессию
    session['cart'] = cart

    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': 'Товар добавлен в корзину',
            'count': sum(item['quantity'] for item in cart)
        })
    else:
        flash('Товар добавлен в корзину', 'success')
        # Иначе перенаправляем на страницу корзины
        return redirect(url_for('cart.index'))

@cart_bp.route('/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    """Обновляет количество товара в корзине"""
    quantity = int(request.form.get('quantity', 1))

    if 'cart' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Корзина не найдена'}), 400
        return redirect(url_for('cart.index')) # Остается для не-AJAX

    product = Product.query.get(product_id)
    if not product:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Товар не найден'}), 404
        flash('Товар не найден', 'danger')
        return redirect(url_for('cart.index'))

    if quantity <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Количество должно быть больше нуля'}), 400
        flash('Количество должно быть больше нуля', 'danger')
        return redirect(url_for('cart.index'))

    # Проверка на наличие на складе
    if product.stock < quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'error',
                'message': f'Недостаточно товара "{product.name}" на складе (в наличии: {product.stock})',
                'product_id': product.id
            }), 400
        else:
            flash(f'Недостаточно товара "{product.name}" на складе (в наличии: {product.stock})', 'danger')
            # ВАЖНО: Если обновляем на странице корзины, и товара не хватает,
            # не позволяем установить количество больше, чем есть на складе.
            # Возвращаем пользователя на корзину, чтобы он увидел сообщение.
            # Можно также вернуть JSON с актуальным доступным количеством.
            # Пока просто редирект с flash. Для AJAX - ошибка.
            return redirect(url_for('cart.index'))


    cart = session['cart']
    found = False
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            found = True
            break
    
    if not found: # Если товара не было в корзине (маловероятно для update, но для полноты)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Товар не найден в корзине для обновления'}), 404
        flash('Товар не найден в корзине для обновления', 'warning')
        return redirect(url_for('cart.index'))

    session['cart'] = cart

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': 'Корзина обновлена',
            'count': sum(item['quantity'] for item in cart),
            'product_id': product_id, # для обновления конкретной строки, если нужно
            'new_quantity': quantity, # для обновления конкретной строки
            'new_subtotal': product.price * quantity # Посчитаем здесь, чтобы JS не думал
        })
    else:
        flash('Корзина обновлена', 'success')
        return redirect(url_for('cart.index'))

@cart_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Удаляет товар из корзины"""
    if 'cart' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Корзина не найдена для удаления товара'}), 400
        return redirect(url_for('cart.index'))

    cart = session['cart']
    original_length = len(cart)
    session['cart'] = [item for item in cart if item['product_id'] != product_id]
    
    if len(session['cart']) == original_length: # Товар не был найден и удален
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Товар не найден в корзине для удаления'}), 404
        flash('Товар не найден в корзине', 'warning')
        return redirect(url_for('cart.index'))


    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'message': 'Товар удален из корзины',
            'count': sum(item['quantity'] for item in session.get('cart', [])), # session.get для безопасности
            'removed_product_id': product_id
        })
    else:
        flash('Товар удален из корзины', 'success')
        return redirect(url_for('cart.index'))

@cart_bp.route('/apply_promocode', methods=['POST'])
def apply_promocode():
    """Применяет промокод"""
    # В реальном приложении здесь должна быть проверка промокода из базы данных
    # и расчет скидки на основе условий промокода
    promocode = request.form.get('promocode', '').strip()
    
    if promocode == 'DISCOUNT10':
        session['discount'] = 10
        flash('Промокод успешно применен. Скидка 10%', 'success')
    else:
        flash('Неверный промокод', 'danger')
    
    return redirect(url_for('cart.index'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Страница оформления заказа"""
    # Проверяем, есть ли товары в корзине
    if 'cart' not in session or not session['cart']:
        flash('Корзина пуста', 'warning')
        return redirect(url_for('shop.home'))
    
    # Получаем товары из корзины
    cart_items = []
    total = 0
    
    for item in session['cart']:
        product = Product.query.get(item['product_id'])
        if product:
            quantity = item['quantity']
            price = product.price
            subtotal = price * quantity
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal
            })
            
            total += subtotal
    
    # Учитываем скидку, если есть
    discount = 0
    if 'discount' in session:
        discount = session['discount']
        total = total - (total * discount / 100)
    
    if request.method == 'POST':
        # Получаем данные из формы
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        postal_code = request.form.get('postal_code')
        payment_method = request.form.get('payment_method')
        shipping_method = request.form.get('shipping_method')
        
        # Создаем новый заказ
        order = Order(
            user_id=session.get('user_id'),
            status='pending',
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            payment_method=payment_method,
            shipping_method=shipping_method,
            total_amount=total
        )
        
        # Добавляем товары к заказу
        for item in cart_items:
            product = item['product']
            quantity = item['quantity']
            
            # Добавляем информацию о количестве и цене в промежуточную таблицу
            db.session.execute(
                db.Table('order_items').insert().values(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=product.price
                )
            )
            
            # Уменьшаем количество товара на складе
            product.stock -= quantity
        
        # Сохраняем заказ
        db.session.add(order)
        db.session.commit()
        
        # Очищаем корзину
        session.pop('cart', None)
        session.pop('discount', None)
        
        # Перенаправляем на страницу успешного оформления заказа
        flash('Заказ успешно оформлен!', 'success')
        return redirect(url_for('cart.order_success', order_id=order.id))
    
    return render_template('checkout.html', 
                          cart_items=cart_items, 
                          total=total,
                          discount=discount)

@cart_bp.route('/order/success/<int:order_id>')
def order_success(order_id):
    """Страница успешного оформления заказа"""
    order = Order.query.get_or_404(order_id)
    return render_template('order_success.html', order=order)

@cart_bp.route('/order/<int:order_id>')
def order_detail(order_id):
    """Страница деталей заказа"""
    order = Order.query.get_or_404(order_id)
    
    # Проверяем, имеет ли пользователь доступ к этому заказу
    if order.user_id and order.user_id != session.get('user_id'):
        flash('У вас нет доступа к этому заказу', 'danger')
        return redirect(url_for('shop.home'))
    
    # Получаем товары заказа
    order_items = order.get_items_with_quantities()
    
    return render_template('order_detail.html', 
                          order=order,
                          order_items=order_items)

@cart_bp.route('/count')
def get_cart_count():
    """Возвращает количество товаров в корзине"""
    count = 0
    if 'cart' in session:
        count = sum(item['quantity'] for item in session['cart'])
    
    return jsonify({
        'count': count
    }) 