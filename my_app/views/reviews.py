"""
Blueprint для отзывов о товарах
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask import session, g
from my_app.extensions import db
from my_app.models import Review, ReviewVote, Product, User, Rating, ReviewPhoto, DetailedRating, Order
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

# Создаем Blueprint
reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

# Конфигурация для загрузки файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_review_photo(file):
    """Сохраняет фото отзыва и возвращает имя файла"""
    if file and allowed_file(file.filename):
        # Создаем уникальное имя файла
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Создаем директорию для фотографий отзывов, если она не существует
        upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'reviews')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Сохраняем файл
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def check_verified_purchase(user_id, product_id):
    """Проверяет, покупал ли пользователь данный товар"""
    if not user_id:
        return False
    
    # Проверяем наличие товара в заказах пользователя
    orders_with_product = Order.query.filter(
        Order.user_id == user_id,
        Order.order_items.any(product_id=product_id)
    ).count()
    
    return orders_with_product > 0

@reviews_bp.route('/add/<int:product_id>', methods=['POST'])
def add_review(product_id):
    """Добавить отзыв о товаре"""
    product = Product.query.get_or_404(product_id)
    
    # Получаем базовую информацию об отзыве
    rating = int(request.form.get('rating', 0))
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    pros = request.form.get('pros', '')
    cons = request.form.get('cons', '')
    usage_period = request.form.get('usage_period', '')
    user_id = session.get('user_id')
    username = request.form.get('username')

    # Минимальная валидация
    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Текст отзыва не может быть пустым.'}), 400
        flash('Текст отзыва не может быть пустым.', 'error')
        return redirect(url_for('shop.product', product_id=product_id))

    if rating == 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Пожалуйста, поставьте оценку.'}), 400
        flash('Пожалуйста, поставьте оценку.', 'error')
        return redirect(url_for('shop.product', product_id=product_id))

    # Определяем имя пользователя
    actual_username = "Гость"
    if user_id:
        user = User.query.get(user_id)
        if user:
            actual_username = user.username
    elif username:
        actual_username = username
    
    # Проверяем, является ли покупка подтвержденной
    is_verified = check_verified_purchase(user_id, product_id)
    
    # Создаем новый отзыв
    review = Review(
        product_id=product_id,
        user_id=user_id,
        username=actual_username,
        rating=rating,
        title=title,
        content=content,
        pros=pros,
        cons=cons,
        usage_period=usage_period,
        is_verified_purchase=is_verified
    )
    
    try:
        db.session.add(review)
        db.session.flush()  # Получаем ID отзыва без коммита
        
        # Обрабатываем детальные оценки
        aspects = ['quality', 'price_value', 'usability', 'appearance']
        for aspect in aspects:
            aspect_rating = request.form.get(f'rating_{aspect}')
            if aspect_rating and aspect_rating.isdigit():
                detailed_rating = DetailedRating(
                    review_id=review.id,
                    aspect=aspect,
                    rating=int(aspect_rating)
                )
                db.session.add(detailed_rating)
        
        # Обрабатываем загрузку фотографий
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                filename = save_review_photo(photo)
                if filename:
                    review_photo = ReviewPhoto(
                        review_id=review.id,
                        filename=filename
                    )
                    db.session.add(review_photo)
        
        db.session.commit()
        
        # Для AJAX возвращаем JSON с новым отзывом
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'message': 'Ваш отзыв успешно добавлен!',
                'review': {
                    'id': review.id,
                    'username': review.username,
                    'rating': review.rating,
                    'title': review.title,
                    'content': review.content,
                    'pros': review.pros,
                    'cons': review.cons,
                    'formatted_date': review.formatted_date,
                    'user_id': review.user_id,
                    'is_verified_purchase': review.is_verified_purchase,
                    'has_photos': review.has_photos,
                    'photos': [{'filename': photo.filename} for photo in review.photos],
                    'avg_rating': product.avg_rating,
                    'total_ratings_count': product.total_ratings_count
                }
            })
        flash('Ваш отзыв успешно добавлен!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при добавлении отзыва: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Произошла ошибка при добавлении отзыва.'}), 500
        flash('Произошла ошибка при добавлении отзыва.', 'error')
    
    # Для не-AJAX запросов - редирект на страницу товара
    return redirect(url_for('shop.product', product_id=product_id))

@reviews_bp.route('/vote/<int:review_id>/<vote_type>', methods=['POST'])
def vote(review_id, vote_type):
    """Голосование за отзыв (лайк или дизлайк)"""
    review = Review.query.get_or_404(review_id)
    
    # Получаем информацию о пользователе
    user_id = session.get('user_id')
    ip_address = request.remote_addr
    
    # Проверяем, голосовал ли уже пользователь
    existing_vote = ReviewVote.query.filter(
        (ReviewVote.review_id == review_id) & 
        ((ReviewVote.user_id == user_id) if user_id else (ReviewVote.ip_address == ip_address))
    ).first()
    
    if existing_vote:
        # Если уже голосовал, меняем голос
        if existing_vote.vote_type == vote_type:
            # Если тот же голос, то отменяем его
            if vote_type == 'like':
                review.likes -= 1
            else:
                review.dislikes -= 1
            db.session.delete(existing_vote)
        else:
            # Если другой голос, то меняем тип
            if vote_type == 'like':
                review.likes += 1
                review.dislikes -= 1
            else:
                review.likes -= 1
                review.dislikes += 1
            existing_vote.vote_type = vote_type
    else:
        # Создаем новый голос
        vote = ReviewVote(
            review_id=review_id,
            user_id=user_id,
            ip_address=ip_address,
            vote_type=vote_type
        )
        # Обновляем счетчики
        if vote_type == 'like':
            review.likes += 1
        else:
            review.dislikes += 1
        db.session.add(vote)
    
    try:
        db.session.commit()
        return jsonify({
            'success': True, 
            'likes': review.likes, 
            'dislikes': review.dislikes
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при голосовании: {str(e)}")
        return jsonify({'success': False, 'error': 'Произошла ошибка при голосовании'})

@reviews_bp.route('/admin-response/<int:review_id>', methods=['POST'])
def admin_response(review_id):
    """Добавление ответа администратора на отзыв"""
    review = Review.query.get_or_404(review_id)
    
    # Проверяем, является ли пользователь администратором
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Необходима авторизация'})
        
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'success': False, 'error': 'Доступ запрещен'})
    
    # Получаем текст ответа
    response_text = request.form.get('response', '')
    
    # Обновляем отзыв
    review.admin_response = response_text
    review.admin_response_date = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'success': True, 
            'response': response_text,
            'date': review.admin_response_formatted_date
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при добавлении ответа администратора: {str(e)}")
        return jsonify({'success': False, 'error': 'Произошла ошибка при добавлении ответа'})

@reviews_bp.route('/product/<int:product_id>')
def product_reviews(product_id):
    """Получить все отзывы о товаре"""
    product = Product.query.get_or_404(product_id)
    
    # Параметры сортировки
    sort_by = request.args.get('sort', 'date')  # date, rating, likes
    order = request.args.get('order', 'desc')   # asc, desc
    
    # Формируем запрос в зависимости от параметров сортировки
    query = Review.query.filter_by(product_id=product_id)
    
    if sort_by == 'date':
        query = query.order_by(Review.created_at.desc() if order == 'desc' else Review.created_at)
    elif sort_by == 'rating':
        query = query.order_by(Review.rating.desc() if order == 'desc' else Review.rating)
    elif sort_by == 'likes':
        query = query.order_by(Review.likes.desc() if order == 'desc' else Review.likes)
    elif sort_by == 'dislikes':
        query = query.order_by(Review.dislikes.desc() if order == 'desc' else Review.dislikes)
    
    reviews = query.all()
    
    # Если это AJAX запрос, возвращаем только HTML шаблон
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('partials/reviews_list.html', reviews=reviews, product=product)
    
    return render_template('product_reviews.html', reviews=reviews, product=product)

@reviews_bp.route('/rate/<int:product_id>', methods=['POST'])
def rate_product(product_id):
    """Быстрая оценка товара без отзыва"""
    product = Product.query.get_or_404(product_id)
    
    # Получаем рейтинг из формы
    rating_value = int(request.form.get('rating', 5))
    if rating_value < 1 or rating_value > 5:
        return jsonify({'success': False, 'error': 'Некорректный рейтинг'})
    
    # Получаем информацию о пользователе
    user_id = session.get('user_id')
    ip_address = request.remote_addr
    
    # Проверяем, не оценивал ли уже пользователь этот товар
    existing_rating = Rating.query.filter(
        (Rating.product_id == product_id) & 
        ((Rating.user_id == user_id) if user_id else (Rating.ip_address == ip_address))
    ).first()
    
    if existing_rating:
        # Обновляем существующую оценку
        existing_rating.rating = rating_value
    else:
        # Создаем новую оценку
        new_rating = Rating(
            product_id=product_id,
            user_id=user_id,
            ip_address=ip_address,
            rating=rating_value
        )
        db.session.add(new_rating)
    
    try:
        db.session.commit()
        
        # Пересчитываем средний рейтинг товара
        avg_rating = product.avg_rating
        ratings_count = product.total_ratings_count
        
        return jsonify({
            'success': True,
            'avg_rating': avg_rating,
            'ratings_count': ratings_count
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при добавлении оценки: {str(e)}")
        return jsonify({'success': False, 'error': 'Произошла ошибка при сохранении оценки'})

# Добавляем новый маршрут для модального окна (без параметров в URL)
@reviews_bp.route('/add-modal', methods=['POST', 'GET'])
def add_review_modal():
    """Добавить отзыв о товаре из модального окна"""
    # Если это GET запрос, просто возвращаем сообщение
    if request.method == 'GET':
        # Возвращаем JSON с базовым успехом, чтобы не показывать ошибку Method Not Allowed
        return jsonify({
            'status': 'success', 
            'message': 'Метод GET поддерживается для тестирования соединения'
        })
    
    # Получаем ID товара из тела формы
    product_id = request.form.get('product_id')
    if not product_id:
        return jsonify({'status': 'error', 'message': 'ID товара не указан.'}), 400
    
    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Некорректный ID товара.'}), 400
    
    # Используем аналогичную логику из add_review
    product = Product.query.get_or_404(product_id)
    
    rating = int(request.form.get('rating', 0))
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    pros = request.form.get('pros', '')
    cons = request.form.get('cons', '')
    usage_period = request.form.get('usage_period', '')
    user_id = session.get('user_id')
    username = request.form.get('username')

    if not content:
        return jsonify({'status': 'error', 'message': 'Текст отзыва не может быть пустым.'}), 400

    if rating == 0:
        return jsonify({'status': 'error', 'message': 'Пожалуйста, поставьте оценку.'}), 400

    # Проверка имени для неавторизованных пользователей
    actual_username = None
    if user_id:
        user = User.query.get(user_id)
        if user:
            actual_username = user.username
    elif username:
        actual_username = username
    else:
        # Для гостей требуем имя
        return jsonify({'status': 'error', 'message': 'Пожалуйста, укажите ваше имя.'}), 400
    
    if not actual_username:
        actual_username = "Гость"
    
    # Проверяем, является ли покупка подтвержденной
    is_verified = check_verified_purchase(user_id, product_id)
    
    review = Review(
        product_id=product_id,
        user_id=user_id,
        username=actual_username,
        rating=rating,
        title=title,
        content=content,
        pros=pros,
        cons=cons,
        usage_period=usage_period,
        is_verified_purchase=is_verified
    )
    
    try:
        db.session.add(review)
        db.session.flush()
        
        # Обрабатываем детальные оценки
        aspects = ['quality', 'price_value', 'usability', 'appearance']
        for aspect in aspects:
            aspect_rating = request.form.get(f'rating_{aspect}')
            if aspect_rating and aspect_rating.isdigit():
                detailed_rating = DetailedRating(
                    review_id=review.id,
                    aspect=aspect,
                    rating=int(aspect_rating)
                )
                db.session.add(detailed_rating)
        
        # Обрабатываем загрузку фотографий из модального окна
        if 'photos' in request.files:
            photos = request.files.getlist('photos')
            for photo in photos:
                filename = save_review_photo(photo)
                if filename:
                    review_photo = ReviewPhoto(
                        review_id=review.id,
                        filename=filename
                    )
                    db.session.add(review_photo)
        
        db.session.commit()
        
        # Возвращаем JSON с данными нового отзыва
        return jsonify({
            'status': 'success',
            'message': 'Ваш отзыв успешно добавлен!',
            'review': {
                'id': review.id,
                'username': review.username,
                'rating': review.rating,
                'title': review.title,
                'content': review.content,
                'pros': review.pros,
                'cons': review.cons,
                'formatted_date': review.formatted_date,
                'user_id': review.user_id,
                'is_verified_purchase': review.is_verified_purchase,
                'has_photos': review.has_photos,
                'photos': [{'filename': photo.filename} for photo in review.photos]
            },
            'new_avg_rating': product.avg_rating,
            'new_total_ratings': product.total_ratings_count
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при добавлении отзыва из модального окна: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Произошла ошибка при добавлении отзыва.'}), 500

@reviews_bp.route('/helpful/<int:review_id>/<vote_type>', methods=['POST'])
def helpful_vote(review_id, vote_type):
    """Голосование за полезность отзыва (helpful/not_helpful)"""
    review = Review.query.get_or_404(review_id)
    
    # Получаем информацию о пользователе
    user_id = session.get('user_id')
    ip_address = request.remote_addr
    
    # Определяем тип голоса
    is_helpful = vote_type == 'helpful'
    
    # Проверяем, голосовал ли уже пользователь за полезность
    existing_vote = ReviewVote.query.filter(
        (ReviewVote.review_id == review_id) & 
        ((ReviewVote.user_id == user_id) if user_id else (ReviewVote.ip_address == ip_address)) &
        (ReviewVote.vote_type.in_(['helpful', 'not_helpful']))
    ).first()
    
    if existing_vote:
        # Если уже голосовал, обрабатываем изменение голоса
        if existing_vote.vote_type == vote_type:
            # Отменяем голос, если тот же тип
            if is_helpful:
                review.helpful_count = max(0, review.helpful_count - 1)
            else:
                review.not_helpful_count = max(0, review.not_helpful_count - 1)
            db.session.delete(existing_vote)
        else:
            # Меняем тип голоса
            existing_vote.vote_type = vote_type
            if is_helpful:
                review.helpful_count += 1
                review.not_helpful_count = max(0, review.not_helpful_count - 1)
            else:
                review.not_helpful_count += 1
                review.helpful_count = max(0, review.helpful_count - 1)
    else:
        # Создаем новый голос
        vote = ReviewVote(
            review_id=review_id,
            user_id=user_id,
            ip_address=ip_address,
            vote_type=vote_type
        )
        # Обновляем счетчики
        if is_helpful:
            review.helpful_count += 1
        else:
            review.not_helpful_count += 1
        db.session.add(vote)
    
    try:
        db.session.commit()
        return jsonify({
            'success': True, 
            'helpful_count': review.helpful_count, 
            'not_helpful_count': review.not_helpful_count
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при голосовании за полезность: {str(e)}")
        return jsonify({'success': False, 'error': 'Произошла ошибка при голосовании'}) 