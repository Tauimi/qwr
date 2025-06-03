from datetime import datetime
from my_app.extensions import db

class FeedbackMessage(db.Model):
    """Модель для сообщений обратной связи"""
    __tablename__ = 'feedback_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<FeedbackMessage {self.id}: {self.subject}>'

class Review(db.Model):
    """Модель отзывов о товарах"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(100), nullable=False)  # Для неавторизованных пользователей
    rating = db.Column(db.Integer, nullable=False)  # От 1 до 5 звезд
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    
    # Связи с другими моделями
    product = db.relationship('Product', backref=db.backref('reviews', lazy=True))
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    
    # Ответы администратора на отзывы
    admin_response = db.Column(db.Text)
    admin_response_date = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Review {self.id}: {self.rating} stars>'
        
    @property
    def formatted_date(self):
        """Возвращает отформатированную дату создания"""
        return self.created_at.strftime('%d.%m.%Y %H:%M')
        
    @property
    def admin_response_formatted_date(self):
        """Возвращает отформатированную дату ответа администратора"""
        if self.admin_response_date:
            return self.admin_response_date.strftime('%d.%m.%Y %H:%M')
        return None
        
# Модель для хранения лайков/дизлайков от пользователей
class ReviewVote(db.Model):
    """Модель для хранения голосов за отзывы"""
    __tablename__ = 'review_votes'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(50))  # Для неавторизованных пользователей
    vote_type = db.Column(db.String(10), nullable=False)  # 'like' или 'dislike'
    
    # Связи с другими моделями
    review = db.relationship('Review', backref=db.backref('votes', lazy=True))
    user = db.relationship('User', backref=db.backref('review_votes', lazy=True))
    
    def __repr__(self):
        return f'<ReviewVote {self.id}: {self.vote_type}>'

class Rating(db.Model):
    """Модель для оценок товаров без отзыва"""
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(50))  # Для неавторизованных пользователей
    rating = db.Column(db.Integer, nullable=False)  # От 1 до 5 звезд
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи с другими моделями
    product = db.relationship('Product', backref=db.backref('ratings', lazy=True))
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))
    
    def __repr__(self):
        return f'<Rating {self.id}: {self.rating} stars>'

class Product(db.Model):
    """Модель товара"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи с другими моделями
    reviews = db.relationship('Review', backref='product', lazy=True)
    ratings = db.relationship('Rating', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.id}: {self.name}>'

    @property
    def avg_rating(self):
        """Рассчитывает средний рейтинг товара с учетом отзывов и простых оценок"""
        from sqlalchemy import func
        
        # Сумма и количество оценок из обычных отзывов
        reviews_rating = db.session.query(
            func.avg(Review.rating), func.count(Review.id)
        ).filter(Review.product_id == self.id).first()
        
        # Сумма и количество быстрых оценок
        ratings_rating = db.session.query(
            func.avg(Rating.rating), func.count(Rating.id)
        ).filter(Rating.product_id == self.id).first()
        
        # Получаем значения из результатов запроса
        reviews_avg = reviews_rating[0] or 0
        reviews_count = reviews_rating[1] or 0
        ratings_avg = ratings_rating[0] or 0
        ratings_count = ratings_rating[1] or 0
        
        # Если нет ни одной оценки, возвращаем 0
        if reviews_count + ratings_count == 0:
            return 0
        
        # Рассчитываем средневзвешенное значение рейтинга
        total_avg = (reviews_avg * reviews_count + ratings_avg * ratings_count) / (reviews_count + ratings_count)
        return round(total_avg, 1)
    
    @property
    def total_ratings_count(self):
        """Возвращает общее количество оценок (отзывы + быстрые оценки)"""
        from sqlalchemy import func
        
        reviews_count = db.session.query(func.count(Review.id)).filter(Review.product_id == self.id).scalar() or 0
        ratings_count = db.session.query(func.count(Rating.id)).filter(Rating.product_id == self.id).scalar() or 0
        
        return reviews_count + ratings_count 