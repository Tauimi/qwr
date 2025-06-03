"""
Blueprint для панели администратора
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from my_app.extensions import db
from my_app.models import Product, Category, User, Order, CategorySpecificationTemplate, Specification
from functools import wraps
import os
from werkzeug.utils import secure_filename
import uuid

# Создаем Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Декоратор для проверки авторизации администратора
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Необходимо войти в систему', 'danger')
            return redirect(url_for('auth.login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Доступ запрещен', 'danger')
            return redirect(url_for('shop.home'))
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def index():
    """Главная страница панели администратора"""
    # Статистика
    stats = {
        'products_count': Product.query.count(),
        'categories_count': Category.query.count(),
        'users_count': User.query.count(),
        'orders_count': Order.query.count(),
    }
    
    # Последние заказы
    latest_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Последние зарегистрированные пользователи
    latest_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                          stats=stats,
                          latest_orders=latest_orders,
                          latest_users=latest_users)

@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    """Страница управления категориями"""
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        
        if parent_id == '':
            parent_id = None
        
        # Проверяем, загружено ли изображение
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                    # Генерируем уникальное имя файла
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    file.save(os.path.join(current_app.config['CATEGORY_IMAGES'], filename))
                    image = filename
        
        # Создаем новую категорию
        category = Category(
            name=name,
            slug=slug,
            description=description,
            parent_id=parent_id,
            image=image
        )
        
        # Сохраняем категорию
        db.session.add(category)
        db.session.commit()
        
        flash('Категория успешно создана', 'success')
        return redirect(url_for('admin.categories'))
    
    # Получаем все категории
    categories = Category.query.all()
    
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """Страница редактирования категории"""
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        # Получаем данные из формы
        category.name = request.form.get('name')
        category.slug = request.form.get('slug')
        category.description = request.form.get('description')
        
        parent_id = request.form.get('parent_id')
        if parent_id == '':
            category.parent_id = None
        else:
            category.parent_id = parent_id
        
        # Проверяем, загружено ли новое изображение
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                    # Генерируем уникальное имя файла
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    file.save(os.path.join(current_app.config['CATEGORY_IMAGES'], filename))
                    
                    # Удаляем старое изображение, если оно есть
                    if category.image:
                        try:
                            os.remove(os.path.join(current_app.config['CATEGORY_IMAGES'], category.image))
                        except:
                            pass
                    
                    category.image = filename
        
        # Обработка характеристик категории
        if 'spec_name' in request.form and 'spec_description' in request.form and 'spec_required' in request.form:
            spec_names = request.form.getlist('spec_name')
            spec_descriptions = request.form.getlist('spec_description')
            spec_required = request.form.getlist('spec_required')
            
            # Проверяем, есть ли новые характеристики
            for i in range(len(spec_names)):
                if spec_names[i]:
                    # Создаем новый шаблон характеристики
                    spec_template = CategorySpecificationTemplate(
                        category_id=category.id,
                        name=spec_names[i],
                        description=spec_descriptions[i],
                        required='on' in spec_required
                    )
                    db.session.add(spec_template)
        
        # Сохраняем изменения
        db.session.commit()
        
        flash('Категория успешно обновлена', 'success')
        return redirect(url_for('admin.categories'))
    
    # Получаем все категории для селекта
    categories = Category.query.all()
    
    return render_template('admin/edit_category.html', 
                          category=category,
                          categories=categories)

@admin_bp.route('/categories/remove_spec_template/<int:template_id>', methods=['POST'])
@admin_required
def remove_spec_template(template_id):
    """Удаляет шаблон характеристики категории"""
    template = CategorySpecificationTemplate.query.get_or_404(template_id)
    category_id = template.category_id
    
    # Удаляем шаблон
    db.session.delete(template)
    db.session.commit()
    
    flash('Шаблон характеристики удален', 'success')
    return redirect(url_for('admin.edit_category', category_id=category_id))

@admin_bp.route('/categories/<int:category_id>/spec_templates', methods=['GET'])
@admin_required
def get_category_spec_templates(category_id):
    """Возвращает список шаблонов характеристик для категории в JSON формате"""
    category = Category.query.get_or_404(category_id)
    templates = []
    
    for template in category.specification_templates:
        templates.append({
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'required': template.required
        })
    
    # Получаем также шаблоны родительской категории, если она есть
    if category.parent_id:
        parent = Category.query.get(category.parent_id)
        if parent:
            for template in parent.specification_templates:
                templates.append({
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'required': template.required,
                    'inherited': True
                })
    
    return {'templates': templates}

@admin_bp.route('/products', methods=['GET', 'POST'])
@admin_required
def products():
    """Страница управления товарами"""
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        slug = request.form.get('slug')
        sku = request.form.get('sku')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        old_price = request.form.get('old_price')
        if old_price:
            old_price = float(old_price)
        stock = int(request.form.get('stock'))
        category_id = request.form.get('category_id')
        if category_id == '':
            category_id = None
        
        # Проверяем, загружено ли изображение
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                    # Генерируем уникальное имя файла
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    file.save(os.path.join(current_app.config['PRODUCT_IMAGES'], filename))
                    image = filename
        
        # Создаем новый товар
        product = Product(
            name=name,
            slug=slug,
            sku=sku,
            description=description,
            price=price,
            old_price=old_price,
            stock=stock,
            category_id=category_id,
            image=image,
            is_featured='is_featured' in request.form,
            is_new='is_new' in request.form,
            is_sale='is_sale' in request.form
        )
        
        # Сохраняем товар
        db.session.add(product)
        db.session.commit()
        
        # Добавляем характеристики товара
        if 'spec_name' in request.form and 'spec_value' in request.form:
            spec_names = request.form.getlist('spec_name')
            spec_values = request.form.getlist('spec_value')
            
            for i in range(len(spec_names)):
                if spec_names[i] and spec_values[i]:
                    # Создаем новую характеристику
                    spec = Specification(
                        product_id=product.id,
                        name=spec_names[i],
                        value=spec_values[i]
                    )
                    db.session.add(spec)
            
            db.session.commit()
        
        flash('Товар успешно создан', 'success')
        return redirect(url_for('admin.products'))
    
    # Получаем все товары и категории
    products = Product.query.all()
    categories = Category.query.all()
    
    return render_template('admin/products.html', 
                          products=products,
                          categories=categories)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    """Страница редактирования товара"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        # Получаем данные из формы
        product.name = request.form.get('name')
        product.slug = request.form.get('slug')
        product.sku = request.form.get('sku')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        
        old_price = request.form.get('old_price')
        if old_price:
            product.old_price = float(old_price)
        else:
            product.old_price = None
            
        product.stock = int(request.form.get('stock'))
        
        category_id = request.form.get('category_id')
        if category_id == '':
            product.category_id = None
        else:
            product.category_id = category_id
        
        # Проверяем, загружено ли новое изображение
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                    # Генерируем уникальное имя файла
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    file.save(os.path.join(current_app.config['PRODUCT_IMAGES'], filename))
                    
                    # Удаляем старое изображение, если оно есть и не является дефолтным
                    if product.image and product.image != 'default-product.jpg':
                        try:
                            os.remove(os.path.join(current_app.config['PRODUCT_IMAGES'], product.image))
                        except:
                            pass
                    
                    product.image = filename
        
        # Обновляем флаги
        product.is_featured = 'is_featured' in request.form
        product.is_new = 'is_new' in request.form
        product.is_sale = 'is_sale' in request.form
        
        # Добавляем новые характеристики товара
        if 'spec_name' in request.form and 'spec_value' in request.form:
            spec_names = request.form.getlist('spec_name')
            spec_values = request.form.getlist('spec_value')
            
            for i in range(len(spec_names)):
                if spec_names[i] and spec_values[i]:
                    # Создаем новую характеристику
                    spec = Specification(
                        product_id=product.id,
                        name=spec_names[i],
                        value=spec_values[i]
                    )
                    db.session.add(spec)
        
        # Сохраняем изменения
        db.session.commit()
        
        flash('Товар успешно обновлен', 'success')
        return redirect(url_for('admin.products'))
    
    # Получаем все категории
    categories = Category.query.all()
    
    return render_template('admin/edit_product.html', 
                          product=product,
                          categories=categories)

@admin_bp.route('/products/<int:product_id>/remove_specification', methods=['POST'])
@admin_required
def remove_specification(product_id):
    """Удаляет характеристику товара"""
    spec_id = request.form.get('spec_id')
    
    if not spec_id:
        flash('Не указан ID характеристики', 'danger')
        return redirect(url_for('admin.edit_product', product_id=product_id))
    
    # Получаем характеристику
    spec = Specification.query.get_or_404(spec_id)
    
    # Проверяем, принадлежит ли характеристика этому товару
    if spec.product_id != product_id:
        flash('Характеристика не принадлежит этому товару', 'danger')
        return redirect(url_for('admin.edit_product', product_id=product_id))
    
    # Удаляем характеристику
    db.session.delete(spec)
    db.session.commit()
    
    flash('Характеристика успешно удалена', 'success')
    return redirect(url_for('admin.edit_product', product_id=product_id))

@admin_bp.route('/products/update_stock', methods=['POST'])
@admin_required
def update_stock():
    """Обновляет остаток товара"""
    product_id = request.form.get('product_id')
    stock = request.form.get('stock')
    
    if not product_id or not stock:
        flash('Не указан ID товара или количество', 'danger')
        return redirect(url_for('admin.products'))
    
    # Получаем товар
    product = Product.query.get_or_404(product_id)
    
    # Обновляем остаток
    product.stock = int(stock)
    db.session.commit()
    
    flash('Остаток товара успешно обновлен', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/users')
@admin_required
def users():
    """Страница управления пользователями"""
    # Получаем всех пользователей
    users = User.query.all()
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/orders')
@admin_required
def orders():
    """Страница управления заказами"""
    # Получаем все заказы, сортированные по дате (сначала новые)
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    # Рассчитываем общую сумму заказов
    total_amount = sum(order.total_amount for order in orders)
    
    # Статистика по статусам заказов
    status_stats = {}
    for order in orders:
        if order.status in status_stats:
            status_stats[order.status] += 1
        else:
            status_stats[order.status] = 1
    
    return render_template('admin/orders.html', 
                          orders=orders,
                          total_amount=total_amount,
                          status_stats=status_stats) 