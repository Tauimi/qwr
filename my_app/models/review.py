"""
Модель отзывов о товарах
"""
from datetime import datetime
from my_app.extensions import db

class ReviewPhoto(db.Model):
    """Модель для хранения фотографий к отзывам"""
    __tablename__ = 'review_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    review = db.relationship('Review', backref=db.backref('photos', lazy=True, cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f'<ReviewPhoto {self.id} for review {self.review_id}>'

class DetailedRating(db.Model):
    """Модель для детальных оценок различных аспектов товара"""
    __tablename__ = 'detailed_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    aspect = db.Column(db.String(50), nullable=False)  # Например: 'quality', 'price_value', 'usability'
    rating = db.Column(db.Integer, nullable=False)  # От 1 до 5
    
    review = db.relationship('Review', backref=db.backref('detailed_ratings', lazy=True, cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f'<DetailedRating {self.aspect}: {self.rating} for review {self.review_id}>'

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
    
    # Новые поля
    helpful_count = db.Column(db.Integer, default=0)  # Счетчик полезности отзыва
    not_helpful_count = db.Column(db.Integer, default=0)  # Счетчик бесполезности отзыва
    is_verified_purchase = db.Column(db.Boolean, default=False)  # Подтвержденная покупка
    pros = db.Column(db.Text)  # Достоинства товара
    cons = db.Column(db.Text)  # Недостатки товара
    usage_period = db.Column(db.String(50))  # Период использования товара
    
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

    @property
    def has_photos(self):
        """Проверяет, есть ли у отзыва фотографии"""
        return len(self.photos) > 0

    @property
    def avg_detailed_rating(self):
        """Возвращает среднюю детальную оценку"""
        if not self.detailed_ratings:
            return self.rating
        
        total = sum(dr.rating for dr in self.detailed_ratings)
        return round(total / len(self.detailed_ratings), 1)
