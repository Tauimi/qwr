"""
Модели заказов
"""
from datetime import datetime
from my_app.extensions import db

# Таблица для связи многие-ко-многим между Product и Order
order_items = db.Table('order_items',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('quantity', db.Integer, default=1),
    db.Column('price', db.Float)
)

class Order(db.Model):
    """Модель заказа"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(50), default='pending')
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    shipping_method = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    items = db.relationship('Product', secondary=order_items, lazy='subquery',
                           backref=db.backref('orders', lazy='dynamic'))
    
    def get_items_with_quantities(self):
        """Возвращает товары с их количеством и ценой"""
        result = []
        for item in db.session.query(order_items).filter_by(order_id=self.id).all():
            product = db.session.query(db.models.Product).get(item.product_id)
            if product:
                result.append({
                    'product': product,
                    'quantity': item.quantity,
                    'price': item.price
                })
        return result
        
    def __repr__(self):
        return f'<Order {self.id}>' 