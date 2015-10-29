# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 17:04:18 2015

@author: sergey
"""

import datetime
import json
import sys
import time
import base64
import re
import sqlalchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
from sqlalchemy import or_, and_, desc
from configurations import sql_uri, def_industry, persons
import uuid
import logging

reload(sys)
sys.setdefaultencoding("utf-8")


"""
Подключение БД
"""
Base = sqlalchemy.ext.declarative.declarative_base()
Engine = sqlalchemy.create_engine(sql_uri, pool_size=20)
Session = sqlalchemy.orm.sessionmaker(bind=Engine)


"""
Логирование сообщений приложения в файл
"""
logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG,
                    filename="app_log.log")


def add_to_log(message, msg_type=None):
    if msg_type == "w":
        logging.warning(message)
    else:
        logging.critical(message)


def create_tables():
    """
    Функция пересоздания таблиц  базе данных MySQL.

    Все таблицы пересоздаются согласно объявлению классов наследованных от Base. Если таблица в БД существует,
    то ничего не происходит.

    :return: нет
    """

    Base.metadata.create_all(Engine)


class User(Base):
    """
    Класс для работы с объектами Пользователей системы.

    Список свойств класса:

    :parameter id: sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    :parameter uuid: идентифкатор (sqlalchemy.Column(sqlalchemy.String(50), default=uuid.uuid1()))
    :parameter name: имя пользователя (sqlalchemy.Column(sqlalchemy.String(256)))
    :parameter surname: фамилия пользователя (sqlalchemy.Column(sqlalchemy.String(256)))
    :parameter login: логин пользователя (sqlalchemy.Column(sqlalchemy.String(50)))
    :parameter password: пароль пользователя (sqlalchemy.Column(sqlalchemy.String(20)))
    :parameter disabled: индикатор использования аккаунта пользователя(0 - используется, 1 - отключен \
    (sqlalchemy.Column(sqlalchemy.Integer))
    :parameter access_groups: список групп доступа в которые входит пользователь

    """

    EDIT_FIELDS = ['name', 'surname', 'password']
    ALL_FIELDS = {'name': 'Имя', 'surname': 'Фамилия',
                  'login': 'Логин', 'password': 'Пароль',
                  'id': 'id', 'uuid': 'uuid',
                  'access_groups': 'Группы доступа'}
    VIEW_FIELDS = ['name', 'surname', 'login', 'password', 'access_groups']
    ADD_FIELDS = ['name', 'surname', 'login', 'password', 'access_groups']
    NAME = "Сотрудник"

    STATUS = {0: 'Используется', 1: 'Не используется'}

    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    uuid = sqlalchemy.Column(sqlalchemy.String(50), default=uuid.uuid1())
    name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    surname = sqlalchemy.Column(sqlalchemy.String(256), default="")
    login = sqlalchemy.Column(sqlalchemy.String(256), default="")
    password = sqlalchemy.Column(sqlalchemy.String(256), default="")
    access_groups = sqlalchemy.Column(sqlalchemy.String(256), default="")
    disabled = Column(Integer, default=0)

    def __init__(self):
        self.uuid = uuid.uuid1()
        self.list_access_groups = list()
        self.list_access_groups = re.split(",", self.access_groups)

    def read(self):
        self.list_access_groups = list()
        if not self.access_groups == "":
            self.list_access_groups = re.split(",", self.access_groups)


"""
Функция получения объекта пользователь по логину
"""


def get_user_by_login(login):
    """
    Получить данные пользователя по логину.
    Информация о событиях записывается в лог приложения.

    :parameter login: логин пользователя

    :returns: объект класса User. None, если объект не найден или найдено несколько.
    """

    session = Session()
    try:
        user = session.query(User).filter(User.login == login).one()
    except sqlalchemy.orm.exc.NoResultFound:
        print "Пользователь не найден"
        logging.warning("Пользователь с логином %s не найден" % login)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
        # status = [False,"Такой логин существует. Задайте другой."]
        print "Найдено множество пользователей."
        logging.warning("Найдено множество пользователей с логином %s." % login)
        return None
    else:
        print "Пользователь найден"
        logging.warning("Пользователь с логином %s найден" % login)
        return user


class TextMessage(Base):
    """
    Класс для работы с текстовыми сообщениями в системе.

    Каждое сообщение имеет код и описание своего расположения.

    Список свойств класса:

    :parameter id: sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    :parameter uuid: идентифкатор (sqlalchemy.Column(sqlalchemy.String(50), default=uuid.uuid1()))
    :parameter code: код сообщения (sqlalchemy.Column(sqlalchemy.String(256)))
    :parameter text: текст сообщения (sqlalchemy.Column(sqlalchemy.String(TEXT)))
    :parameter place: место показа в системе (sqlalchemy.Column(sqlalchemy.String(256)))

    """

    __tablename__ = 'text_messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    code = sqlalchemy.Column(sqlalchemy.String(256), default="")
    text = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    place = sqlalchemy.Column(sqlalchemy.String(256), default="")

    def __init__(self):
        pass


"""
Функция получения описания по коду
"""


def get_desc(code):
    """
    Получить описание по его коду.

    :parameter code: код сообщения

    :returns: возвращает свойство text объекта класса Text_message. "", если объект не найден или найдено несколько.
    """

    session = Session()
    try:
        description = session.query(TextMessage).filter(TextMessage.code == code).one()
    except sqlalchemy.orm.exc.NoResultFound:
        print "Описание не найдено."
        logging.warning("Описание с кодом %s не найдено" % code)
        return ""
    except sqlalchemy.orm.exc.MultipleResultsFound:
        # status = [False,"Такой логин существует. Задайте другой."]
        print "Найдено множество описаний с таким кодом."
        logging.warning("Найдено множество описаний с кодом %s." % code)
        return ""
    else:
        print "Описание найдено"
        logging.warning("Описание с кодом %s найдено" % code)
        return description.text


class WizardConfiguration(Base):
    """
    Класс для хранения настроек мастера: текущий этап, выбранные опции, прочие данные которые необходимо запомнить.

    :parameter id: sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    :parameter industry: отрасль (sqlalchemy.Column(sqlalchemy.String(256)))
    :parameter cur_step: номер текущего шага в мастере (sqlalchemy.Column(sqlalchemy.String(256)))
    :parameter status: общий статус мастера (sqlalchemy.Column(sqlalchemy.String(256)))

    """

    __tablename__ = 'wizard_configuration'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    industry = sqlalchemy.Column(sqlalchemy.String(256), default="")
    cur_step = sqlalchemy.Column(sqlalchemy.String(256), default="")
    status = sqlalchemy.Column(sqlalchemy.String(256), default="")

    def __init__(self):
        self.industry = ""
        self.cur_step = ""
        self.status = ""


def wizard_conf_save(session):
    """
    Сохранение новых данных в базу.

    :return: True - сохранение прошло успешно, False - ошибки при сохранении
    """

    try:
        session.commit()
    except Exception as e:
        print(str(e))
        return False
    else:
        return True


def wizard_conf_read(session):
    """
    Чтение настроек мастера из базы.

    :return: None - ошибки при чтении конфигурации, или объект класса WizardConfiguration
    """

    try:
        wiz_conf = session.query(WizardConfiguration).one()
    except sqlalchemy.orm.exc.NoResultFound:
        print "Конфигурация мастера не найдена."
        logging.warning("Конфигурация мастера не найдена.")
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        # status = [False,"Такой логин существует. Задайте другой."]
        print "Найдено множество конфигураций."
        logging.warning("Найдено множество конфигураций.")
        raise Exception(e)
    else:
        print "Конфигурация найдена."
        logging.warning("Конфигурация найдена.")
        return wiz_conf


class OrgStucture(Base):
    """
    Класс для хранения орг структуры компании

    """

    __tablename__ = 'org_structure'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    parentid = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    org_name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    director = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def __init__(self):
        self.parentid = 0
        self.org_name = ""
        self.director = 0


def get_structure_sorted():
    """
    Возвращает список ИД всех уже существующих организационных единиц

    :return:список с ИД, если ничего нет, то пустой
    """

    session = Session()
    try:
        resp = session.query(OrgStucture).filter(OrgStucture.parentid != 0).all()
    except Exception as e:
        print "Ошибка при поиске организационноых единиц. " + str(e)
        return list()
    finally:
        session.close()

    # Сортируем согласно родительским объектам.
    sorted = list()
    shift = list()
    root = get_org_structure_root()
    sorted.append(root)
    shift.append(0)
    for one in resp:
        inx=0
        for i in sorted:
            if one.parentid == i.id:
                inx = sorted.index(i)
        sorted.insert(inx+1, one)
        shift.insert(inx+1, shift[inx]+5)

    return sorted, shift






def get_org_structure():
    """
    Возвращает структуру организации.

    :return:
    """

    session = Session()
    try:
        resp = session.query(OrgStucture).all()
    except Exception as e:
        print "Ошибка при поиске организационноых единиц. " + str(e)
        return list()
    else:
        return resp
    finally:
        session.close()


def get_org_structure_root():
    """
    Возвращает id корневого узла.


    :return: id корневого узла
    """
    session = Session()
    try:
        query = session.query(OrgStucture). \
            filter(OrgStucture.parentid == 0).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Родительский узел не найден."+str(e)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Найдено несколько корневых узлов. " + str(e)
        raise e
    else:
        return query
    finally:
        session.close()


def save_new_org_structure(parentid, director, org_name):
    """
    Записыает новый орг объект в базу.


    :return:
    """
    session = Session()
    new = OrgStucture()
    new.director = director
    new.parentid = parentid
    new.org_name = org_name

    try:
        session.add(new)
        session.commit()
    except Exception as e:
        print "Ошибка при записи объекта орг структуры. " + str(e)
        return "error"
    else:
        return "writed"
    finally:
        session.close()


def save_edit_org_structure(parentid, director, org_name, org_id):
    """
    Записыает изменения орг объекта в базу.


    :return:
    """

    session = Session()
    try:
        new = session.query(OrgStucture).filter(OrgStucture.id == org_id).one()
    except Exception as e:
        pass
    else:
        new.director = director
        new.parentid = parentid
        new.org_name = org_name

        try:
            session.commit()
        except Exception as e:
            print "Ошибка при записи объекта орг структуры. " + str(e)
            return "error"
        else:
            return "writed"
    finally:
        session.close()


def delete_org_structure(org_id):
    """
    Удаляет орг объекта в базу.

    :return:
    """

    session = Session()
    try:
        new = session.query(OrgStucture).filter(OrgStucture.id == org_id).one()
    except Exception as e:
        pass
    else:

        try:
            session.delete(new)
            session.commit()
        except Exception as e:
            print "Ошибка удаления объекта орг структуры. " + str(e)
            return "error"
        else:
            return "writed"
    finally:
        session.close()