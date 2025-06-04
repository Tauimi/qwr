"""
Blueprint для основных страниц магазина
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, abort, send_from_directory
import os
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import selectinload
from my_app.extensions import db
from my_app.models.product import Product
from my_app.models.category import Category
from my_app.models.visitor import Visitor
from my_app.models.review import Review
from my_app.models.review_vote import ReviewVote
from my_app.models.rating import Rating
from my_app.models.feedback import FeedbackMessage

# Создаем Blueprint
shop_bp = Blueprint('shop', __name__, url_prefix='')

@shop_bp.route('/')
def home():
    """Главная страница"""
    # Получаем популярные товары
    featured_products = Product.query.filter_by(is_featured=True).limit(8).all()
    
    # Получаем новинки
    new_products = Product.query.filter_by(is_new=True).order_by(Product.created_at.desc()).limit(8).all()
    
    # Получаем товары со скидкой
    sale_products = Product.query.filter_by(is_sale=True).order_by(Product.created_at.desc()).limit(8).all()
    
    # Получаем категории для меню
    categories = Category.query.filter_by(parent_id=None).all()
    
    # Получаем все товары для отображения на главной странице
    products = featured_products
    
    # Статистика
    stats = {
        'products_count': Product.query.count(),
        'categories_count': Category.query.count(),
    }
    
    # Получаем статистику посетителей
    try:
        visitor_stats = Visitor.get_visitors_stats()
        stats.update(visitor_stats)
    except Exception as e:
        current_app.logger.error(f"Ошибка получения статистики посетителей: {str(e)}")
    
    return render_template('index.html', 
                          featured_products=featured_products,
                          new_products=new_products,
                          sale_products=sale_products,
                          categories=categories,
                          products=products,
                          stats=stats)

@shop_bp.route('/catalog')
def catalog():
    """Страница каталога"""
    sort_by = request.args.get('sort', 'default')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)

    categories = Category.query.filter_by(parent_id=None).all()
    products_query = Product.query

    products_query = products_query.options(
        selectinload(Product.category),
        selectinload(Product.specifications)
    )

    avg_rating_reviews_subquery = db.session.query(
        Review.product_id.label('product_id'),
        func.avg(Review.rating).label('avg_review_rating'),
        func.count(Review.id).label('total_ratings_count')
    ).group_by(Review.product_id).subquery('avg_rating_sub')

    positive_reviews_subquery = db.session.query(
        Review.product_id.label('product_id'),
        func.count(Review.id).label('positive_reviews_count')
    ).filter(Review.rating > 3).group_by(Review.product_id).subquery('positive_reviews_sub')

    products_query = products_query.outerjoin(
        avg_rating_reviews_subquery,
        Product.id == avg_rating_reviews_subquery.c.product_id
    ).outerjoin(
        positive_reviews_subquery,
        Product.id == positive_reviews_subquery.c.product_id
    ).add_columns(
        func.coalesce(avg_rating_reviews_subquery.c.avg_review_rating, 0).label('avg_rating'),
        func.coalesce(avg_rating_reviews_subquery.c.total_ratings_count, 0).label('total_ratings_count'),
        func.coalesce(positive_reviews_subquery.c.positive_reviews_count, 0).label('positive_reviews_count')
    )

    if sort_by == 'price_low':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        products_query = products_query.order_by(Product.price.desc())
    elif sort_by == 'newest':
        products_query = products_query.order_by(Product.created_at.desc())
    elif sort_by == 'rating_high':
        products_query = products_query.order_by(desc('avg_rating'))
    elif sort_by == 'rating_low':
        products_query = products_query.order_by(asc('avg_rating'))
    elif sort_by == 'reviews_high':
        products_query = products_query.order_by(desc('positive_reviews_count'))
    else: # default
        products_query = products_query.order_by(Product.name.asc())
    
    pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items

    return render_template(
        'catalog.html',
        products=products,
        categories=categories,
        pagination=pagination,
        sort_by=sort_by
    )

@shop_bp.route('/category/<int:category_id>')
def category(category_id):
    """Страница категории"""
    sort_by = request.args.get('sort', 'default')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)
    
    category_obj = Category.query.get_or_404(category_id)
    products_query = Product.query.filter_by(category_id=category_id)

    products_query = products_query.options(
        selectinload(Product.specifications)
        # Product.category будет уже загружен т.к. фильтруем по category_id
    )

    avg_rating_reviews_subquery = db.session.query(
        Review.product_id.label('product_id'),
        func.avg(Review.rating).label('avg_review_rating'),
        func.count(Review.id).label('total_ratings_count')
    ).group_by(Review.product_id).subquery('avg_rating_sub')

    positive_reviews_subquery = db.session.query(
        Review.product_id.label('product_id'),
        func.count(Review.id).label('positive_reviews_count')
    ).filter(Review.rating > 3).group_by(Review.product_id).subquery('positive_reviews_sub')

    products_query = products_query.outerjoin(
        avg_rating_reviews_subquery,
        Product.id == avg_rating_reviews_subquery.c.product_id
    ).outerjoin(
        positive_reviews_subquery,
        Product.id == positive_reviews_subquery.c.product_id
    ).add_columns(
        func.coalesce(avg_rating_reviews_subquery.c.avg_review_rating, 0).label('avg_rating'),
        func.coalesce(avg_rating_reviews_subquery.c.total_ratings_count, 0).label('total_ratings_count'),
        func.coalesce(positive_reviews_subquery.c.positive_reviews_count, 0).label('positive_reviews_count')
    )
    
    if sort_by == 'price_low':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        products_query = products_query.order_by(Product.price.desc())
    elif sort_by == 'newest':
        products_query = products_query.order_by(Product.created_at.desc())
    elif sort_by == 'rating_high':
        products_query = products_query.order_by(desc('avg_rating')) 
    elif sort_by == 'rating_low':
        products_query = products_query.order_by(asc('avg_rating'))
    elif sort_by == 'reviews_high':
        products_query = products_query.order_by(desc('positive_reviews_count'))
    else: # default
        products_query = products_query.order_by(Product.name.asc())

    pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    
    return render_template(
        'category.html',
        category=category_obj, 
        products=products,
        pagination=pagination,
        sort_by=sort_by
    )

@shop_bp.route('/product/<int:product_id>')
def product(product_id):
    """Страница товара"""
    product = Product.query.get_or_404(product_id)
    
    # Добавляем товар в список просмотренных, если его там еще нет
    if 'visited_products' not in session:
        session['visited_products'] = []
    
    visited_products = session['visited_products']
    if product_id not in visited_products:
        visited_products.append(product_id)
        session['visited_products'] = visited_products[:10]  # Храним только 10 последних

@shop_bp.route('/product_modal/<int:product_id>')
def product_modal(product_id):
    """Возвращает HTML для модального окна товара"""
    product = Product.query.get_or_404(product_id)
    # The logic for visited products is not needed for the modal view
    # as it's handled by the full product page or can be moved to client-side if desired.

    # Fetch related products for the modal as well
    related_products = Product.query.filter(Product.category_id == product.category_id, Product.id != product_id).limit(4).all()

    # Fetch reviews and ratings for the modal
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    total_reviews = len(reviews)
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(product_id=product_id).scalar()
    if avg_rating is None: avg_rating = 0

    # Render a partial template for the modal content
    return render_template('product_modal_content.html', 
                           product=product, 
                           related_products=related_products,
                           reviews=reviews,
                           total_reviews=total_reviews,
                           avg_rating=avg_rating)

@shop_bp.route('/search')
def search():
    """Поиск товаров"""
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('shop.catalog'))
    
    # Поиск товаров с похожим названием
    products = Product.query.filter(
        Product.name.ilike(f'%{query}%') | 
        Product.description.ilike(f'%{query}%')
    ).all()
    
    # Поиск категорий с похожим названием
    categories = Category.query.filter(
        Category.name.ilike(f'%{query}%')
    ).all()
    
    return render_template('search_results.html', 
                          query=query, 
                          products=products, 
                          categories=categories)

@shop_bp.route('/carousel/<int:slide_id>')
def get_carousel_image(slide_id):
    """Возвращает изображение для карусели"""
    # Словарь с именами файлов для каждого слайда
    carousel_images = {
        1: 'carousel-1.jpg',
        2: 'carousel-2.jpg',
        3: 'carousel-3.jpg'
    }
    
    # Получаем имя файла или используем запасное изображение
    image_name = carousel_images.get(slide_id, 'carousel-default.jpg')
    
    # Путь к директории с изображениями карусели
    carousel_dir = os.path.join(current_app.static_folder, 'images', 'carousel')
    
    # Если директория не существует, создаем ее
    if not os.path.exists(carousel_dir):
        os.makedirs(carousel_dir)
        
        # Если файлы не существуют, используем запасное изображение
        if not os.path.exists(os.path.join(carousel_dir, image_name)):
            image_name = 'default.jpg'
    
    return send_from_directory(os.path.join(current_app.static_folder, 'images', 'carousel'), image_name)