
"""
Модель для оценок товаров без отзыва
"""
from datetime import datetime
from my_app.extensions import db

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
