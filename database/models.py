from datetime import datetime
from typing import Optional

import aio_pika
import sqlalchemy as sa

from database.controller import DbController
from database.db_core import Base
from utils.types import (
    IntColumnType,
    StrColumnType,
    BoolColumnType,
    DateTimeColumnType,
)


class UserRole:
    ACCOUNTANT = 1
    WORKER = 2
    SERVICE = 3


class User(Base, DbController):
    __tablename__ = 'users'

    id: IntColumnType = sa.Column(sa.Integer(), primary_key=True)
    telegram_id: IntColumnType = sa.Column(sa.Integer(), nullable=False, unique=True)
    username: StrColumnType = sa.Column(sa.String(), nullable=False)
    role_id: IntColumnType = sa.Column(sa.Integer(), sa.ForeignKey("user_roles.id"), nullable=False)
    is_deleted: BoolColumnType = sa.Column(sa.Boolean(), nullable=False, default=False)

    @staticmethod
    async def get_by_telegram_id(telegram_user_id: int) -> Optional['User']:
        return await User.get(telegram_id=telegram_user_id, is_deleted=False)


class OrderStatus(Base, DbController):
    __tablename__ = 'order_statuses'

    NEW = 1
    PROCESSING = 2
    READY = 3
    DONE = 4
    DECLINED = 5

    id: IntColumnType = sa.Column(sa.Integer(), primary_key=True)
    name: StrColumnType = sa.Column(sa.String, nullable=False, unique=True)

    @staticmethod
    def get_str_by_id(order_id: int) -> str | None:
        return {
            1: 'Новая',
            2: 'Обрабатывается',
            3: 'Готова к выдачи',
            4: 'Выполнена',
            5: 'Отменена',
        }.get(order_id)


class Document(Base, DbController):
    __tablename__ = 'documents'

    id: IntColumnType = sa.Column(sa.Integer(), primary_key=True)
    name: StrColumnType = sa.Column(sa.String(), nullable=False, unique=True)
    is_deleted: BoolColumnType = sa.Column(sa.Boolean(), nullable=False, default=False)


class Order(Base, DbController):
    __tablename__ = 'orders'

    id: IntColumnType = sa.Column(sa.Integer(), primary_key=True)
    document_id: IntColumnType = sa.Column(sa.Integer(), sa.ForeignKey(Document.id), nullable=False)
    sender_id: IntColumnType = sa.Column(sa.Integer(), sa.ForeignKey(User.id), nullable=False)
    receiver_id: IntColumnType = sa.Column(sa.Integer(), sa.ForeignKey(User.id), nullable=False)
    status_id: int | sa.Column = sa.Column(sa.Integer(), sa.ForeignKey(OrderStatus.id), nullable=False)
    created_at: DateTimeColumnType = sa.Column(sa.DateTime(), default=datetime.now, nullable=False)
    status_changed_at: DateTimeColumnType = sa.Column(sa.DateTime())


class Cell(Base, DbController):
    __tablename__ = 'cells'

    id: IntColumnType = sa.Column(sa.Integer(), primary_key=True)
    order_id: IntColumnType = sa.Column(sa.Integer(), sa.ForeignKey(Order.id))
    is_open: BoolColumnType = sa.Column(sa.Boolean(), nullable=False, default=False)
