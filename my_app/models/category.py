"""
Модели категорий товаров
"""
from my_app.extensions import db

class CategorySpecificationTemplate(db.Model):
    """Модель шаблона характеристик для категории"""
    __tablename__ = 'category_spec_templates'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Название характеристики
    description = db.Column(db.String(255), nullable=True)  # Описание характеристики
    required = db.Column(db.Boolean, default=False)  # Обязательна ли характеристика

    def __repr__(self):
        return f'<CategorySpecTemplate {self.name}>'

class Category(db.Model):
    """Модель категории товаров"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    image = db.Column(db.String(255), nullable=True)

    # Связи
    products = db.relationship('Product', backref='category', lazy=True)
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy=True)
    specification_templates = db.relationship('CategorySpecificationTemplate', backref='category', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>' 