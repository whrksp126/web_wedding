from sqlalchemy import Column, Integer, BigInteger, String, Text, Date, Time, DateTime, ForeignKey, Float
from werkzeug.security import generate_password_hash

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.sql import func
  
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.types import TypeDecorator

from app.config import DATABASE_HOST, DATABASE_DB, DATABASE_PORT, DATABASE_PASSWORD, DATABASE_USER

import json
import enum
import datetime

url = 'mysql://{}:{}@{}:{}/{}'.format(
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_DB
)
  
engine = create_engine(url, echo=False, connect_args={'charset': 'utf8'}, pool_pre_ping=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()



class Template(Base):
    __tablename__ = 'template'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(256), nullable=True)

    def __init__(self, name, description):
        self.name = name
        self.description = description


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    user_id = Column(String(512), nullable=False, unique=True)
    user_pw = Column(String(512), nullable=False)
    email = Column(String(512), nullable=False, unique=True)
    guestbook_pw = Column(String(512), nullable=False, default='0000')

    def __init__(self, name, user_id, user_pw, email):
        from app import bcrypt

        self.name = name
        self.user_id = user_id
        self.user_pw = bcrypt.hashpw(user_pw.encode('utf-8'), bcrypt.gensalt())
        self.email = email


class UserHasTemplate(Base):
    __tablename__ = 'user_has_template'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('template.id'), nullable=False)

    def __init__(self, user_id, template_id):
        self.user_id = user_id
        self.template_id = template_id


class Relation(Base):
    __tablename__ = 'relation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    relation = Column(String(50), nullable=False)

    def __init__(self, relation):
        self.relation = relation


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    acc_bank = Column(String(50), nullable=False)
    acc_number = Column(String(50), nullable=False)
    acc_name = Column(String(50), nullable=False)
    usertemplate_id = Column(Integer, ForeignKey('user_has_template.id'), nullable=False)
    relation_id = Column(Integer, ForeignKey('relation.id'), nullable=False)

    def __init__(self, acc_bank, acc_number, acc_name, usertemplate_id, relation_id):
        self.acc_bank = acc_bank
        self.acc_number = acc_number
        self.acc_name = acc_name
        self.usertemplate_id = usertemplate_id
        self.relation_id = relation_id


class Guestbook(Base):
    __tablename__ = 'guest_book'
    id = Column(Integer, primary_key=True, autoincrement=True)
    writer = Column(String(50), nullable=False)
    writer_pw = Column(String(50), nullable=False)
    contents = Column(Text, nullable=False)
    usertemplate_id = Column(Integer, ForeignKey('user_has_template.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now())

    def __init__(self, writer, writer_pw, contents, usertemplate_id):
        self.writer = writer
        self.writer_pw = writer_pw
        self.contents = contents
        self.usertemplate_id = usertemplate_id


class Information(Base):
    __tablename__ = 'information'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    tel = Column(String(50), nullable=True)
    usertemplate_id = Column(Integer, ForeignKey('user_has_template.id'), nullable=False)
    relation_id = Column(Integer, ForeignKey('relation.id'), nullable=False)

    def __init__(self, first_name, last_name, tel, usertemplate_id, relation_id):
        self.first_name = first_name
        self.last_name = last_name
        self.tel = tel
        self.usertemplate_id = usertemplate_id
        self.relation_id = relation_id


class Picturetype(Base):
    __tablename__ = 'picture_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __init__(self, name):
        self.name = name


class Picture(Base):
    __tablename__ = 'picture'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(512), nullable=False)
    usertemplate_id = Column(Integer, ForeignKey('user_has_template.id'), nullable=False)
    picture_type = Column(Integer, ForeignKey('picture.id'), nullable=False)
    priority = Column(Integer, nullable=True)

    def __init__(self, url, usertemplate_id, picture_type, priority):
        self.url = url
        self.usertemplate_id = usertemplate_id
        self.picture_type = picture_type
        self.priority = priority


class Texttype(Base):
    __tablename__ = 'text_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __init__(self, name):
        self.name = name


class Textlist(Base):
    __tablename__ = 'text_list'
    id = Column(Integer, primary_key=True, autoincrement=True)
    contents = Column(Text, nullable=False)
    usertemplate_id = Column(Integer, ForeignKey('user_has_template.id'), nullable=False)
    text_type = Column(Integer, ForeignKey('text_type.id'), nullable=False)

    def __init__(self, contents, usertemplate_id, text_type):
        self.contents = contents
        self.usertemplate_id = usertemplate_id
        self.text_type = text_type


class Transportationtype(Base):
    __tablename__ = 'transportation_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __init__(self, name):
        self.name = name


class Transportation(Base):
    __tablename__ = 'transportation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    contents = Column(Text, nullable=False)
    usertemplate_id = Column(Integer, ForeignKey('user_has_template.id'), nullable=False)
    transportation_type = Column(Integer, ForeignKey('transportation_type.id'), nullable=False)

    def __init__(self, contents, usertemplate_id, transportation_type):
        self.contents = contents
        self.usertemplate_id = usertemplate_id
        self.transportation_type = transportation_type


class Weddinghall(Base):
    __tablename__ = 'wedding_hall'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    address = Column(String(256), nullable=False, unique=True)
    address_detail = Column(String(256), nullable=False, unique=True)
    date = Column(Date, nullable=False)
    time = Column(String(128), nullable=False)
    usertemplate_id = Column(Integer, ForeignKey('user_has_template.id'), default=None)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    def __init__(self, name, address, address_detail, date, time, usertemplate_id, lat, lng):
        self.name = name
        self.address = address
        self.address_detail = address_detail
        self.date = date
        self.time = time
        self.usertemplate_id = usertemplate_id
        self.lat = lat
        self.lng = lng


Base.metadata.create_all(engine)