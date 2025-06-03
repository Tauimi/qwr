"""
Скрипт для выполнения миграции базы данных PostgreSQL
"""
import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from my_app import create_app

def execute_migration():
    """Выполняет миграцию базы данных для добавления колонки sku"""
    # Получаем URL базы данных из переменной окружения
    database_url = os.environ.get('DATABASE_URL', '')
    
    if not database_url:
        print("Ошибка: Не указан URL базы данных")
        sys.exit(1)
    
    # Преобразование URL из формата postgres:// в postgresql:// для psycopg2
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://')
    
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Проверяем существование колонки sku
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'sku';
        """)
        
        column_exists = cursor.fetchone()
        
        if not column_exists:
            print("Колонка 'sku' не существует. Добавляем...")
            # Добавляем колонку sku
            cursor.execute(sql.SQL("""
                ALTER TABLE products 
                ADD COLUMN sku VARCHAR(50) NULL;
            """))
            print("Колонка 'sku' успешно добавлена.")
        else:
            print("Колонка 'sku' уже существует.")
        
        # Закрываем соединение
        cursor.close()
        conn.close()
        
        print("Миграция успешно завершена.")
        return True
    
    except Exception as e:
        print(f"Ошибка при выполнении миграции: {str(e)}")
        return False

if __name__ == "__main__":
    # Создаем приложение для доступа к контексту, если нужно
    app = create_app(os.getenv('APP_SETTINGS', 'development'))
    
    print("Запуск миграции базы данных...")
    execute_migration()
