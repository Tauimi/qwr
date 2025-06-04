"""Обновление системы отзывов

Revision ID: reviews_update
Revises: 
Create Date: 2023-07-10 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'reviews_update'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем новые поля в таблицу отзывов
    op.add_column('reviews', sa.Column('helpful_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('reviews', sa.Column('not_helpful_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('reviews', sa.Column('is_verified_purchase', sa.Boolean(), nullable=True, server_default='0'))
    op.add_column('reviews', sa.Column('pros', sa.Text(), nullable=True))
    op.add_column('reviews', sa.Column('cons', sa.Text(), nullable=True))
    op.add_column('reviews', sa.Column('usage_period', sa.String(50), nullable=True))
    
    # Создаем таблицу для фотографий отзывов
    op.create_table(
        'review_photos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('upload_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу для детальных оценок
    op.create_table(
        'detailed_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('aspect', sa.String(50), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Удаляем таблицы
    op.drop_table('detailed_ratings')
    op.drop_table('review_photos')
    
    # Удаляем новые поля из таблицы отзывов
    op.drop_column('reviews', 'usage_period')
    op.drop_column('reviews', 'cons')
    op.drop_column('reviews', 'pros')
    op.drop_column('reviews', 'is_verified_purchase')
    op.drop_column('reviews', 'not_helpful_count')
    op.drop_column('reviews', 'helpful_count') 