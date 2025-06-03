"""
Blueprint для личного кабинета пользователя
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from my_app.extensions import db
from my_app.models import User, Order
from werkzeug.security import check_password_hash
from functools import wraps

# Создаем Blueprint
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

# Декоратор для проверки авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Необходимо войти в систему', 'danger')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@profile_bp.route('/')
@login_required
def index():
    """Главная страница личного кабинета"""
    # Получаем пользователя
    user = User.query.get(session['user_id'])
    
    # Получаем заказы пользователя
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    
    return render_template('profile.html', 
                          user=user,
                          orders=orders)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Страница редактирования профиля"""
    # Получаем пользователя
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        # Получаем данные из формы
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Проверяем, изменился ли email
        if email != user.email:
            # Проверяем, что email уникален
            if User.query.filter_by(email=email).first():
                flash('Пользователь с таким email уже существует', 'danger')
                return redirect(url_for('profile.edit'))
        
        # Обновляем данные пользователя
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        user.address = address
        
        # Если заполнены поля для изменения пароля
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            # Проверяем текущий пароль
            if not user.check_password(current_password):
                flash('Неверный текущий пароль', 'danger')
                return redirect(url_for('profile.edit'))
            
            # Проверяем, что новые пароли совпадают
            if new_password != confirm_password:
                flash('Новые пароли не совпадают', 'danger')
                return redirect(url_for('profile.edit'))
            
            # Обновляем пароль
            user.set_password(new_password)
        
        # Сохраняем изменения
        db.session.commit()
        
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('profile.index'))
    
    return render_template('edit_profile.html', user=user) 