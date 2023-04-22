import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Pets(SqlAlchemyBase):
    __tablename__ = 'pets'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    feed = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    sleep = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    happiness = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    birthday = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship('User')