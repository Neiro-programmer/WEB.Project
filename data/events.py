import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, Enum
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Event(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'events'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    starting_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now)
    ending_time = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    contact = sqlalchemy.Column(sqlalchemy.String, default='Нет информации о способах связи')
    telegram = sqlalchemy.Column(sqlalchemy.String, default='Нет информации о тг')
    file = sqlalchemy.Column(sqlalchemy.String, default='../static/img/default.png')
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    category = sqlalchemy.Column(
        Enum('Все', 'Спорт', 'Музыка', 'Искусство', 'Общение', 'Психология', 'Игры', 'Дегустация',
             name='event_category'), nullable=False, default=0)
    location = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user = orm.relationship('User')
