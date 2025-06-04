#!/usr/bin/env python
"""
Скрипт для заполнения базы данных тестовыми категориями и товарами
Подходит для Railway и Replit
"""
import os
import random
import string
from slugify import slugify
from my_app import create_app
from my_app.extensions import db
from my_app.models import Category, Product, Specification

# Создаем экземпляр приложения
app = create_app(os.getenv('APP_SETTINGS', 'development'))

# Данные для наполнения
CATEGORIES = [
    {
        "name": "Смартфоны и гаджеты",
        "description": "Мобильные устройства и аксессуары",
        "subcategories": [
            {
                "name": "Смартфоны",
                "description": "Мобильные телефоны с сенсорным экраном",
            },
            {
                "name": "Планшеты",
                "description": "Портативные устройства с большим экраном",
            },
            {
                "name": "Умные часы",
                "description": "Носимые устройства с различными функциями",
            }
        ]
    },
    {
        "name": "Компьютеры",
        "description": "Настольные компьютеры, ноутбуки и комплектующие",
        "subcategories": [
            {
                "name": "Ноутбуки",
                "description": "Портативные компьютеры для работы и развлечений",
            },
            {
                "name": "Настольные ПК",
                "description": "Стационарные компьютеры для дома и офиса",
            },
            {
                "name": "Комплектующие",
                "description": "Детали и запчасти для компьютеров",
            }
        ]
    },
    {
        "name": "Техника для дома",
        "description": "Бытовая техника для комфортной жизни",
        "subcategories": [
            {
                "name": "Пылесосы",
                "description": "Устройства для уборки помещений",
            },
            {
                "name": "Стиральные машины",
                "description": "Техника для стирки белья",
            },
            {
                "name": "Холодильники",
                "description": "Техника для хранения продуктов",
            }
        ]
    }
]

# Словари с характеристиками для разных категорий
SMARTPHONE_SPECS = {
    "Процессор": ["Snapdragon 8 Gen 2", "Apple A16 Bionic", "Exynos 2200", "MediaTek Dimensity 9000"],
    "Оперативная память": ["4 ГБ", "6 ГБ", "8 ГБ", "12 ГБ", "16 ГБ"],
    "Встроенная память": ["64 ГБ", "128 ГБ", "256 ГБ", "512 ГБ", "1 TБ"],
    "Экран": ["AMOLED 6.1\"", "OLED 6.7\"", "IPS 6.5\"", "Dynamic AMOLED 6.8\""],
    "Основная камера": ["12 МП", "48 МП", "50 МП", "108 МП"],
    "Фронтальная камера": ["8 МП", "12 МП", "16 МП", "40 МП"],
    "Аккумулятор": ["3500 мАч", "4000 мАч", "4500 мАч", "5000 мАч"]
}

LAPTOP_SPECS = {
    "Процессор": ["Intel Core i5-12500H", "AMD Ryzen 7 5800H", "Apple M2", "Intel Core i7-13700H"],
    "Оперативная память": ["8 ГБ", "16 ГБ", "32 ГБ", "64 ГБ"],
    "Накопитель": ["SSD 256 ГБ", "SSD 512 ГБ", "SSD 1 ТБ", "SSD 2 ТБ"],
    "Видеокарта": ["Встроенная", "NVIDIA RTX 3050", "NVIDIA RTX 3060", "AMD Radeon RX 6700M"],
    "Экран": ["14\" IPS Full HD", "15.6\" OLED 2K", "16\" Mini-LED", "17.3\" IPS Full HD"],
    "Вес": ["1.2 кг", "1.5 кг", "1.8 кг", "2.3 кг"]
}

TABLET_SPECS = {
    "Процессор": ["Apple A14 Bionic", "Snapdragon 870", "MediaTek Helio G99", "Exynos 1380"],
    "Экран": ["10.2\" IPS", "10.9\" Liquid Retina", "11\" AMOLED", "12.9\" Mini-LED"],
    "Оперативная память": ["3 ГБ", "4 ГБ", "6 ГБ", "8 ГБ"],
    "Встроенная память": ["32 ГБ", "64 ГБ", "128 ГБ", "256 ГБ"],
    "Аккумулятор": ["7000 мАч", "8000 мАч", "9000 мАч", "10000 мАч"]
}

VACUUM_SPECS = {
    "Тип уборки": ["Сухая", "Влажная", "Комбинированная"],
    "Мощность всасывания": ["250 Вт", "350 Вт", "450 Вт", "550 Вт"],
    "Тип пылесборника": ["Мешок", "Контейнер", "Аквафильтр"],
    "Уровень шума": ["65 дБ", "70 дБ", "75 дБ", "80 дБ"],
    "Вес": ["2.5 кг", "3 кг", "4 кг", "5 кг"]
}

REFRIGERATOR_SPECS = {
    "Тип": ["Однокамерный", "Двухкамерный", "Side-by-side", "Многодверный"],
    "Общий объем": ["200 л", "300 л", "400 л", "500 л", "600 л"],
    "Класс энергопотребления": ["A", "A+", "A++", "A+++"],
    "Система размораживания": ["Ручная", "Капельная", "No Frost"],
    "Количество полок": ["3", "4", "5", "6"]
}

WASHING_MACHINE_SPECS = {
    "Загрузка": ["5 кг", "6 кг", "7 кг", "8 кг", "10 кг"],
    "Максимальная скорость отжима": ["800 об/мин", "1000 об/мин", "1200 об/мин", "1400 об/мин"],
    "Класс энергопотребления": ["A", "A+", "A++", "A+++"],
    "Количество программ": ["8", "12", "16", "20"],
    "Тип управления": ["Механическое", "Электронное", "Сенсорное"]
}

# Соответствие категорий и спецификаций
CATEGORY_SPECS_MAP = {
    "Смартфоны": SMARTPHONE_SPECS,
    "Планшеты": TABLET_SPECS,
    "Ноутбуки": LAPTOP_SPECS,
    "Пылесосы": VACUUM_SPECS,
    "Холодильники": REFRIGERATOR_SPECS,
    "Стиральные машины": WASHING_MACHINE_SPECS
}

# Генерация случайного SKU
def generate_sku(prefix="TM", length=8):
    """Генерирует случайный SKU-код товара"""
    chars = string.ascii_uppercase + string.digits
    return f"{prefix}-{''.join(random.choice(chars) for _ in range(length))}"

def seed_db():
    """Заполняет базу данных тестовыми данными"""
    with app.app_context():
        print("Начинаем заполнение базы данных...")
        # Проверяем, существуют ли таблицы. Если нет, создаем их.
        # Это важно для Railway, где миграции могут не всегда запускаться автоматически перед seed-ом.
        try:
            # Попытка получить данные из одной из таблиц, чтобы проверить ее существование
            # Например, из таблицы Category
            Category.query.first()
        except Exception as e:
            print(f"Таблицы базы данных не найдены. Создаем таблицы: {e}")
            db.create_all()
            print("Таблицы успешно созданы.")
        
        # Проверяем, есть ли уже данные в базе
        existing_categories = Category.query.count()
        if existing_categories > 0:
            print(f"База данных уже содержит {existing_categories} категорий. Пропускаем заполнение.")
            return False

        # Создаем категории и подкатегории
        for category_data in CATEGORIES:
            # Проверяем, существует ли категория с таким slug
            slug = slugify(category_data["name"])
            existing_category = Category.query.filter_by(slug=slug).first()
            
            if existing_category:
                print(f"Категория с slug '{slug}' уже существует. Пропускаем.")
                category = existing_category
            else:
                category = Category(
                    name=category_data["name"],
                    slug=slug,
                    description=category_data["description"]
                )
                db.session.add(category)
                try:
                    db.session.commit()
                    print(f"Создана категория: {category.name}")
                except Exception as e:
                    db.session.rollback()
                    print(f"Ошибка при создании категории {category.name}: {e}")
                    continue

            # Добавляем подкатегории
            for subcategory_data in category_data["subcategories"]:
                # Проверяем, существует ли подкатегория с таким slug
                subcategory_slug = slugify(subcategory_data["name"])
                existing_subcategory = Category.query.filter_by(slug=subcategory_slug).first()
                
                if existing_subcategory:
                    print(f"  - Подкатегория с slug '{subcategory_slug}' уже существует. Пропускаем.")
                    subcategory = existing_subcategory
                else:
                    subcategory = Category(
                        name=subcategory_data["name"],
                        slug=subcategory_slug,
                        description=subcategory_data["description"],
                        parent_id=category.id
                    )
                    db.session.add(subcategory)
                    try:
                        db.session.commit()
                        print(f"  - Создана подкатегория: {subcategory.name}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"  - Ошибка при создании подкатегории {subcategory.name}: {e}")
                        continue

                # Генерируем товары для подкатегории
                num_products = random.randint(5, 15)  # Случайное количество товаров от 5 до 15

                for i in range(num_products):
                    # Выбираем названия товаров в зависимости от категории
                    if subcategory.name == "Смартфоны":
                        brands = ["Samsung Galaxy", "Apple iPhone", "Xiaomi Redmi", "Google Pixel", "OnePlus"]
                        model_suffix = ["Pro", "Ultra", "Plus", "Lite", "Max", ""]
                        product_name = f"{random.choice(brands)} {random.randint(10, 20)} {random.choice(model_suffix)}"
                    elif subcategory.name == "Планшеты":
                        brands = ["Apple iPad", "Samsung Galaxy Tab", "Lenovo Tab", "Xiaomi Pad", "Huawei MatePad"]
                        product_name = f"{random.choice(brands)} {random.randint(5, 11)} {random.choice(['Pro', 'Air', 'Lite', ''])}"
                    elif subcategory.name == "Ноутбуки":
                        brands = ["Apple MacBook", "Dell XPS", "HP Spectre", "Lenovo ThinkPad", "ASUS ZenBook", "Acer Swift"]
                        product_name = f"{random.choice(brands)} {random.choice(['Pro', 'Air', 'X', 'Ultra', 'Plus'])} {random.randint(13, 17)}"
                    elif subcategory.name == "Пылесосы":
                        brands = ["Dyson", "Samsung", "Xiaomi", "Philips", "LG", "Bosch"]
                        product_name = f"{random.choice(brands)} {random.choice(['PowerClean', 'TurboSuction', 'UltraVac', 'EcoClean', 'SmartVac'])} {random.randint(1, 9)}000"
                    elif subcategory.name == "Холодильники":
                        brands = ["LG", "Samsung", "Bosch", "Liebherr", "Haier", "Indesit"]
                        product_name = f"{random.choice(brands)} {random.choice(['FreshCold', 'IceMax', 'NoFrost', 'SmartCool', 'CrystalFreeze'])} {random.randint(100, 999)}"
                    elif subcategory.name == "Стиральные машины":
                        brands = ["Bosch", "LG", "Samsung", "Electrolux", "Siemens", "Whirlpool"]
                        product_name = f"{random.choice(brands)} {random.choice(['WashPro', 'CleanMaster', 'EcoBubble', 'PerfectWash', 'AquaControl'])} {random.randint(5, 12)}000"
                    else:
                        product_name = f"Товар {subcategory.name} #{i+1}"

                    # Генерируем цены
                    price = round(random.uniform(1000, 150000), -1)  # Цена от 1000 до 150000 с округлением до десятков
                    is_sale = random.choice([True, False])
                    old_price = round(price * random.uniform(1.1, 1.5), -1) if is_sale else None  # Старая цена на 10-50% выше

                    # Создаем базовый slug и проверяем его уникальность
                    base_slug = slugify(product_name)
                    unique_slug = base_slug

                    # Проверяем существует ли товар с таким slug
                    existing_product = Product.query.filter_by(slug=unique_slug).first()

                    # Если существует, добавляем короткий случайный суффикс
                    if existing_product:
                        print(f"    * Товар с slug '{unique_slug}' уже существует. Создаем уникальный slug.")
                        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                        unique_slug = f"{base_slug}-{suffix}"

                    # Создаем объект товара и добавляем его в базу данных
                    product = Product(
                        name=product_name,
                        slug=unique_slug,
                        sku=generate_sku(),
                        description=f"Подробное описание товара {product_name}. Здесь могут быть перечислены особенности, преимущества и технические характеристики.",
                        price=price,
                        old_price=old_price,
                        stock=random.randint(0, 50),
                        category_id=subcategory.id,
                        is_featured=random.choice([True, False]),
                        is_new=random.choice([True, False]),
                        is_sale=is_sale
                    )

                    db.session.add(product)
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(f"    * Ошибка при создании товара {product_name}: {e}")
                        continue

                    # Добавляем характеристики товара
                    if subcategory.name in CATEGORY_SPECS_MAP:
                        specs = CATEGORY_SPECS_MAP[subcategory.name]
                        for spec_name, spec_values in specs.items():
                            spec = Specification(
                                product_id=product.id,
                                name=spec_name,
                                value=random.choice(spec_values)
                            )
                            db.session.add(spec)
                        
                        try:
                            db.session.commit()
                            print(f"    * Создан товар: {product.name} - {product.price} руб.")
                        except Exception as e:
                            db.session.rollback()
                            print(f"    * Ошибка при добавлении характеристик для товара {product.name}: {e}")

        print("База данных успешно заполнена!")
        return True


if __name__ == "__main__":
    seed_db()