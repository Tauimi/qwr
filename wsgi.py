"""
WSGI-файл для запуска приложения через Gunicorn
"""
import os
import sys

# Автоматическое заполнение настроек перед импортом приложения
try:
    from auto_config import setup_railway_config
    setup_railway_config()
    print("✅ Автоматическая настройка успешно применена")
except Exception as e:
    print(f"⚠️ Ошибка при автоматической настройке: {str(e)}")

# Импортируем фабрику приложения после настройки переменных окружения
from my_app import create_app
from my_app.extensions import db

# Создаем экземпляр приложения
app = create_app(os.getenv('APP_SETTINGS', 'production'))  # Используем production по умолчанию для Railway

# Определяем стандартную переменную application для совместимости с WSGI серверами
application = app

# Проверяем наличие подключения к базе данных
database_url = os.environ.get('DATABASE_URL')
with app.app_context():
    try:
        # Проверяем соединение с базой данных
        db.engine.connect()
        print("✅ Подключение к базе данных успешно")
        
        if database_url:
            print("✅ База данных настроена")
            # Импортируем и запускаем скрипт заполнения базы данных только если это явно указано
            if os.environ.get('SEED_DATABASE', 'False') == 'True':
                try:
                    from seed_db import seed_db
                    result = seed_db()
                    if result:
                        print("✅ База данных заполнена тестовыми данными")
                    else:
                        print("ℹ️ База данных уже содержит данные, дополнительное заполнение не требуется")
                except Exception as e:
                    print(f"⚠️ Ошибка заполнения базы данных: {str(e)}")
                    print("   Продолжаем работу с существующими данными")
        else:
            print("ℹ️ База данных не настроена")
            print("   Приложение запущено в демо-режиме с локальной SQLite базой")
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {str(e)}")
        print("   Приложение запущено в демо-режиме")

if __name__ == "__main__":
    app.run()