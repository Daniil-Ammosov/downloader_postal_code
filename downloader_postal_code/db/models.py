# coding: utf-8

import datetime

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class Release(Base):
    """
    Таблица для сохранения даты последнего релиза архива ФИАС
    """
    __tablename__ = "release"
    id = sa.Column(sa.Integer(), primary_key=True)
    version = sa.Column(sa.Integer(), nullable=False)
