# Монолитное Flask-приложение для Render

## Описание проблемы и решение

В процессе деплоя возникла ошибка из-за отсутствия Blueprint'ов, которые использовались в шаблонах. 
Проблема возникла при переходе с модульной на монолитную структуру приложения.

```
werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'shop.home'. Did you mean 'health' instead?
```

Решение:
1. Добавлены Blueprint'ы в app.py для совместимости со старыми шаблонами
2. Изменена команда запуска в render.yaml с `gunicorn wsgi:application` на `gunicorn app:app`
3. Добавлен шаблон для админ-панели

## Инструкция по деплою

1. Убедитесь, что в файле `render.yaml` команда запуска указана правильно: `gunicorn wsgi:application`
2. Залейте изменения в репозиторий GitHub:
```
git add .
git commit -m "Исправлены ошибки деплоя, добавлены Blueprint'ы и шаблоны"
git push
```
3. Убедитесь, что на Render настроена автоматическая сборка из ветки `main`
4. Дождитесь завершения деплоя и проверьте логи на наличие ошибок

## Структура проекта

- `app.py` - основной файл приложения с маршрутами и моделями
- `wsgi.py` - файл для запуска через WSGI
- `render.yaml` - конфигурация для Render
- `templates/` - HTML-шаблоны
- `static/` - статические файлы (CSS, JS, изображения)
- `requirements.txt` - зависимости проекта
- `init_db.py` - скрипт для инициализации базы данных
- `flask_app.py` - файл для работы с Flask CLI (например, миграции)
- `logs/` - папка для логов (создается автоматически)
- `migrations/` - папка для миграций (создается автоматически)

## Локальный запуск (для разработки)

1. Создайте виртуальное окружение:
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Установите зависимости:
```
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта (опционально):
```
APP_SETTINGS=development
SECRET_KEY=your-secret-key
```

4. Инициализируйте базу данных:
```
python init_db.py
```

5. Запустите приложение:
```
python app.py
```

6. Или используйте Flask CLI:
```
set FLASK_APP=flask_app.py  # Windows
export FLASK_APP=flask_app.py  # Linux/Mac
flask run
```

## База данных

В режиме разработки используется SQLite, в продакшене - PostgreSQL (предоставляется Render).
При деплое на Render база данных создается автоматически согласно настройкам в `render.yaml`. 

### Миграции базы данных

Для управления схемой базы данных используется Flask-Migrate:

1. Инициализация папки миграций (только один раз):
```
python init_db.py
flask db init
```

2. Создание миграции после изменения моделей:
```
flask db migrate -m "Описание изменений"
```

3. Применение миграций:
```
flask db upgrade
```

4. Для отката миграции:
```
flask db downgrade
``` 