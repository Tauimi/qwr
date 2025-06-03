"""
Модели данных приложения
"""
# Импорт моделей для упрощения доступа
from .user import User
from .product import Product, Specification
from .category import Category, CategorySpecificationTemplate
from .order import Order, order_items
from .visitor import Visitor
from .review import Review
from .review_vote import ReviewVote
from .rating import Rating
from .feedback import FeedbackMessage