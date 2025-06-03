
"""
Модель отзывов о товарах
"""
from datetime import datetime
from my_app.extensions import db

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
