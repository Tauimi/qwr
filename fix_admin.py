#!/usr/bin/env python
"""
Скрипт для исправления аккаунта администратора
"""
import os
from my_app import create_app
from my_app.extensions import db
from my_app.models import User
from werkzeug.security import generate_password_hash

# Данные для администратора
ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASSWORD = 'admin123'

# Создаем экземпляр приложения
app = create_app(os.getenv('APP_SETTINGS', 'development'))

def fix_admin_account():
    """Исправляет или создает аккаунт администратора"""
    with app.app_context():
        # Проверяем существование таблиц
        try:
            # Пробуем получить список пользователей
            users = User.query.all()
            print(f"Найдено пользователей: {len(users)}")
            
            # Выводим информацию о каждом пользователе для отладки
            for user in users:
                print(f"ID: {user.id}, Имя: {user.username}, Email: {user.email}, Админ: {user.is_admin}")
                
        except Exception as e:
            print(f"Ошибка при доступе к базе данных: {str(e)}")
            print("Создаем таблицы...")
            db.create_all()
            print("Таблицы созданы.")
        
        # Пытаемся найти администратора по имени пользователя
        admin = User.query.filter_by(username=ADMIN_USERNAME).first()
        
        if admin:
            # Если администратор существует, обновляем его данные
            print(f"Найден администратор: ID {admin.id}, Email: {admin.email}, Статус админа: {admin.is_admin}")
            
            # Обновляем флаг администратора, если он не установлен
            if not admin.is_admin:
                admin.is_admin = True
                print("Установлен флаг администратора")
            
            # Напрямую обновляем хеш пароля (вместо set_password)
            admin.password_hash = generate_password_hash(ADMIN_PASSWORD)
            print("Пароль администратора обновлен")
            
            # Обновляем email, если он не совпадает
            if admin.email != ADMIN_EMAIL:
                admin.email = ADMIN_EMAIL
                print(f"Email администратора обновлен на {ADMIN_EMAIL}")
            
            # Устанавливаем активный статус
            admin.is_active = True
            print("Аккаунт администратора активирован")
            
            # Сохраняем изменения
            db.session.commit()
            print("Аккаунт администратора успешно обновлен!")
        else:
            # Если администратор не существует, создаем его
            print("Администратор не найден. Создаем нового администратора...")
            
            # Создаем нового администратора
            admin = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                is_admin=True,
                is_active=True
            )
            
            # Напрямую устанавливаем хеш пароля
            admin.password_hash = generate_password_hash(ADMIN_PASSWORD)
            
            # Добавляем в базу данных
            db.session.add(admin)
            db.session.commit()
            
            print(f"Создан новый аккаунт администратора:")
            print(f"Логин: {ADMIN_USERNAME}")
            print(f"Пароль: {ADMIN_PASSWORD}")
            print(f"Email: {ADMIN_EMAIL}")
        
        # Проверяем учетные данные администратора
        verify_admin = User.query.filter_by(username=ADMIN_USERNAME).first()
        if verify_admin:
            print("\nПроверка учетных данных администратора:")
            print(f"Логин: {verify_admin.username}")
            print(f"Email: {verify_admin.email}")
            print(f"Флаг администратора: {verify_admin.is_admin}")
            print(f"Активный статус: {verify_admin.is_active}")
            print(f"Хеш пароля существует: {'Да' if verify_admin.password_hash else 'Нет'}")
        else:
            print("ОШИБКА: Не удалось создать администратора!")

if __name__ == "__main__":
    print("Начинаем исправление аккаунта администратора...")
    fix_admin_account()
    print("Операция завершена.")