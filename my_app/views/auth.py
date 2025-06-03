"""
Blueprint для аутентификации пользователей
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from my_app.extensions import db
from my_app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

# Создаем Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в систему"""
    # Если пользователь уже авторизован, перенаправляем на главную
    if 'user_id' in session:
        return redirect(url_for('shop.home'))

    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверяем, существует ли пользователь по имени пользователя
        user = User.query.filter_by(username=username).first()

        # Если пользователь не найден по имени, проверяем по email
        if not user:
            user = User.query.filter_by(email=username).first()

        if user and user.check_password(password):
            # Очищаем сессию перед авторизацией для избежания проблем
            session.clear()
            # Авторизуем пользователя
            session['user_id'] = user.id
            # Устанавливаем флаг is_admin в сессию
            session['is_admin'] = user.is_admin
            session.permanent = True  # Делаем сессию постоянной

            # Если есть параметр next, перенаправляем туда
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('shop.home'))
        else:
            flash('Неверный логин или пароль', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    # Если пользователь уже авторизован, перенаправляем на главную
    if 'user_id' in session:
        return redirect(url_for('shop.home'))
    
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Проверяем, что пароли совпадают
        if password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return redirect(url_for('auth.register'))
        
        # Проверяем, что имя пользователя и email уникальны
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('auth.register'))
        
        # Создаем нового пользователя
        user = User(
            username=username,
            email=email,
            is_active=True
        )
        user.set_password(password)
        
        # Сохраняем пользователя
        db.session.add(user)
        db.session.commit()
        
        # Авторизуем пользователя
        session['user_id'] = user.id
        # Устанавливаем флаг is_admin в сессию
        session['is_admin'] = user.is_admin
        
        flash('Вы успешно зарегистрировались', 'success')
        return redirect(url_for('shop.home'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """Выход из системы"""
    # Удаляем пользователя из сессии
    session.pop('user_id', None)
    # Удаляем флаг администратора
    session.pop('is_admin', None)
    
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('shop.home'))