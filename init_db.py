#!/usr/bin/env python
"""
Скрипт для инициализации базы данных и миграций
"""
import os
from my_app import create_app
from my_app.extensions import db
from my_app.models import User

# Создаем экземпляр приложения
app = create_app(os.getenv('APP_SETTINGS', 'development'))

def init_db():
    """Инициализирует базу данных"""
    with app.app_context():
        # Создаем все таблицы если они не существуют
        db.create_all()
        
        # Проверяем, существует ли уже админ
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Создаем администратора
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Создан аккаунт администратора:")
            print("Логин: admin")
            print("Пароль: admin123")
        
        print("База данных инициализирована успешно!")

def create_migration_folder():
    """Создает папку для миграций, если она не существует"""
    migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations')
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
        print(f"Создана директория для миграций: {migrations_dir}")
    else:
        print(f"Директория для миграций уже существует: {migrations_dir}")

if __name__ == "__main__":
    print("Инициализация базы данных...")
    create_migration_folder()
    init_db()
    print("Теперь вы можете создать миграции командой:")
    print("flask db init")
    print("flask db migrate -m 'Initial migration'")
    print("flask db upgrade")
    print("Инициализация базы данных завершена.")
