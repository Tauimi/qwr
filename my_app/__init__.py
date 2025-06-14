"""
Монолитное Flask-приложение для деплоя на Railway, разбитое на модули
"""
import os
import logging
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, render_template, redirect, url_for, request, session, send_from_directory, abort, current_app, Markup
from .extensions import db, migrate, BreakExtension
from .config import config
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла, если он есть
load_dotenv()

def allowed_file(filename):
    """Проверяет, что файл имеет разрешенное расширение"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file, folder):
    """Сохраняет загруженное изображение в указанную папку"""
    # Проверяем, что файл имеет разрешенное расширение
    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла
        import uuid
        unique_filename = str(uuid.uuid4())
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{unique_filename}.{file_extension}"
        
        # Создаем полный путь для сохранения файла
        save_path = os.path.join(folder, filename)
        
        # Сохраняем файл
        file.save(save_path)
        
        # Возвращаем относительный путь к файлу
        return filename
    
    return None

# Определение фильтра nl2br для преобразования переносов строк в HTML теги <br>
def nl2br_filter(text):
    if not text:
        return ""
    return Markup(text.replace('\n', '<br>'))

# Функция для создания администратора при первом запуске
def create_admin_if_not_exists():
    """Создает пользователя-администратора, если в БД нет пользователей"""
    from .models import User
    
    # Проверяем есть ли пользователи в базе данных
    user_count = User.query.count()
    
    if user_count == 0:
        # Определяем данные администратора
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123!')
        
        # Создаем пользователя-администратора
        admin_user = User(
            username=admin_username,
            email=admin_email,
            is_admin=True,
            is_active=True
        )
        
        # Устанавливаем пароль
        admin_user.set_password(admin_password)
        
        # Сохраняем в базу данных
        db.session.add(admin_user)
        db.session.commit()
        
        # Логируем создание администратора
        current_app.logger.info(f'Создан администратор: {admin_username}')

def create_app(config_name=None):
    """Создает и настраивает экземпляр приложения Flask"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')

    # Определяем конфигурацию
    config_name = config_name or os.getenv('APP_SETTINGS', 'development')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Добавляем расширение для break
    app.jinja_env.add_extension(BreakExtension)
    
    # Регистрируем фильтр nl2br
    app.jinja_env.filters['nl2br'] = nl2br_filter

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)

    # Гарантируем создание всех таблиц перед первым запросом
    with app.app_context():
        db.create_all()
        
        # Создаем первого администратора, если нет пользователей
        create_admin_if_not_exists()

    # Настройка логирования
    if not app.debug:
        # Создание директории для логов, если её нет
        logs_dir = os.path.join(app.root_path, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Настройка форматирования логов
        file_handler = logging.FileHandler(os.path.join(logs_dir, 'app.log'))
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Приложение запущено')

    # Регистрация обработчиков запросов перед запросом
    @app.before_request
    def initialize_session():
        """Инициализирует сессию для неавторизованных пользователей"""
        if 'cart' not in session:
            session['cart'] = []
        if 'favorites' not in session:
            session['favorites'] = []
        if 'compare' not in session:
            session['compare'] = []
        if 'visited_products' not in session:
            session['visited_products'] = []
        
    # Добавление отслеживания посетителей
    @app.before_request
    def track_visitor():
        """Отслеживает посетителей сайта"""
        # Пропускаем запросы к статическим файлам и API
        if request.path.startswith('/static') or request.path.startswith('/api'):
            return
            
        # Получаем IP-адрес и User-Agent
        from .models import Visitor
        
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        page = request.path
        
        # Сохраняем информацию о посетителе
        visitor = Visitor(
            ip_address=ip_address,
            user_agent=user_agent,
            page_visited=page
        )
        
        # Добавляем в сессию и коммитим
        db.session.add(visitor)
        db.session.commit()

    # Регистрация обработчиков ошибок
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    # Регистрация основных маршрутов
    @app.route('/about')
    def about_redirect():
        return redirect(url_for('static_pages.about'))

    # Добавляем аналогичные перенаправления для остальных статических страниц
    @app.route('/delivery')
    def delivery_redirect():
        return redirect(url_for('static_pages.delivery'))
        
    @app.route('/contact', methods=['GET', 'POST'])
    def contact_redirect():
        # Если это POST запрос, перенаправляем его на обработчик формы обратной связи
        if request.method == 'POST':
            # Импортируем функцию submit из модуля feedback
            from .views.feedback import submit
            return submit()
        # Для GET запросов, перенаправляем на страницу контактов
        return redirect(url_for('static_pages.contact'))
        
    @app.route('/sitemap')
    def sitemap_redirect():
        return redirect(url_for('static_pages.sitemap'))
        
    @app.route('/terms')
    def terms_redirect():
        return redirect(url_for('static_pages.terms'))
        
    @app.route('/privacy')
    def privacy_redirect():
        return redirect(url_for('static_pages.privacy'))
        
    @app.route('/returns')
    def returns_redirect():
        return redirect(url_for('static_pages.returns'))
        
    @app.route('/warranty')
    def warranty_redirect():
        return redirect(url_for('static_pages.warranty'))
        
    @app.route('/faq')
    def faq_redirect():
        return redirect(url_for('static_pages.faq'))

    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'ok',
            'version': '1.0.0',
            'server_time': str(datetime.now())
        })

    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy'
        })

    # Импортируем и регистрируем все blueprints
    from .views import all_blueprints
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    # Возвращаем созданное приложение
    return app