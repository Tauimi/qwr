"""
Blueprint для отзывов о товарах
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask import session, g
from my_app.extensions import db
from my_app.models import Review, ReviewVote, Product, User, Rating
from datetime import datetime

# Создаем Blueprint
reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@reviews_bp.route('/add/<int:product_id>', methods=['POST'])
def add_review(product_id):
    """Добавить отзыв о товаре"""
    product = Product.query.get_or_404(product_id)
    
    # Получаем данные из формы
    rating = int(request.form.get('rating', 5))
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    username = request.form.get('username', 'Гость')
    
    # Проверяем, авторизован ли пользователь
    user_id = session.get('user_id')
    
    # Создаем новый отзыв
    review = Review(
        product_id=product_id,
        user_id=user_id,
        username=username,
        rating=rating,
        title=title,
        content=content
    )
    
    try:
        db.session.add(review)
        db.session.commit()
        flash('Ваш отзыв успешно добавлен!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при добавлении отзыва: {str(e)}")
        flash('Произошла ошибка при добавлении отзыва.', 'error')
    
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