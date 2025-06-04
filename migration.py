"""
Скрипт для выполнения миграции базы данных
"""
import os
import sys
from flask_migrate import upgrade, stamp, migrate, init
from my_app import create_app
from my_app.extensions import db

def execute_migration():
    """Выполняет миграцию базы данных через Flask-Migrate"""
    # Создаем экземпляр приложения
    app = create_app(os.getenv('APP_SETTINGS', 'production'))

    # Проверяем наличие переменной окружения DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Предупреждение: Не указан URL базы данных. Используется SQLite.")
    try:
        with app.app_context():
            # Проверяем существует ли каталог migrations/versions
            migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations', 'versions')

            if not os.path.exists(migrations_dir):
                print("Каталог миграций не существует. Инициализируем миграции...")
                init()
                print("Миграции инициализированы.")

            # Проверяем, существует ли колонка sku в таблице products
            inspect = db.inspect(db.engine)
            if inspect.has_table('products'):
                columns = [column['name'] for column in inspect.get_columns('products')]
                if 'sku' not in columns:
                    print("Колонка 'sku' не существует в таблице products. Создаем миграцию...")
                    # Создаем миграцию
                    migrate(message="Add sku column to products")
                    print("Миграция создана.")

                    # Применяем миграцию
                    upgrade()
                    print("Миграция применена.")
                else:
                    print("Колонка 'sku' уже существует в таблице products.")
                    # Ставим метку текущей версии базы данных
                    stamp()
            else:
                print("Таблица 'products' не существует. Создаем схему базы данных...")
                db.create_all()
                print("Схема базы данных создана.")
        
                # Инициализируем миграции и ставим метку
                stamp()
                print("Метка текущей версии базы данных установлена.")
        print("Миграция успешно завершена.")
        return True
    
    except Exception as e:
        print(f"Ошибка при выполнении миграции: {str(e)}")
        return False

if __name__ == "__main__":
    print("Запуск миграции базы данных...")
    execute_migration()
