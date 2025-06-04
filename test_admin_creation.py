"""
Скрипт для тестирования создания администратора при первом запуске
"""
import os
from my_app import create_app
from my_app.extensions import db
from my_app.models import User

# Создаем приложение
app = create_app('development')

# Контекст приложения
with app.app_context():
    # Удаляем всех пользователей для теста
    try:
        user_count = User.query.count()
        print(f"Текущее количество пользователей: {user_count}")
        
        if user_count > 0:
            # Очищаем таблицу пользователей
            User.query.delete()
            db.session.commit()
            print("Все пользователи удалены")
        
        # Проверяем, что пользователей нет
        assert User.query.count() == 0
        print("Проверка успешна: база данных не содержит пользователей")
        
        # Вызываем функцию для создания администратора
        from my_app import create_admin_if_not_exists
        create_admin_if_not_exists()
        
        # Проверяем, что администратор создан
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            print(f"Администратор успешно создан:")
            print(f"- Имя пользователя: {admin_user.username}")
            print(f"- Email: {admin_user.email}")
            print(f"- Создан: {admin_user.created_at}")
            assert admin_user.is_admin == True
            assert admin_user.is_active == True
            print("Все проверки пройдены успешно!")
        else:
            print("ОШИБКА: Администратор не был создан!")
    
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        db.session.rollback()

print("Тестирование завершено.") 