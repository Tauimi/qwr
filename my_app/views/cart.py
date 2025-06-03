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
    flash('Товар добавлен в корзину', 'success')
    
    # Если запрос был AJAX, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'success',
            'cart_count': sum(item['quantity'] for item in cart)
        })
    
    # Иначе перенаправляем на страницу корзины
    return redirect(url_for('cart.index'))

@cart_bp.route('/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    """Обновляет количество товара в корзине"""
    # Получаем новое количество из формы
    quantity = int(request.form.get('quantity', 1))
    
    # Проверяем, что количество положительное
    if quantity <= 0:
        flash('Количество должно быть больше нуля', 'danger')
        return redirect(url_for('cart.index'))
    
    # Проверяем, есть ли корзина
    if 'cart' not in session:
        return redirect(url_for('cart.index'))
    
    # Обновляем количество товара
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            break
    
    # Обновляем сессию
    session['cart'] = cart
    flash('Корзина обновлена', 'success')
    
    return redirect(url_for('cart.index'))

@cart_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Удаляет товар из корзины"""
    if 'cart' not in session:
        return redirect(url_for('cart.index'))
    
    # Ищем товар в корзине и удаляем его
    cart = session['cart']
    session['cart'] = [item for item in cart if item['product_id'] != product_id]
    
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