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
from configurations import *
import random
import uuid
import logging
import py_expression_eval

reload(sys)
sys.setdefaultencoding("utf-8")

"""
Cosntants
"""

def_industry = {"1": "Дистрибьюция"}
industry_goals = {"1": ["g1", "g2", "g3", "g4"]}
persons = {0: "", 1: "замените меня", 2: "замените меня", 3: "замените меня", 4: "замените меня"}

perspectives = {0: "Финансы", 1: "Клиенты", 2: "Процессы", 3: "Персонал"}
PERSPECTIVE_COLORS = ["#CC6666", "#669966", "#336699", "#CC9966"]

enterprise_strategic_map = "ent0"
current_strategic_map = enterprise_strategic_map

KPI_SCALE_TYPE = {0: "Красный/Зеленый", 1: "Зеленый/Красный", 2: "Шкала (Красный/Желтый/Зеленый)",
                  3: "Шкала (Зеленый/Желтый/Красный)", 4: "Шкала (Красный/Зеленый/Красный)"}

SCALE_COLOR = {0: ["CC6666", "669966"], 1: ["669966", "CC6666"], 2: ["CC6666", "FFCC33", "669966"],
                  3: ["669966", "FFCC33", "CC6666"], 4: ["CC6666", "669966", "CC6666"]}

CYCLES = {0: "Неделя", 1: "Месяца(ев)", 2: "Квартал", 3: "Полгода", 4: "Год"}

MEASURES = {0: "Штуки", 1: "Проценты", 2: "Рубли", 3: "Баллы", 4: "Дни"}

MEASURES_SPEC = {0: "шт", 1: "%", 2: "руб", 3: "б", 4: "д"}

MEASURES_FORMAT = {0: "{:3.0f}", 1: "{:3.0f}", 2: "{:.2f}", 3: "{:3.0f}", 4: "{:3.0f}"}

GOAL_TYPE = {0: "lib", 1: "custom"}

GOAL_EDIT_FLAG = {0: "Нельзя изменять KPI", 1: "Можно изменять KPI"}

PERIOD_NAME = ["Декабрь", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
USER_STATUS = {0: "Активен", 1: "Отключен"}

VERSION = 0

AUTO_TARGET_CODES = {"101": "Первый квартал", "104": "Второй квартал", "107": "Третий квартал",
                     "110": "Четвертый квартал", "106": "Первое полугодие", "112": "Второе полугодие",
                     "113": "Год"}


class FactCycle(object):
    code = None
    name = ""

    def __init__(self, code=None, name=""):
        self.name = name
        self.code = code

FACT_CYCLES = {0: FactCycle(0, "День"), 1: FactCycle(1, "Неделя"), 2: FactCycle(2, "Месяц"), 3: FactCycle(3, "Квартал")}

"""
Подключение БД
"""
Base = sqlalchemy.ext.declarative.declarative_base()
Engine = sqlalchemy.create_engine(sql_uri, pool_size=20, pool_recycle=3600)
Session = sqlalchemy.orm.sessionmaker(bind=Engine)


"""
Логирование сообщений приложения в файл
"""
logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG,
                    filename="app_log.log")


def escape(t):
    """
    Экранирование специальных символов при выводе на экран.

    :param t: строка
    :return: экранированная строка
    """

    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("'", "&#39;").replace('"', "&quot;"))


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


def make_periods_for_kpi(start_date=None, plan_period=None):
    """
    Функция расчета отчетных периодов и названий для показателей

    :param start_date: стартовая дата, с какого месяца создаем периоды
    :param plan_period: сколько надо создать периодов начания со стартовой даты
    :return:
    """
    """
    period_date = dict()
    period_name = dict()

    for one in range(1, int(plan_period) + 1):
        print "Период: %s" % one

        year = start_date.year + ((start_date.month + one - 1) // 12)
        month = ((start_date.month % 12) + one) - 12 * ((start_date.month + one) // 12)
        if not month:
            month = 12

        print year, month

        period_date[one] = datetime.datetime(year, month, 1)
        if (period_date[one].month - 1) == 0:
            period_name[one] = str(PERIOD_NAME[period_date[one].month - 1]) + " " + \
                               str(period_date[one].year - 1)
        else:
            period_name[one] = str(PERIOD_NAME[period_date[one].month - 1]) + " " + \
                               str(period_date[one].year)

        print "Отчетная дата периода: %s" % period_date[one]
        print "Название отчетного периода: %s" % period_name[one]

    return period_date, period_name
    """
    return None, None


def make_periods_for_kpi_new(start_date=None, plan_period=None):
    """
        Функция формирования отчетных периодов и названий для них.
        Код периода формируется: номер отчетного месяца + год. Например: апрель 2016 -> 42016
        Отчетная дата формируется: первое число месяца следующего за отчетным. Например: апрель 2016 -> 01.05.2016

    :param start_date: стартовая дата, с какого месяца создаем периоды
    :param plan_period: сколько надо создать периодов начиная со стартовой даты
    :return:
    """

    # каждый элемент содержит массив из 3-х элементов: код периода, название периода, отчетная дата
    periods = dict()

    for one in range(0, int(plan_period)):
        p = one + 1
        print "Период: %s" % p
        periods[p] = list()

        year = start_date.year + ((start_date.month + one - 1) // 12)
        month = ((start_date.month % 12) + one) - 12 * ((start_date.month + one) // 12)
        if month == 0:
            month = 12

        print "Месяц: %s, год: %s" % (month, year)
        print "Код периода: %s" % (str(month) + str(year))
        print "Название периода: %s" % (PERIOD_NAME[month] + str(year))

        # код периода
        periods[p].append(str(month) + str(year))
        # название периода
        periods[p].append(PERIOD_NAME[month] + " " + str(year))

        if month + 1 == 13:
            month = 1
            year += 1
            periods[p].append(datetime.datetime(year, month, 1))
            print "Отчетная дата периода: %s" % datetime.datetime(year, month, 1)
        else:
            periods[p].append(datetime.datetime(year, month + 1, 1))
            print "Отчетная дата периода: %s" % datetime.datetime(year, month + 1, 1)

        print "-------------------------------------"

    return periods


def define_period(date=None):
    """
    Функция ищет к какому периоду относиться указанная дата и возвращает код и название периода.

    :param date: указанная дата
    :return:
    """

    """
    year = date.year
    month = date.month
    period_code = ""

    if month == 12:
        period_code = str(1) + str(year + 1)
    else:
        period_code = str(month + 1) + str(year)

    period_name = PERIOD_NAME[month] + " " + str(year)

    return [period_code, period_name]
    """
    return None


def define_period_new(date=None):
    """
    Функция ищет к какому периоду относиться указанная дата и возвращает код и название периода.

    :param date: указанная дата
    :return:
    """

    year = date.year
    month = date.month
    period = list()
    # код периода
    period.append(str(month) + str(year))
    # название периода
    period.append(PERIOD_NAME[month] + " " + str(year))
    # отчетная дата
    if month + 1 == 13:
        month = 1
        year += 1
        period.append(datetime.datetime(year, month, 1))
    else:
        period.append(datetime.datetime(year, month + 1, 1))

    return period


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
        self.disabled = 0

    def read(self):
        self.list_access_groups = list()
        if not self.access_groups == "":
            self.list_access_groups = re.split(",", self.access_groups)


"""
Функция получения объекта пользователь по логину
"""


def get_user_by_login(login=None):
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
        print "Пользователь не найден get_user_by_login()."
        logging.warning("Пользователь с логином %s не найден" % login)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound:
        # status = [False,"Такой логин существует. Задайте другой."]
        print "Найдено множество пользователей get_user_by_login()."
        logging.warning("Найдено множество пользователей с логином %s." % login)
        return None
    else:
        print "Пользователь найден get_user_by_login()."
        logging.warning("Пользователь с логином %s найден" % login)
        return user
    finally:
        session.close()


def get_all_users():
    """
    Получить всех пользователей в системе.

    :return: Словарь пользователей, ключ - идентификатор, значение - объект типа Users
    """

    session = Session()
    try:
        resp = session.query(User).order_by(User.surname.asc()).all()
    except Exception as e:
        print "Ошибка при получении данных пользовтелей get_all_users(). %s" % str(e)
        raise e
    else:
        users = dict()
        for one in resp:
            one.read()
            users[one.uuid] = one
        return users
    finally:
        session.close()


def add_new_user(name=None, surname=None, login=None, passwd=None, groups=None, status=None):

    session = Session()
    try:
        resp = session.query(User).filter(User.login == login).one()
    except sqlalchemy.orm.exc.NoResultFound:
        print "Пользователь c таким логином не найден. add_new_user()."
        print "Создаем нового."
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "add_new_user(). Найдено много пользователей c таким логином."
        raise e
    else:
        return None

    new_user = User()
    new_user.name = name
    new_user.surname = surname
    new_user.login = login
    new_user.password = passwd
    new_user.disabled = status
    new_user.access_groups = groups
    try:
        session.add(new_user)
        session.commit()
    except Exception as e:
        print "Ошибка при создании пользователя add_new_user(). %s " % str(e)
        raise e
    else:
        print "Пользователь создан add_new_user()."
        read_user_info()
        return new_user
    finally:
        session.close()




def user_update(uuid=None, name=None, surname=None, login=None, passwd=None, groups=None, status=None):
    """
    Обновление данных пользователя.

    :param uuid:
    :param name:
    :param surname:
    :param login:
    :param passwd:
    :param groups:
    :param status:
    :return:
    """

    session = Session()
    try:
        resp = session.query(User).filter(User.uuid == uuid).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Пользователь c таким UUID не найден. user_update()."
        raise e
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Найдено много пользователей c таким UUID. user_update()."
        raise e
    except Exception as e:
        print "Ошибка в user_update()."
        raise e
    else:
        # обновляем данные
        resp.name = name
        resp.surname = surname
        resp.login = login
        resp.password = passwd
        resp.access_groups = ",".join(groups)
        session.commit()
    finally:
        session.close()
        read_user_info()


def user_disable(uuid=None):
    """
    Обновление данных пользователя.

    :param uuid:
    :return:
    """

    session = Session()
    print uuid
    try:
        resp = session.query(User).filter(User.uuid == uuid).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Пользователь c таким UUID не найден. user_disable()."
        raise e
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Найдено много пользователей c таким UUID. user_disable()."
        raise e
    except Exception as e:
        print "Ошибка в user_disable()."
        raise e
    else:
        # обновляем данные
        resp.disabled = 1
        session.commit()
    finally:
        session.close()
        read_user_info()


def user_enable(uuid=None):
    """
    Обновление данных пользователя.

    :param uuid:
    :return:
    """

    session = Session()
    try:
        resp = session.query(User).filter(User.uuid == uuid).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Пользователь c таким UUID не найден. user_enable()."
        raise e
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Найдено много пользователей c таким UUID. user_enable()."
        raise e
    except Exception as e:
        print "Ошибка в user_enable()."
        raise e
    else:
        # обновляем данные
        resp.disabled = 0
        session.commit()
    finally:
        session.close()
        read_user_info()


def read_user_info():
    # ЧИтаем данные пользователей и заносим persons

    session = Session()
    global persons

    try:
        resp = session.query(User).all()
    except Exception as e:
        print "read_user_info(). Ошибка чтения пользоваетлей из базы. %s" % str(e)
    else:
        for one in resp:
            persons[one.id] = one.name + " " + one.surname

    finally:
        session.close()

read_user_info()


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
    object_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    status = sqlalchemy.Column(sqlalchemy.String(256), default="")

    def __init__(self):
        self.industry = ""
        self.cur_step = ""
        self.object_code = ""
        self.status = ""


def wizard_conf_save_old(session):
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


def wizard_conf_read_old(session):
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


def wizard_conf_read(object_code=None):
    session = Session()
    try:
        query = session.query(WizardConfiguration).filter(WizardConfiguration.object_code == object_code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено для WizardConfiguration(). BMTObjects.wizard_conf_read(). %s" % str(e)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.wizard_conf_read(). НАйдено много конфигураций для объекта: %s. %s" %\
              (object_code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции BMTObjects.wizard_conf_read(). %s" % str(e)
        raise e
    else:
        return query
    finally:
        session.close()


def wizard_conf_save(object_code=None, status="", cur_step="", industry=""):
    if not object_code:
        e = Exception()
        e.message = "Ошибка в функции BMTObjects.wizard_conf_save(). Не указан object_code. %s" % str(e)
        raise e

    session = Session()
    try:
        query = session.query(WizardConfiguration).filter(WizardConfiguration.object_code == object_code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        # Идем дальше
        pass
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.wizard_conf_read(). НАйдено много конфигураций для объекта: %s. %s" %\
              (object_code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции BMTObjects.wizard_conf_read(). %s" % str(e)
        raise e
    else:
        if query:
            # не пустой, обновляем настройки
            query.cur_step = cur_step
            query.status = status
            query.industry = industry
            try:
                session.commit()
            except Exception as e:
                print "Ошибка в функции BMTObjects.wizard_conf_read(). %s" % str(e)
                raise e
        else:
            # если пустой, создаем настройки
            conf = WizardConfiguration()
            conf.cur_step = cur_step
            conf.status = status
            conf.industry = industry
            conf.object_code = object_code
            try:
                session.add(conf)
                session.commit()
            except Exception as e:
                print "Ошибка в функции BMTObjects.wizard_conf_read(). %s" % str(e)
                raise e
    finally:
        session.close()


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
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено в get_structure_sorted()."+str(e)
        return list(), list()
    except Exception as e:
        print "Ошибка при поиске организационноых единиц get_structure_sorted(). " + str(e)
        raise e
    else:
        # Сортируем согласно родительским объектам.
        sorted = list()
        shift = list()
        root = get_org_structure_root()
        if root:
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
        else:
            return list(), list()
    finally:
        session.close()


def get_org_structure(org_id=None):
    """
    Возвращает структуру организации.

    :return:
    """

    session = Session()
    # если указан org_id, то возвращаем только указанную орг единицу. Если не найдено, то None
    if org_id:
        try:
            resp = session.query(OrgStucture).filter(OrgStucture.id == int(org_id)).one()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "get_org_structure. Ничего не найдено."+str(e)
            return None
        except sqlalchemy.orm.exc.MultipleResultsFound as e:
            print "get_org_structure. Найдено много объектов с ID = %s. Ошибка: %s" % (org_id, str(e))
            return None
        except Exception as e:
            print "Ошибка при поиске организационноых единиц. " + str(e)
            return None
        else:
            return resp
        finally:
            session.close()


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
        print "get_org_structure_root(). Родительский узел не найден."+str(e)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "get_org_structure_root(). Найдено несколько корневых узлов. " + str(e)
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


class Lib_Goal(Base):
    __tablename__ = "lib_goals"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    code = sqlalchemy.Column(sqlalchemy.String(10), default="", unique=True)
    goal_name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    description = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    perspective = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    type = sqlalchemy.Column(sqlalchemy.Integer, default=0) # тип цели, lib|custom - из биб-ки или создана пользователем
    edit = sqlalchemy.Column(sqlalchemy.Integer, default=0) # можно ли менять привязки KPI к цели.


    def __init__(self):
        self.code = ""
        self.goal_name = ""
        self.description = ""
        self.perspective = 0
        self.type = 0
        self.edit = 0


class Lib_KPI(Base):
    __tablename__ = "lib_kpi"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    description = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    code = sqlalchemy.Column(sqlalchemy.String(10), default="", unique=True)
    formula = sqlalchemy.Column(sqlalchemy.String(256), default="")
    link_to_desc = sqlalchemy.Column(sqlalchemy.String(256), default="")
    measure = sqlalchemy.Column(sqlalchemy.String(256), default=0) # from MEASURES
    target_responsible = sqlalchemy.Column(sqlalchemy.Integer, default=0) # from PERSONS
    fact_responsible = sqlalchemy.Column(sqlalchemy.Integer, default=0) # from PERSONS
    cycle = sqlalchemy.Column(sqlalchemy.Integer, default=0) # from CYCLES

    def __init__(self):
        self.name = ""
        self.description = ""
        self.code = ""
        self.formula = ""
        self.link_to_desc = "#"


class Lib_linked_goals(Base):
    __tablename__ = "lib_linked_goals"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    parent_code = sqlalchemy.Column(sqlalchemy.String(256), default="")
    child_code = sqlalchemy.Column(sqlalchemy.String(256), default="")


class Lib_linked_kpi_to_goal(Base):
    __tablename__ = "lib_linked_kpi_to_goal"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    goal_code = sqlalchemy.Column(sqlalchemy.String(256), default="")
    kpi_code = sqlalchemy.Column(sqlalchemy.String(256), default="")


class Custom_goal(Base):
    __tablename__ = "custom_goals"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    code = sqlalchemy.Column(sqlalchemy.String(10), default="", unique=True)
    goal_name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    description = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    perspective = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    type = sqlalchemy.Column(sqlalchemy.Integer, default=0) # тип цели, lib|custom - из биб-ки или создана пользователем
    edit = sqlalchemy.Column(sqlalchemy.Integer, default=0) # можно ли менять привязки KPI к цели.

    def __init__(self):
        u = uuid.uuid4().get_hex().__str__()
        self.code = "dg" + "".join(random.sample(u, 4))
        self.goal_name = ""
        self.description = ""
        self.perspective = 0
        self.type = 0
        self.edit = 0


def create_new_custom_goal(goal_fields):
    """
    Создаем новую кастомную цель, добавлем ее в таблицу кастомных целей и в текущую карту.

    :param goal_fields: список полей новой цели
    :return: код новой цели

    """

    goal = Custom_goal()

    session = Session()
    try:
        for key in goal_fields.keys():
            goal.__dict__[key] = goal_fields[key]
        session.add(goal)
        session.commit()
    except Exception as e:
        print "Ошибка в функции BMTObjects.create_new_custom_goal(). Цель не записана. %s" % str(e)
        raise e
    else:
        # Добавляем запись в стратегическую карту
        smap = StrategicMap()
        smap.goal_code = goal.code
        smap.date = datetime.datetime.now()
        smap.map_code = current_strategic_map
        smap.version = VERSION
        try:
            session.add(smap)
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.create_new_custom_goal(). Strategic map не записана. %s" % str(e)
            raise e
        else:
            return [True, goal.code]
    finally:
        session.close()


def update_custom_goal(code, goal_fields):
    """
    Обновление свойств цели.

    :param code: код цели
    :param goal_fields: свойства цели
    :return:
    """

    session = Session()
    try:
        resp = session.query(Custom_goal).filter(Custom_goal.code == code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "BMTObjects.update_custom_goal(). Не найдена цель с кодом: %s. %s" % (code, str(e))
        raise e
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.update_custom_goal(). НАйдено много целей с кодом: %s. %s" % (code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции BMTObjects.update_custom_goal(). %s" % str(e)
        raise e
    else:
        resp.goal_name = goal_fields.get('goal_name')
        resp.description = goal_fields.get('description')
        resp.perspective = goal_fields.get('perspective')

        try:
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.update_custom_goal(). Сохранение изменений. %s" % str(e)
            raise e
    finally:
        session.close()


def update_custom_link_for_goals(code, linked, delete_all=False):
    """
    Обновление связей для цели.

    :param code: код цели
    :param linked: новые связи
    :return:
    """

    session = Session()

    # Проверяем условие "Удалить все связи"
    if delete_all:
        try:
            resp = session.query(Custom_linked_goals).filter(or_(Custom_linked_goals.parent_code == code,
                                                                 Custom_linked_goals.child_code == code)).all()
        except Exception as e:
            print "Ошибка в функции BMTObjects. update_custom_link_for_goals(). Сохранение изменений. %s" % str(e)
            raise e
        else:
            for one in resp:
                session.delete(one)
            session.commit()
            return
        finally:
            session.close()


    if not isinstance(linked, list):
        linked = [linked]

    for_delete = []
    # ищем все связи редактируемой цели и проверяем их наличие в linked
    # если ответ положительный, убираем ее из linked и ищем дальше, если отрицательный - то удалем связь.
    # В конце в линкед должны остатьтся только новые связи, их создаем.
    try:
        resp = session.query(Custom_linked_goals).filter(Custom_linked_goals.parent_code == code).all()
        # resp1 = session.query(Custom_linked_goals).filter(Custom_linked_goals.child_code == code).all()
    except Exception as e:
        print "Ошибка в функции BMTObjects. update_custom_link_for_goals(). Сохранение изменений. %s" % str(e)
        raise e
    else:
        for one in resp:
            if one.child_code in linked:
                linked.remove(one.child_code)
            else:
                for_delete.append(one.child_code)

        print for_delete
        print linked

        if for_delete:
            # Удаляем лишние связи из старых
            try:
                resp = session.query(Custom_linked_goals).filter(or_(and_(Custom_linked_goals.parent_code == code,
                                                                          Custom_linked_goals.child_code.in_(for_delete)),
                                                                     and_(Custom_linked_goals.parent_code.in_(for_delete),
                                                                          Custom_linked_goals.child_code == code))).all()
                print resp
            except Exception as e:
                print "Ошибка в функции BMTObjects. update_custom_link_for_goals(). Сохранение изменений. %s" % str(e)
                raise e
            else:
                print "Удаляем связи: "
                for one in resp:
                    print one.parent_code, one.child_code
                    session.delete(one)

                session.commit()

        # Если в linked не пусто, создаем новые связи или возвращаемся
        if linked:

            # Создаем новые
            for one in linked:
                try:
                    create_custom_link_for_goals(code, one)
                except Exception as e:
                    print "Ошибка в функции BMTObjects. update_custom_link_for_goals(). Создание новых связей. %s" % str(e)
                    raise e
    finally:
        session.close()


class Custom_KPI(Base):

    __tablename__ = "custom_kpi"
    # TODO: Переделать работу с объектами CustomKPI для мастера планирования Карты компании
    # TODO: Переделать работу с объектами CustomKPI при переносе из LibKPI
    # TODO: Переделать объекты LibKPI

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    description = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    code = sqlalchemy.Column(sqlalchemy.String(10), default="", unique=True)
    formula = sqlalchemy.Column(sqlalchemy.String(256), default="")
    link_to_desc = sqlalchemy.Column(sqlalchemy.String(256), default="")
    # TODO: перевести measure из строки в целое число
    measure = sqlalchemy.Column(sqlalchemy.String(256), default=0) # from MEASURES
    target_responsible = sqlalchemy.Column(sqlalchemy.Integer, default=0) # from PERSONS
    fact_responsible = sqlalchemy.Column(sqlalchemy.Integer, default=0) # from PERSONS
    fact_cycle = sqlalchemy.Column(sqlalchemy.Integer, default=0) # from FACT_CYCLES
    cycle = sqlalchemy.Column(sqlalchemy.Integer, default=0) # from CYCLES
    kpi_scale_type = sqlalchemy.Column(sqlalchemy.Integer, default=0) # from  KPI_SCALE_TYPE
    data_source = sqlalchemy.Column(sqlalchemy.String(256), default="")

    def __init__(self):
        self.name = ""
        self.description = ""
        u = uuid.uuid4().get_hex().__str__()
        self.code = "kp" + "".join(random.sample(u, 4))
        self.formula = ""
        self.link_to_desc = "#"
        self.measure = 0
        self.cycle = 0
        self.target_responsible = 0
        self.fact_responsible = 0
        self.fact_cycle = 2
        self.data_source = ""
        self.kpi_scale_type = 0


def create_new_custom_kpi(kpi_fields):
    """
    Создаем новый кастомный показатель, добавлем его в таблицу и в текущую карту.

    :param kpi_fields: список полей нового показателя
    :return: код новго показателя

    """

    kpi = Custom_KPI()

    session = Session()
    try:
        for key in kpi_fields.keys():
            kpi.__dict__[key] = kpi_fields[key]
        session.add(kpi)
        session.commit()
    except Exception as e:
        print "Ошибка в функции BMTObjects.create_new_custom_kpi(). Показатель не записан. %s" % str(e)
        raise e
    else:
        # Добавляем запись в стратегическую карту
        smap = StrategicMap()
        smap.kpi_code = kpi.code
        smap.date = datetime.datetime.now()
        smap.map_code = current_strategic_map
        smap.version = VERSION
        try:
            session.add(smap)
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.create_new_custom_kpi(). Strategic map не записана. %s" % str(e)
            raise e
        else:
            return [True, kpi.code]
    finally:
        session.close()


class Custom_linked_goals(Base):
    __tablename__ = "custom_linked_goals"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    parent_code = sqlalchemy.Column(sqlalchemy.String(256), default="")
    child_code = sqlalchemy.Column(sqlalchemy.String(256), default="")


def create_custom_link_for_goals(goal, linked):
    """
    Связываем кастомную цель с другими целями

    :param goal:
    :param linked:
    :return:
    """

    session = Session()
    if not isinstance(linked, list):
        linked = [linked]

    print linked

    for one in linked:
        link = Custom_linked_goals()
        link.parent_code = goal
        link.child_code = one
        link1 = Custom_linked_goals()
        link1.parent_code = one
        link1.child_code = goal
        try:
            session.add(link)
            session.add(link1)
            session.commit()
        except Exception as e:
            session.close()
            print "Ошибка в функции create_custom_link_for_goals(). %s" % str(e)
            raise e

    session.close()


class Custom_linked_kpi_to_goal(Base):
    __tablename__ = "custom_linked_kpi_to_goal"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    goal_code = sqlalchemy.Column(sqlalchemy.String(256), default="")
    kpi_code = sqlalchemy.Column(sqlalchemy.String(256), default="")


def create_custom_link_kpi_to_goal(goal, kpi):
    """

    :param goal:
    :param kpi:
    :return:
    """

    session = Session()
    link = Custom_linked_kpi_to_goal()
    link.goal_code = goal
    link.kpi_code = kpi
    try:
        session.add(link)
        session.commit()
    except Exception as e:
        print "Ошибка в функции create_custom_link_kpi_to_goal(). %s" % str(e)
        raise e
    finally:
        session.close()


def delete_custom_link_kpi_to_goal(goal, kpi):
    """

    :param goal:
    :param kpi:
    :return:
    """

    session = Session()
    print goal
    print kpi

    try:
        resp = session.query(Custom_linked_kpi_to_goal).\
            filter(and_(Custom_linked_kpi_to_goal.kpi_code == kpi,
                        Custom_linked_kpi_to_goal.goal_code == goal)).one()

    except Exception as e:
        print "Ошибка в функции delete_custom_link_kpi_to_goal(). %s" % str(e)
        raise e
    else:
        session.delete(resp)
        session.commit()
    finally:
        session.close()


def update_custom_kpi(custom_kpi_update):
    """
    Обновляет значения полей кастомного KPI.

    :param custom_kpi_update:
    :return:
    """

    session = Session()

    print "SAVE custom kpi"
    for key in custom_kpi_update.keys():
        print key, ":", custom_kpi_update[key]

    try:
        resp = session.query(Custom_KPI).filter(Custom_KPI.code == custom_kpi_update['code']).one()
    except Exception as e:
        print "Ошибка в функции  update_custom_kpi(). %s" % str(e)
        raise e
    else:
        # Обновляем связь с целью
        try:
            resp1 = session.query(Custom_linked_kpi_to_goal).\
                filter(Custom_linked_kpi_to_goal.kpi_code == custom_kpi_update["code"]).one()
        except sqlalchemy.orm.exc.NoResultFound:
            print "Ни одна цель не связана с KPI: %s" % custom_kpi_update["code"]
            if custom_kpi_update["linked_goal"] != "0":
                print "Создаем связь GOAL: %s  --> KPI: %s" % (custom_kpi_update["linked_goal"], custom_kpi_update["code"])
                create_custom_link_kpi_to_goal(goal=custom_kpi_update["linked_goal"], kpi=custom_kpi_update["code"])
            else:
                print "Новая цель = %s - это операционный показатель." % custom_kpi_update["linked_goal"]
        except Exception as e:
            print "Ошибка в функции update_custom_kpi() при поиске связи KPI с целью. %s" % str(e)
        else:
            if custom_kpi_update["linked_goal"] == "0":
                print "update_custom_kpi(). Удаляем связь с целью для KPI: %s." % resp1.goal_code
                delete_custom_link_kpi_to_goal(goal=resp1.goal_code, kpi=custom_kpi_update["code"])
            else:
                print "update_custom_kpi(). Обновлем цель с %s на %s." % (resp1.goal_code, custom_kpi_update["linked_goal"])
                resp1.goal_code = custom_kpi_update["linked_goal"]

        resp.target_responsible = custom_kpi_update["target_responsible"]
        resp.fact_responsible = custom_kpi_update["fact_responsible"]
        # resp.fact_cycle = custom_kpi_update["fact_cycle"]
        resp.measure = custom_kpi_update["measure"]
        resp.cycle = custom_kpi_update["cycle"]
        resp.name = custom_kpi_update["name"]
        resp.description = custom_kpi_update["description"]
        resp.formula = custom_kpi_update["formula"]
        resp.link_to_desc = custom_kpi_update["link_to_desc"]
        resp.data_source = custom_kpi_update["data_source"]
        resp.kpi_scale_type = custom_kpi_update["kpi_scale_type"]
        session.commit()

    finally:
        session.close()


def load_custom_goals_kpi(goal_code=None, kpi_code=None):
    """
    Функция загрузки из базы всех целей и показателей компании.

    :parameter goal_code: код цели
    :parameter kpi_code: код показателя

    :return:
    """

    session = Session()

    try:
        if goal_code:
            resp = session.query(Custom_goal).filter(Custom_goal.code == goal_code).one()
        else:
            resp = session.query(Custom_goal).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Функция load_custom_goals_kpi(). Ничего не найдено для goal %s" % goal_code
        goals = None
    except Exception as e:
        session.close()
        raise e
    else:

        if goal_code:
            goals = resp
        else:
            goals = dict()
            for g in resp:
                goals[g.code] = g

    try:
        if kpi_code:
            resp = session.query(Custom_KPI).filter(Custom_KPI.code == kpi_code).one()
        else:
            resp = session.query(Custom_KPI).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Функция load_custom_goals_kpi(). Ничего не найдено для kpi %s" % goal_code
        kpi = None
    except Exception as e:
        raise e
    else:
        if kpi_code:
            kpi = resp
        else:
            kpi = dict()
            for k in resp:
                kpi[k.code] = k

    finally:
        session.close()

    return goals, kpi


def load_lib_goals_kpi():
    """
    Функция загрузки из базы всех заранее заданных целей и показателей.

    :return:
    """

    session = Session()
    try:
        resp = session.query(Lib_Goal).all()
    except Exception as e:
        raise e
    else:
        goals = dict()
        for g in resp:
            goals[g.code] = g

    try:
        resp = session.query(Lib_KPI).all()
    except Exception as e:
        raise e
    else:
        kpi = dict()
        for k in resp:
            kpi[k.code] = k

    return goals, kpi

    session.close()


def load_lib_links():

    session = Session()
    try:
        resp = session.query(Lib_linked_goals).all()
    except Exception as e:
        raise e
    else:
        linked_goals = dict()
        for g in resp:
            if g.parent_code in linked_goals.keys():
                linked_goals[g.parent_code].append(g.child_code)
            else:
                linked_goals[g.parent_code] = list()
                linked_goals[g.parent_code].append(g.child_code)

    try:
        resp = session.query(Lib_linked_kpi_to_goal).all()
    except Exception as e:
        raise e
    else:
        linked_kpi = dict()
        for g in resp:
            if g.goal_code in linked_kpi.keys():
                linked_kpi[g.goal_code].append(g.kpi_code)
            else:
                linked_kpi[g.goal_code] = list()
                linked_kpi[g.goal_code].append(g.kpi_code)
    return linked_goals, linked_kpi

    session.close()


def load_map_links(for_goals=None, for_kpi=None):
    """
    Получить связи между указанными целями и показателями.

    :param for_goals:
    :param for_kpi:
    :return: словарь списков, где ключ - код цели, значние - список kpi. Если нет kpi, то цель не включается.
    """

    session = Session()

    if for_goals and for_kpi:
        # ищем связанные с указанными целями kpi и возвращаем словарь списков
        if not isinstance(for_goals, list):
            for_goals = [for_goals]
        if not isinstance(for_kpi, list):
            for_kpi = [for_kpi]

        try:
            resp = session.query(Custom_linked_kpi_to_goal).\
                filter(and_(Custom_linked_kpi_to_goal.goal_code.in_(for_goals),
                            Custom_linked_kpi_to_goal.kpi_code.in_(for_kpi))).all()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "Ничего не найдено load_custom_links() для GOALS: %s. %s" % (for_goals, str(e))
            return dict()
        except Exception as e:
            print "Ошибка в функции BMTObjects.load_custom_links(). %s" % str(e)
            raise e
        else:
            linked_kpi = dict()
            for g in resp:
                if g.goal_code in linked_kpi.keys():
                    linked_kpi[g.goal_code].append(g.kpi_code)
                else:
                    linked_kpi[g.goal_code] = list()
                    linked_kpi[g.goal_code].append(g.kpi_code)
            return linked_kpi
        finally:
            session.close()

        return dict()

    else:
        return dict()


def load_custom_links(for_kpi=None):
    """
    Функция возвращает словари целей и показателей связанных с целями.
    Ключами в обеих структурах являются goal_code, значениями списки кодов связанных объектов.

    :param for_kpi:
    :param for_goals:

    :return: linked_goals, linked_kpi - словари.
    """

    session = Session()

    if for_kpi:
        # Ищем связанные с kpi цели, возвращаем Объект цели, None или ошибку
        try:
            resp = session.query(Custom_linked_kpi_to_goal).filter(Custom_linked_kpi_to_goal.kpi_code == for_kpi).one()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "Ничего не найдено load_custom_links() для KPI: %s. %s" % (for_kpi, str(e))
            return None
        except sqlalchemy.orm.exc.MultipleResultsFound as e:
            print "Ошибка в функции BMTObjects.load_custom_links(). НАйдено много целей для KPI: %s. %s" %\
                  (for_kpi, str(e))
            raise e
        except Exception as e:
            print "Ошибка в функции BMTObjects.load_custom_links(). %s" % str(e)
            raise e
        else:
            return resp
        finally:
            session.close()

        return None

    # Стандартный алгоритм
    try:
        resp = session.query(Custom_linked_goals).all()
    except Exception as e:
        raise e
    else:
        linked_goals = dict()
        for g in resp:
            if g.parent_code in linked_goals.keys():
                linked_goals[g.parent_code].append(g.child_code)
            else:
                linked_goals[g.parent_code] = list()
                linked_goals[g.parent_code].append(g.child_code)

    try:
        resp = session.query(Custom_linked_kpi_to_goal).all()
    except Exception as e:
        raise e
    else:
        linked_kpi = dict()
        for g in resp:
            if g.goal_code in linked_kpi.keys():
                linked_kpi[g.goal_code].append(g.kpi_code)
            else:
                linked_kpi[g.goal_code] = list()
                linked_kpi[g.goal_code].append(g.kpi_code)
    finally:
        session.close()

    return linked_goals, linked_kpi


def save_picked_goals_to_custom(picked_goals):
    """
    Сохраняем выбранные цели из библиотеки в кастомные таблицы.
    Сохраняем свящи между ними.

    :parameter picked_goals: выбранные коды целей

    :return:
    """

    session = Session()
    custom_goals = load_custom_goals_kpi()[0]

    try:
        resp = session.query(Lib_Goal).filter(and_(Lib_Goal.code.in_(picked_goals),
                                                   Lib_Goal.code.notin_(custom_goals.keys()))).all()
    except sqlalchemy.orm.exc.NoResultFound:
        return
    except Exception as e:
        raise e
    else:
        for g in resp:
            n = Custom_goal()
            n.code = g.code
            n.goal_name = g.goal_name
            n.description = g.description
            n.perspective = g.perspective
            n.type = g.type
            n.edit = g.edit
            session.add(n)
            session.commit()
            # Добавлем запись в стратегическую карту
            n = StrategicMap()
            n.map_code = current_strategic_map
            n.goal_code = g.code
            session.add(n)
            session.commit()
    finally:
        session.close()

    save_picked_links_to_custom()


def save_picked_links_to_custom():
    """
    Сохраняем связи между кастомными целями.

    :return:
    """

    session = Session()

    try:
        req = session.query(Custom_goal.code).all()
        resp = [i[0] for i in req]
        lresp = session.query(Lib_linked_goals).filter(and_(Lib_linked_goals.parent_code.in_(resp),
                                                            Lib_linked_goals.child_code.in_(resp))).all()
    except Exception as e:
        raise e
    else:
        print "Custom goals code: %s" % resp
        print type(resp)
        print "Lib goals links: %s" % lresp
        for l in lresp:
            req = session.query(Custom_linked_goals).filter(and_(Custom_linked_goals.parent_code == l.parent_code),
                                                            Custom_linked_goals.child_code == l.child_code).one_or_none()
            if not req:
                print "Adding link to custom %s - %s" %(l.parent_code, l.child_code)
                n = Custom_linked_goals()
                n.parent_code = l.parent_code
                n.child_code = l.child_code
                session.add(n)
                session.commit()
            else:
                print "Link already added to custom"
    finally:
        session.close()


def save_picked_kpi_to_custom(picked_kpi):
    """
    Сохраняем выбранные показатели из библиотеки в кастомные таблицы.
    Сохраняем связи между ними.

    :return:
    """

    session = Session()
    custom_kpi = load_custom_goals_kpi()[1]

    try:
        resp = session.query(Lib_KPI).filter(and_(Lib_KPI.code.in_(picked_kpi),
                                                  Lib_KPI.code.notin_(custom_kpi.keys()))).all()
    except Exception as e:
        raise e
    else:
        for g in resp:
            # Копируем показатели
            n = Custom_KPI()
            n.code = g.code
            n.name = g.name
            n.description = g.description
            n.formula = g.formula
            n.link_to_desc = g.link_to_desc
            n.cycle = g.cycle
            n.fact_responsible = g.fact_responsible
            n.measure = g.measure
            n.target_responsible = g.target_responsible
            session.add(n)
            session.commit()
            # Добавлем запись в стратегическую карту
            n = StrategicMap()
            n.map_code = current_strategic_map
            n.kpi_code = g.code
            session.add(n)
            session.commit()
    finally:
        session.close()

    save_picked_kpi_links_to_custom()


def save_picked_kpi_links_to_custom():
    session = Session()

    try:
        req = session.query(Custom_KPI.code).all()
        resp = [i[0] for i in req]
        req = session.query(Custom_goal.code).all()
        resp1 = [i[0] for i in req]
        lresp = session.query(Lib_linked_kpi_to_goal).filter(and_(Lib_linked_kpi_to_goal.kpi_code.in_(resp),
                                                                  Lib_linked_kpi_to_goal.goal_code.in_(resp1))).all()
    except Exception as e:
        raise e
    else:
        print "Custom KPI codes: %s" % resp1
        print "Custom goals codes: %s" % resp
        print "Lib goals to KPI links: %s" % lresp
        for l in lresp:
            req = session.query(Custom_linked_kpi_to_goal).filter(and_(Custom_linked_kpi_to_goal.goal_code ==
                                                                       l.goal_code),
                                                                  Custom_linked_kpi_to_goal.kpi_code ==
                                                                  l.kpi_code).one_or_none()
            if not req:
                print "Adding link to custom %s - %s" %(l.goal_code, l.kpi_code)
                n = Custom_linked_kpi_to_goal()
                n.goal_code = l.goal_code
                n.kpi_code = l.kpi_code
                session.add(n)
                session.commit()
            else:
                print "Link already added to custom"
    finally:
        session.close()


class StrategicMapDescription(Base):
    """
    Класс для хранения данных о стратегических картах. Код карты, название, описание, владелец, дата.
    """
    __tablename__ = "strategic_maps_desc"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    code = sqlalchemy.Column(sqlalchemy.String(10), default="", unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    description = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    owner = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    status = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    department = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date = sqlalchemy.Column(sqlalchemy.DATETIME(), default=datetime.datetime.now())
    start_date = sqlalchemy.Column(sqlalchemy.DATETIME(), default=datetime.datetime.now())  # Начало работы карты
    cycle = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # период используемый при планировании
    cycle_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # количество периодов
    draw_data = sqlalchemy.Column(sqlalchemy.TEXT(), default="")

    def __init__(self):
        self.code = ""
        self.name = ""
        self.description = ""
        self.owner = 0
        self.status = 0
        self.department = 0
        self.date = datetime.datetime.now()
        self.start_date = datetime.datetime.now()
        self.cycle = 1
        self.cycle_count = 1
        self.draw_data = ""

    def create_enterprise_map(self):
        session = Session()

        self.code = "ent0"
        self.name = "Стратегическая карта компании"
        self.description = "Стратегическая карта компании верхнего уровня."
        self.owner = 0
        self.status = 0
        self.department = 0
        self.date = datetime.datetime.now()
        self.start_date = datetime.datetime.now()
        self.cycle = 1
        self.cycle_count = 1
        self.draw_data = ""

        try:
            session.add(self)
            session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()


def create_ent_strategic_map(owner=None, cycle=None, cycle_count=None):
    session = Session()

    s = StrategicMapDescription()
    s.code = enterprise_strategic_map
    s.name = "Стратегическая карта компании"
    s.description = "Стратегическая карта компании верхнего уровня."
    s.owner = owner
    s.status = 0
    s.department = 0
    s.date = datetime.datetime.now()
    s.start_date = datetime.datetime.now()
    if cycle:
        s.cycle = cycle
    else:
        s.cycle = 1  # стандартный период: месяц
    if cycle_count:
        s.cycle_count = cycle_count
    else:
        s.cycle_count = 3  # планируем стандартно на 3 пероида вперед

    try:
        session.add(s)
        session.commit()
    except Exception as e:
        raise e
    finally:
        session.close()


def create_dep_strategic_map(department, name="", description="", owner=0, status=0):
    session = Session()

    s = StrategicMapDescription()
    s.code = "dep" + str(department)
    s.name = name
    s.description = description
    s.owner = owner
    s.status = status
    s.department = department
    s.start_date = datetime.datetime.now()
    s.cycle = 1
    s.cycle_count = 3
    s.date = datetime.datetime.now()

    try:
        session.add(s)
        session.commit()
    except Exception as e:
        raise e
    finally:
        session.close()


def get_map_for_dep(department):
    session = Session()

    try:
        query = session.query(StrategicMapDescription).filter(StrategicMapDescription.department == int(department)).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено для StrategicMapDescription(). BMTObjects.get_map_for_dep(). %s" % str(e)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.get_map_for_dep(). НАйдено много карт для подразделения: %s. %s" %\
              (department, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции get_map_for_dep(). %s" % str(e)
        raise e
    else:
        return query
    finally:
        session.close()


def get_all_maps():
    # Возвращает объекты всех карт, отсортированные по дате создания.

    session = Session()

    try:
        query = session.query(StrategicMapDescription).order_by(StrategicMapDescription.date.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено для StrategicMapDescription(). BMTObjects.get_all_maps(). %s" % str(e)
        return None
    except Exception as e:
        print "Ошибка в функции get_map_for_dep(). %s" % str(e)
        raise e
    else:
        return query
    finally:
        session.close()


def get_strategic_map_object(current_map_code):
    # Возвращает объект катры по коду

    session = Session()

    try:
        query = session.query(StrategicMapDescription).filter(StrategicMapDescription.code == current_map_code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено для StrategicMapDescription(). BMTObjects.get_strategic_map_object(). %s" % str(e)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.get_strategic_map_object(). НАйдено много карт для кода: %s. %s" %\
              (current_map_code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции get_strategic_map_object(). %s" % str(e)
        raise e
    else:
        return query
    finally:
        session.close()


def save_map_draw_data(map_code, json_string):
    """
    Записываем данные о расположении объектов для отрисовки карты на странице.
    Храним json строку с данными для fabric.js

    :param map_code: код карты
    :param json_string: строка в формате json с данными об объектах на карте для fabric.js

    :return: ничего. Лови исключение.
    """

    session = Session()
    try:
        resp = session.query(StrategicMapDescription).filter(StrategicMapDescription.code == map_code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено для StrategicMapDescription(). BMTObjects.save_map_draw_data(). %s" % str(e)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.save_map_draw_data(). НАйдено много карт для кода: %s. %s" %\
              (map_code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции save_map_draw_data(). %s" % str(e)
        raise e
    else:
        resp.draw_data = json_string
        session.commit()
    finally:
        session.close()

    session.close()


def load_map_draw_data(map_code):
    """
    Загружаем данные о расположении объектов для отрисовки карты на странице.
    Храним json строку с данными для fabric.js

    :param map_code: код карты

    :return: json строка для fabric.js
    """

    session = Session()
    try:
        resp = session.query(StrategicMapDescription).filter(StrategicMapDescription.code == map_code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено для StrategicMapDescription(). BMTObjects.load_map_draw_data(). %s" % str(e)
        return None
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.load_map_draw_data(). НАйдено много карт для кода: %s. %s" %\
              (map_code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции load_map_draw_data(). %s" % str(e)
        raise e
    else:
        return resp.draw_data
    finally:
        session.close()


class StrategicMap(Base):
    """
    Класс для хранения информации об объектах которые входят в ту или иную карту.
    Хранит коды объектов, каждый тип в своем поле.
    """
    __tablename__ = "strategic_maps"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    map_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    goal_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    kpi_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    metric_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    event_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    version = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date = sqlalchemy.Column(sqlalchemy.DATETIME(), default=datetime.datetime.now())

    def __init__(self):
        self.map_code = ""
        self.goal_code = ""
        self.kpi_code = ""
        self.metric_code = ""
        self.event_code = ""
        self.version = 0
        self.date = datetime.datetime.now()


def load_cur_map_objects(cur_map=None):
    """
    Загружаем объекты находящиеся в указанной стратегической карте.
    Если ничего не указано, загружем для текущей current_strategic_map.

    :return:
    """
    goals = dict()
    kpi = dict()
    events = dict()
    metrics = dict()

    if not cur_map:
        cur_map = current_strategic_map

    session = Session()
    # Загружаем цели для указанной карты
    try:
        query = session.query(StrategicMap).filter(StrategicMap.map_code == cur_map).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        # Если ничего нет, то возвращаем None
        pass
    except Exception as e:
        print "Ошибка в функции BMTObjects.load_cur_map_objects(). %s" % str(e)
        raise e
    else:
        for each in query:
            if each.goal_code:
                goals[each.goal_code] = load_custom_goals_kpi(each.goal_code, None)[0]
            if each.kpi_code:
                one = load_custom_goals_kpi(None, each.kpi_code)[1]
                kpi[each.kpi_code] = one
                # проверяем наличие связанной цели. Если такой нет, то это операционный показатель
                if not load_custom_links(for_kpi=each.kpi_code):
                    metrics[each.kpi_code] = one
            if each.event_code:
                events[each.event_code] = get_events(each.event_code)
            if each.metric_code:
                pass
    finally:
        return goals, kpi, events, metrics
        session.close()


def save_goals_to_map(picked_goals):
    """
    Сохраняем указание на выбранные цели в текущую карту.

    :parameter picked_goals: выбранные коды целей

    :return:
    """

    session = Session()
    for g in picked_goals:
        try:
            query = session.query(StrategicMap).filter(and_(StrategicMap.map_code == current_strategic_map,
                                                            StrategicMap.goal_code == g)).one_or_none()
        except Exception as e:
            session.close()
            raise e
        if not query:

            # Добавлем запись в стратегическую карту
            n = StrategicMap()
            n.map_code = current_strategic_map
            n.goal_code = g
            try:
                session.add(n)
                session.commit()
            except Exception as e:
                session.close()
                raise e
        else:
            print "Функция save_goals_to_map(). Запись для goal %s в карте %s существует." % (g, current_strategic_map)

    session.close()


def save_kpi_to_map(picked_kpi):
    """
    Сохраняем указание на выбранные kpi в текущую карту.

    :parameter picked_kpi: выбранные коды показателей

    :return:
    """

    session = Session()

    print "save_kpi_to_map()"
    print current_strategic_map
    print picked_kpi

    for g in picked_kpi:
        try:
            query = session.query(StrategicMap).filter(and_(StrategicMap.map_code == current_strategic_map,
                                                            StrategicMap.kpi_code == g)).one_or_none()
        except Exception as e:
            session.close()
            raise e
        if not query:

            # Добавлем запись в стратегическую карту
            n = StrategicMap()
            n.map_code = current_strategic_map
            n.kpi_code = g
            try:
                session.add(n)
                session.commit()
            except Exception as e:
                session.close()
                raise e
        else:
            print "Функция save_kpi_to_map(). Запись для kpi %s в карте %s существует." % (g, current_strategic_map)

    session.close()


def remove_goal_from_map(goal_code=None, map_code=None):
    """
    Удаляет вхождение указанной цели из карты. Если код карты не указан, удаляет из текущей.

    :param goal_code: код цели
    :param map_code: код карты
    :return:
    """

    if not goal_code or not map_code:
        return False

    session = Session()
    try:
        resp = session.query(StrategicMap).filter(and_(StrategicMap.goal_code == goal_code),
                                                  (StrategicMap.map_code == map_code)).delete()
    except Exception as e:
        session.close()
        print "Ошибка в функции BMTObjects.remove_goal_from_map(). При удалении цели из карты. %s" % str(e)
    else:
        return True
    finally:
        session.commit()
        session.close()


def remove_kpi_from_map(kpi_code=None, map_code=None):
    """
    Удаляет вхождение указанного показателя из карты. Если код карты не указан, удаляет из текущей.

    :param kpi_code: код показателя
    :param map_code: код карты
    :return:
    """

    if not kpi_code or not map_code:
        return False

    session = Session()
    try:
        resp = session.query(StrategicMap).filter(and_(StrategicMap.kpi_code == kpi_code),
                                                  (StrategicMap.map_code == map_code)).delete()
    except Exception as e:
        session.close()
        print "Ошибка в функции BMTObjects.remove_kpi_from_map(). При удалении kpi из карты. %s" % str(e)
    else:
        return True
    finally:
        session.commit()
        session.close()


def group_goals(map_goals):
    """
    Группирует цели по перспективам и прочим условиям.
    Возвращает ТОЛЬКО КОДЫ для сгруппированных целей.

    :param map_goals:
    :return:
    """

    # Порядок следования как в перспективах
    grouped_goals = [[], [], [], []]
    for goal in map_goals.values():
        p = goal.perspective
        grouped_goals[p].append(goal.code)

    return grouped_goals


class KPITargetValue(Base):
    """
    Класс для хранения целевых значений показателей и их типов.
    """
    __tablename__ = "kpi_target_values"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    kpi_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    first_value = sqlalchemy.Column(sqlalchemy.Float, default=0)
    second_value = sqlalchemy.Column(sqlalchemy.Float, default=0)
    formula = sqlalchemy.Column(sqlalchemy.String(256), default="")  # для вычисления авто показателей кварталы, полгода, год
    version = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date = sqlalchemy.Column(sqlalchemy.DATETIME(), default=datetime.datetime.now())
    period_code = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # Код периода к которому относится значение
    period_name = sqlalchemy.Column(sqlalchemy.String(256), default="")  # Название периода к которому относиться значение

    def __init__(self):
        self.kpi_code = 0
        self.first_value = 0
        self.second_value = 0
        self.version = 0
        self.date = datetime.datetime.now()
        self.period_code = 0
        self.period_name = ""
        self.formula = ""


def get_kpi_target_value(kpi_code=None, period_code=None):
    """
    Возвращает список объектов класса KPITargetValue.

    :param kpi_code:
    :param period_code:
    """

    session = Session()

    if kpi_code and not period_code:
        try:
            resp = session.query(KPITargetValue).filter(KPITargetValue.kpi_code == kpi_code).\
                order_by(KPITargetValue.date.asc(), KPITargetValue.period_code.asc()).all()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "BMTObjects.get_kpi_target_value(). Ничего не найдено для KPI = %s" % kpi_code
            return None
        except Exception as e:
            print "Ошибка в функции BMTObjects.get_kpi_target_value(). " + str(e)
            raise e
        else:
            return resp
        finally:
            session.close()
    elif kpi_code and period_code:
        try:
            resp = session.query(KPITargetValue).filter(and_(KPITargetValue.kpi_code == kpi_code,
                                                             KPITargetValue.period_code == period_code)).one()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "BMTObjects.get_kpi_target_value(). Ничего не найдено для KPI = %s и Period = %s" % \
                  (kpi_code, period_code)
            return None
        except Exception as e:
            print "Ошибка в функции BMTObjects.get_kpi_target_value(). " + str(e)
            raise e
        else:
            return resp
        finally:
            session.close()
    else:
        session.close()
        return None


def save_kpi_target_value(kpi_target_value):
    """
    Сохраняет объект класса KPITargetValue.
    Если такой kpi_code и дата уже встречались, то происходит обновление. Если нет, то создается новый.
    """

    session = Session()
    print "SAVE target values"
    # for key in kpi_target_value.keys():
    #    print key, ":", kpi_target_value[key]

    # check exist
    try:
        exist = session.query(KPITargetValue).filter(and_(KPITargetValue.kpi_code == kpi_target_value['kpi_code'],
                                                          KPITargetValue.period_code == kpi_target_value['period_code'])).one()
    except sqlalchemy.orm.exc.NoResultFound:
        exist = None
    except Exception as e:
        print "Ошибка в функции BMTObjects.save_kpi_target_value. Чтение KPITargetValue. " + str(e)
        session.close()
        raise e

    if exist:
        # такой объект существует, обновляем
        print "KPI TARGET такой объект существует, обновляем"
        try:
            # если значение не передано, присваиваем по умолчанию 0
            if kpi_target_value.get("first_value"):
                exist.first_value = kpi_target_value["first_value"]

            if kpi_target_value.get("second_value"):
                exist.second_value = kpi_target_value["second_value"]

            if kpi_target_value.get("formula"):
                exist.formula = kpi_target_value["formula"]

            #else:
            #    exist.first_value = 0
            # exist.second_value = kpi_target_value["second_value"]
            # exist.kpi_scale_type = kpi_target_value["kpi_scale_type"]
            # exist.data_source = kpi_target_value["data_source"]
            # exist.version = kpi_target_value["version"]
            # exist.date = datetime.datetime.now()
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.save_kpi_target_value. Обновление KPITargetValue. " + str(e)
            raise e
        finally:
            session.close()
    else:
        # создаем новый
        new = KPITargetValue()
        try:
            for key in kpi_target_value.keys():
                new.__dict__[key] = kpi_target_value[key]
            session.add(new)
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.save_kpi_target_value. Создание нового KPITargetValue. " + str(e)
            raise e
        finally:
            session.close()


def delete_kpi_target_value(kpi_code=None, period_code=None):
    """
    Удаляем целевые значения из базы для указанного в kpi_code показателя.
    Если указан конкретный период в period_code, то удаляем только его.

    :param kpi_code: код показателя
    :param period_code: код периода
    :return:
    """

    session = Session()
    try:
        if period_code:
            resp = session.query(KPITargetValue).filter(and_(KPITargetValue.kpi_code == kpi_code,
                                                             KPITargetValue.period_code == period_code)).all()
        else:
            resp = session.query(KPITargetValue).filter(KPITargetValue.kpi_code == kpi_code).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "BMTObjects.delete_kpi_target_value(). Ничего не найдено для KPI = %s" % kpi_code
        return None
    except Exception as e:
        print "Ошибка в функции BMTObjects.delete_kpi_target_value(). " + str(e)
        raise e
    else:
        try:
            for one in resp:
                session.delete(one)
                session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.delete_kpi_target_value() при удалении целевых значений. " + str(e)
            raise e
    finally:
        session.close()


def create_auto_target_values(for_kpi=None):
    """
    Рассчитать и заполнить автоматические значения для показателей.
    Названия автоматических значений и их коды указаны в константе AUTO_TARGET_CODES.

    При удалении периодов входящих в формулу для расчета, формула изменяется если остался хотя бы один период, который \
    должен в нее входить. Т.е. если последовательно уделаять месяца 2-ого квартала, после удаления последнего месяца в \
    формуле останется запись только о нем. Но это не будет влиять на расчеты, т.к. данные о самом периоде были удалены.\
    После добавления нового месяца в период, формула будет автоматически пересчитана.

    :param for_kpi: рассчитать для указанного kpi

    :return:
    """

    session = Session()

    if for_kpi:
        target = get_kpi_target_value(for_kpi)
        formula = dict()
        for one in target:
            # Эта проверка нужна пока коды периодов сдвинуты на один месяц вперед!!!
            # вычисляем реальный месяц и год для целевого значения
            if one.date.month - 1 == 0:
                month = 12
                year = one.date.year - 1
            else:
                month = one.date.month - 1
                year = one.date.year

            # это авто период, исключаем из обработки
            if str(one.period_code // 10000) not in AUTO_TARGET_CODES.keys():
                # print "Период: %s , дата: %s" % (one.period_code, one.date)
                # print "Реальный месяц: %s" % month
                # print "Реальный год: %s" % year

                if not formula.get("101" + str(year)):
                    # создаем пустые значения
                    for key in AUTO_TARGET_CODES.keys():
                        formula[str(key) + str(year)] = list()
                        formula[str(key) + str(year)].append(list())  # [0] список периодов для расчета
                        formula[str(key) + str(year)].append("")  # [1] код периода для формирования названия
                        formula[str(key) + str(year)].append("")  # [2] дата отчетного периода
                        formula[str(key) + str(year)].append(str(year))  # [3] год для формирования названия

                if 1 <= month <= 3:
                    print AUTO_TARGET_CODES["101"]
                    # первый квартал
                    formula["101" + str(year)][0].append("p_" + str(one.period_code))
                    formula["101" + str(year)][1] = "101"
                    formula["101" + str(year)][2] = datetime.datetime.strptime("01.04.%s" % str(year), "%d.%m.%Y").date()
                    # первое полугодие
                    formula["106" + str(year)][0].append("p_" + str(one.period_code))
                    formula["106" + str(year)][1] = "106"
                    formula["106" + str(year)][2] = datetime.datetime.strptime("01.07.%s" % str(year), "%d.%m.%Y").date()
                elif 4 <= month <= 6:
                    print AUTO_TARGET_CODES["104"]
                    # второй квартал
                    formula["104" + str(year)][0].append("p_" + str(one.period_code))
                    formula["104" + str(year)][1] = "104"
                    formula["104" + str(year)][2] = datetime.datetime.strptime("01.07.%s" % str(year), "%d.%m.%Y").date()
                    # первое полугодие
                    formula["106" + str(year)][0].append("p_" + str(one.period_code))
                    formula["106" + str(year)][1] = "106"
                    formula["106" + str(year)][2] = datetime.datetime.strptime("01.07.%s" % str(year), "%d.%m.%Y").date()
                elif 7 <= month <= 9:
                    print AUTO_TARGET_CODES["107"]
                    formula["107" + str(year)][0].append("p_" + str(one.period_code))
                    formula["107" + str(year)][1] = "107"
                    formula["107" + str(year)][2] = datetime.datetime.strptime("01.10.%s" % str(year), "%d.%m.%Y").date()
                    formula["112" + str(year)][0].append("p_" + str(one.period_code))
                    formula["112" + str(year)][1] = "112"
                    formula["112" + str(year)][2] = datetime.datetime.strptime("01.01.%s" % str(year + 1), "%d.%m.%Y").date()
                elif 10 <= month <= 12:
                    print AUTO_TARGET_CODES["110"]
                    # Четвертый квартал
                    formula["110" + str(year)][0].append("p_" + str(one.period_code))
                    formula["110" + str(year)][1] = "110"
                    formula["110" + str(year)][2] = datetime.datetime.strptime("01.01.%s" % str(year + 1), "%d.%m.%Y").date()
                    # Второе полугодие
                    formula["112" + str(year)][0].append("p_" + str(one.period_code))
                    formula["112" + str(year)][1] = "112"
                    formula["112" + str(year)][2] = datetime.datetime.strptime("01.01.%s" % str(year + 1), "%d.%m.%Y").date()

                formula["113" + str(year)][0].append("p_" + str(one.period_code))
                formula["113" + str(year)][1] = "113"
                formula["113" + str(year)][2] = datetime.datetime.strptime("01.01.%s" % str(year + 1), "%d.%m.%Y").date()

                #print "---------------------------"

        print formula

        # сохраняем авто периоды для показателя
        for one in formula.keys():
            # Создаем только те периоды в которых есть данные
            if formula[one][1]:
                target_value = dict()
                target_value["kpi_code"] = for_kpi
                # target_value["first_value"] = 0
                # TODO: Различные варианты расчета исходя из природы показателя. Указать в свойствах показателя.
                # Сумма, среднее
                target_value["formula"] = " + ".join(formula[one][0])  # тут надо делать выбор формулы. Сейчас: сумма
                target_value["date"] = formula[one][2]
                target_value["period_code"] = int(one)
                target_value["period_name"] = str(AUTO_TARGET_CODES.get(formula[one][1])) + " " + str(formula[one][3])

                try:
                    save_kpi_target_value(target_value)
                except Exception as e:
                    raise e
                print "---------------------------------"

    session.close()


def calculate_auto_target_values(for_kpi=None, for_period=None):
    """
    Функция расчета целевого значения показателя по формуле для автоматических периодов

    :param for_kpi: код показателя
    :param for_period: период для которого надо сделать расчет
    :return: значение расчета float или None, если ошибка
    """

    if not for_kpi:
        return None

    session = Session()
    try:
        t = get_kpi_target_value(for_kpi)
    except Exception as e:
        session.close()
        raise e
    else:
        if t:
            target = dict()
            for one in t:
                target[one.period_code] = one
        else:
            session.close()
            return None

    if for_period and target.get(for_period).formula:
        # если указан период и есть формула, делаем расчет только для него
        print target.get(for_period).formula
        try:
            formula = py_expression_eval.Parser().parse(target.get(for_period).formula)
        except Exception as e:
            print "Формула некорректная. %s" % str(e)
        else:
            variables = dict()
            print formula.variables()
            for v in formula.variables():
                variables[v] = 0
                print v.split("_")[1]
                if target.get(int(v.split("_")[1])):
                    variables[v] = target.get(int(v.split("_")[1])).second_value
                    print v, " : ", variables[v]

            result = formula.evaluate(variables)
            print result

            target_value = dict()
            target_value["kpi_code"] = for_kpi
            # target_value["first_value"] = result
            target_value["second_value"] = result
            target_value["period_code"] = for_period

            try:
                save_kpi_target_value(target_value)
            except Exception as e:
                raise e

    # расчет всех авто периодов для целевых значений показателя
    if for_kpi and not for_period:
        print "Рассчитываем все AUTO PERIODS TARGET для KPI: %s" % for_kpi
        for period in target.values():
            if period.formula:
                print period.period_code, " : ", period.formula
                try:
                    formula = py_expression_eval.Parser().parse(period.formula)
                except Exception as e:
                    print "Формула некорректная. %s" % str(e)
                else:
                    variables = dict()
                    print formula.variables()
                    for v in formula.variables():
                        variables[v] = 0
                        print v.split("_")[1]
                        if target.get(int(v.split("_")[1])):
                            variables[v] = target.get(int(v.split("_")[1])).second_value
                            print v, " : ", variables[v]

                    try:
                        result = formula.evaluate(variables)
                    except Exception as e:
                        print "Ошибка в расчетах AUTO PERIODS TARGET для KPI: %s" % for_kpi
                        session.close()
                        raise e
                    else:
                        print result

                        target_value = dict()
                        target_value["kpi_code"] = for_kpi
                        # target_value["first_value"] = result
                        target_value["second_value"] = result
                        target_value["period_code"] = period.period_code

                        try:
                            save_kpi_target_value(target_value)
                        except Exception as e:
                            session.close()
                            raise e
    session.close()


class KPIFactValue(Base):
    """
    Хранит фактические значения метрик.
    """
    __tablename__ = "fact_values"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    kpi_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    fact_value = sqlalchemy.Column(sqlalchemy.Float, default=0)
    create_date = sqlalchemy.Column(sqlalchemy.DATETIME(), default=datetime.datetime.now())
    period_code = sqlalchemy.Column(sqlalchemy.String(256), default="")
    version = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def __init__(self):
        self.kpi_code = ""
        self.fact_value = 0
        self.create_date = datetime.datetime.now()
        self.period_code = ""
        self.version = 0


def get_kpi_fact_values(for_kpi=None, period_code=None):
    """
    Функция возвращает все записи о фактических значениях для указанного KPI

    :param for_kpi: для указанного kpi
    :param period_code: код периода
    :return:
    """

    session = Session()
    if for_kpi and not period_code:
        try:
            if for_kpi:
                resp = session.query(KPIFactValue).filter(KPIFactValue.kpi_code == for_kpi).\
                    order_by(KPIFactValue.period_code.asc(), KPIFactValue.create_date.asc()).all()
            else:
                return None
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "BMTObjects.get_kpi_fact_value(). Ничего не найдено для KPI = %s" % for_kpi
            return None
        except Exception as e:
            print "Ошибка в функции BMTObjects.get_kpi_fact_value(). " + str(e)
            raise e
        else:
            fact = dict()
            for one in resp:
                if fact.get(one.period_code):
                    fact[one.period_code].append(one)
                else:
                    fact[one.period_code] = list()
                    fact[one.period_code].append(one)
            return fact
        finally:
            session.close()
    elif for_kpi and period_code:
        try:
            resp = session.query(KPIFactValue).filter(and_(KPIFactValue.kpi_code == for_kpi,
                                                           KPIFactValue.period_code == period_code)).\
                order_by(KPIFactValue.create_date.asc()).all()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "BMTObjects.get_kpi_fact_value(). Ничего не найдено для KPI = %s и Period = %s" % \
                  (for_kpi, period_code)
            return None
        except Exception as e:
            print "Ошибка в функции BMTObjects.get_kpi_fact_value(). " + str(e)
            raise e
        else:
            return resp
        finally:
            session.close()

    else:
        session.close()
        return None


def get_fact_period_code(for_kpi=None, date=None):

    return ""


def save_kpi_fact_value(kpi_fact=None):

    session = Session()
    # проверяем, существует ли запись для этого показателя и периода
    try:
        exist = session.query(KPIFactValue).filter(KPIFactValue.kpi_code == kpi_fact["kpi_code"],
                                                   KPIFactValue.period_code == kpi_fact["period_code"]).all()
    except sqlalchemy.orm.exc.NoResultFound:
        exist = None
    except Exception as e:
        print "Ошибка в функции BMTObjects.save_kpi_fact_value. Чтение KPIFactValue. " + str(e)
        session.close()
        raise e

    exist = None

    if exist:
        print "KPI FACT такой объект существует, обновляем"
        try:
            # если значение не передано, присваиваем по умолчанию 0
            if kpi_fact.get("fact_value"):
                exist.fact_value = kpi_fact["fact_value"]

            if kpi_fact.get("create_date"):
                exist.create_date = kpi_fact["create_date"]

            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.save_kpi_fact_value. Обновление KPIFactValue. " + str(e)
            raise e
        finally:
            session.close()
    else:
        # создаем запись
        new = KPIFactValue()
        try:
            for key in kpi_fact.keys():
                new.__dict__[key] = kpi_fact[key]
            session.add(new)
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.save_kpi_fact_value. Создание нового KPITFactValue. " + str(e)
            raise e
        finally:
            session.close()


def calculate_auto_fact_values(for_kpi=None):

    return ""


class Event(Base):
    """
    Хранит данные о мероприятиях.
    Мероприятие может быть связано только с одной целью.

    """
    __tablename__ = "events"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    event_code = sqlalchemy.Column(sqlalchemy.String(10), unique=True)
    linked_goal_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    description = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    plan_result = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    fact_result = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    start_date = sqlalchemy.Column(sqlalchemy.DATETIME())
    end_date = sqlalchemy.Column(sqlalchemy.DATETIME())
    responsible = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    actors = sqlalchemy.Column(sqlalchemy.String(256), default="")

    def __init__(self):
        u = uuid.uuid4().get_hex().__str__()
        self.event_code = "".join(random.sample(u, 6))
        self.actors = 0
        self.description = ""
        self.end_date = None
        self.start_date = datetime.datetime.now()
        self.fact_result = ""
        self.linked_goal_code = ""
        self.name = ""
        self.plan_result = ""


def get_events(event_code=None):
    """
    Возвращает все мероприятия.

    :parameter event_code: код события

    :return:
    """
    events = dict()
    session = Session()
    try:
        if event_code:
            query = session.query(Event).filter(Event.event_code == event_code).all()
        else:
            query = session.query(Event).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено для Event(). BMTObjects.get_events(). %s" % str(e)
        return events
    except Exception as e:
        print "Ошибка в функции BMTObjects.get_events(). %s" % str(e)
        raise e
    else:
        if event_code:
            return query[0]
        else:
            for one in query:
                events[one.event_code] = one
            return events
    finally:
        session.close()


def create_new_event(event_fields):
    """
    Функция создания нового мероприятия.
    :return:
    """
    event = Event()

    session = Session()
    try:
        for key in event_fields.keys():
            event.__dict__[key] = event_fields[key]
        session.add(event)
        session.commit()
    except Exception as e:
        print "Ошибка в функции BMTObjects.create_new_event(). Мероприятие не записано. %s" % str(e)
        raise e
    else:
        # Добавляем запись в стратегическую карту
        smap = StrategicMap()
        smap.event_code = event.event_code
        smap.date = datetime.datetime.now()
        smap.map_code = current_strategic_map
        smap.version = VERSION
        try:
            session.add(smap)
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.create_new_event(). Strategic map не записана. %s" % str(e)
            raise e
    finally:
        session.close()

    return [True, ""]


def update_event(event_code, event_fields):
    """
    Функция изменения мероприятия.
    :return:
    """
    session = Session()
    try:
        query = session.query(Event).filter(Event.event_code == event_code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        return [False, "Нет такого мероприятия."]
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.update_event(). НАйдено много мероприятий с кодом: %s. %s" % (event_code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции BMTObjects.update_event(). %s" % str(e)
        raise e
    else:
        # Фактический результат заполняется при смене статуса. В отдельной функции
        try:
            query.actors = event_fields['actors']
            query.description = event_fields['description']
            query.end_date = event_fields['end_date']
            query.start_date = event_fields['start_date']
            query.name = event_fields['name']
            query.plan_result = event_fields['plan_result']
            query.linked_goal_code = event_fields['linked_goal_code']
            query.responsible = event_fields['responsible']
        except Exception as e:
            print "Ошибка в функции BMTObjects.update_event(). Не все параметры указаны. %s" % str(e)
            raise e

        try:
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.update_event(). Мероприятие не обновлено. %s" % str(e)
            raise e
    finally:
        session.close()

    return [True, ""]


def delete_event(event_code):
    """
    Функция удаления мероприятия.

    :return:
    """

    session = Session()
    try:
        query = session.query(Event).filter(Event.event_code == event_code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        return [False, "Нет такого мероприятия."]
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции BMTObjects.delete_event(). НАйдено много мероприятий с кодом: %s. %s" % (event_code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции BMTObjects.delete_event(). Поиск Event. %s" % str(e)
        raise e
    else:
        try:
            session.delete(query)
            session.commit()
        except Exception as e:
            print "Ошибка в функции BMTObjects.delete_event(). Удаление Event. %s" % str(e)
            raise e
        else:
            try:
                query1 = session.query(StrategicMap).filter(StrategicMap.event_code == event_code).delete()
            except Exception as e:
                print "Ошибка в функции BMTObjects.delete_event(). Поиск связи в Strategic Map. %s" % str(e)
                raise e
            else:
                try:
                    session.commit()
                except Exception as e:
                    print "Ошибка в функции BMTObjects.delete_event(). Удаление связи в Strategic Map. %s" % str(e)
                    raise e
    finally:
        session.close()


def check_access(subject, person):
    # Проверяем права доступ person к субъекту

    return [True, True]


def change_current_strategic_map(smap):
    # меняем текущую стратегическую карту
    global current_strategic_map
    current_strategic_map = smap


class MonitorDescription(Base):

    __tablename__= "monitor_desc"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    code = sqlalchemy.Column(sqlalchemy.String(10), default="", unique=True)
    name = sqlalchemy.Column(sqlalchemy.String(256), default="")
    description = sqlalchemy.Column(sqlalchemy.TEXT(), default="")
    owner = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # создатель и редактор
    status = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    viewers = sqlalchemy.Column(sqlalchemy.String(256), default="")  # кто видит монитор

    def __init__(self):
        u = uuid.uuid4().get_hex().__str__()
        self.code = "mn" + "".join(random.sample(u, 4))
        self.name = ""
        self.description = ""
        self.owner = 0
        self.status = 0
        self.viewers = ""


def get_monitor_desc(mon_code=None):

    session = Session()

    if mon_code:
        # Ищем описание монитора по коду
        try:
            resp = session.query(MonitorDescription).filter(MonitorDescription.code == mon_code).one()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "Ничего не найдено get_monitor_desc() для монитора: %s. %s" % (mon_code, str(e))
            return dict()
        except sqlalchemy.orm.exc.MultipleResultsFound as e:
            print "Ошибка в функции get_monitor_desc(). Найдено много мониторов с кодом: %s. %s" %\
                  (mon_code, str(e))
            raise e
        except Exception as e:
            print "Ошибка в функции get_monitor_desc(). %s" % str(e)
            raise e
        else:
            return resp
        finally:
            session.close()

    # конкретный код не указан, возвращаем все мониторы в виде словаря. Ключ: код монитора
    try:
        resp = session.query(MonitorDescription).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено get_monitor_desc(). %s" % str(e)
        return dict()
    except Exception as e:
        print "Ошибка в функции get_monitor_desc(). %s" % str(e)
        raise e
    else:
        mon = dict()
        for one in resp:
            mon[one.code] = one
        return mon
    finally:
        session.close()


def create_monitor(monitor_fields=None):

    session = Session()
    new = MonitorDescription()
    try:
        for key in monitor_fields.keys():
            new.__dict__[key] = monitor_fields[key]
        session.add(new)
        session.commit()
    except Exception as e:
        print "Ошибка в функции BMTObjects.create_monitor(). Монитор не записан. %s" % str(e)
        raise e
    else:
        return new.code
    finally:
        session.close()


def update_monitor_desc(code=None, name=None, desc=None, owner=None):

    session = Session()

    try:
        query = session.query(MonitorDescription).filter(MonitorDescription.code == code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        return [False, "Нет такого монитора."]
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "Ошибка в функции update_monitor_desc(). Найдено много мониторов с кодом: %s. %s" % (code, str(e))
        raise e
    except Exception as e:
        print "Ошибка в функции update_monitor_desc(). %s" % str(e)
        raise e
    else:
        try:
            query.name = name
            query.description = desc
            query.owner = owner
        except Exception as e:
            print "Ошибка в функции update_monitor_desc(). Не все параметры указаны. %s" % str(e)
            raise e

        try:
            session.commit()
        except Exception as e:
            print "Ошибка в функции update_monitor_desc(). Монитор не обновлен. %s" % str(e)
            raise e
    finally:
        session.close()


def delete_monitor(code=None):

    session = Session()
    try:
        query = session.query(MonitorDescription).filter(MonitorDescription.code == code).one()
    except sqlalchemy.orm.exc.NoResultFound as e:
        return [False, "Нет такого монитора."]
    except sqlalchemy.orm.exc.MultipleResultsFound as e:
        print "delete_monitor(). Найдено много мониторов с кодом: %s. %s" % (code, str(e))
        raise e
    except Exception as e:
        print "delete_monitor().Ошибка поиска монитора: %s. %s" % (code,str(e))
        raise e
    else:
        try:
            mon = session.query(Monitor).filter(Monitor.mon_code == code).all()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "Нет индикаторов для монитора %s." % code
            mon = list()
        except Exception as e:
            print "delete_monitor().Ошибка поиска индикаторов для монитора: %s. %s" % (code,str(e))
            raise e

        try:
            if mon:
                for one in mon:
                    session.delete(one)
            session.delete(query)
            session.commit()
        except Exception as e:
            print "delete_monitor(). Ошибка при удалении записей монитора. %s" % str(e)
            raise e
    finally:
        session.close()


class Monitor(Base):

    __tablename__ = "monitor"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    mon_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    kpi_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    opkpi_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    version = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date = sqlalchemy.Column(sqlalchemy.DATETIME(), default=datetime.datetime.now())

    def __init__(self):
        self.mon_code = ""
        self.kpi_code = ""
        self.opkpi_code = ""
        self.version = 0
        self.date = datetime.datetime.now()


def get_monitor_data(mon_code=None, period=None):
    """
        Возвращает данные о показателях входящих в монитор для вывода пользователю.
        Название показателей, план, факт, оценку по шкале.

    :param mon_code:
    :param period:
    :return:
    """

    """
        1. Список стратегических показателей в мониторе
        2. Для каждого показателя плановое значение на текущий период
        3. Для каждого показателя фактические значения за текущий период
        4. Для каждого показателя текущий процент факта от плана
        5. Для каждого показателя шкалу оценки
    """
    resp = get_monitor_indicators(mon_code=mon_code)
    mon = dict()
    if not period:
        period = define_period_new(datetime.datetime.now())

    # 1
    try:
        for one in resp["kpi"]:
            mon[one] = list()
            kpi = load_custom_goals_kpi(goal_code=None, kpi_code=one)[1]
            mon[one].append(kpi)  # добавляем объект показателя
    except Exception as e:
        print "Ошибка в функции get_monitor_data()1. %s" % str(e)
        raise e

    for one in mon.keys():
        # 2 план для текущего периода
        try:
            target = get_kpi_target_value(kpi_code=one, period_code=period[0])
        except Exception as e:
            print "Ошибка в функции get_monitor_data()2. %s" % str(e)
            raise e
        else:
            mon[one].append(target)
        # 3 факт для текущего периода
        try:
            fact = get_kpi_fact_values(for_kpi=one,period_code=period[0])
        except Exception as e:
            print "Ошибка в функции get_monitor_data()3. %s" % str(e)
            raise e
        else:
            mon[one].append(fact)

        # 4 отношени факта к плану %
        trend = float()
        if fact:
            trend = fact[0].fact_value
        else:
            trend = 0

        if target and target.first_value != 0:
            trend = trend/target.first_value*100
        mon[one].append(trend)

        # 5 цвет этого показателя на мониторе
        scale = mon[one][0].kpi_scale_type
        if fact and target and scale == 0 :
            try:
                if fact[0].fact_value >= target.first_value:
                    mon[one].append(SCALE_COLOR[scale][1])
                else:
                    mon[one].append(SCALE_COLOR[scale][0])
            except Exception as e:
                print "Ошибка в функции get_monitor_data()5. %s" % str(e)
                mon[one].append("000000")
        else:
            mon[one].append("000000")

    return mon


def get_monitor_indicators(mon_code=None):
    """
    Возвращает список показателей входящих в монитор.

    :param mon_code:
    :return:
    """
    session = Session()

    try:
        resp = session.query(Monitor).filter(Monitor.mon_code == mon_code).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено get_monitor_indicators(). %s" % str(e)
        return dict()
    except Exception as e:
        print "Ошибка в функции get_monitor_indicators(). %s" % str(e)
        raise e
    else:
        mon = dict([("kpi", list()), ("opkpi", list())])
        for one in resp:
            if one.kpi_code:
                mon["kpi"].append(one.kpi_code)
            if one.opkpi_code:
                mon["opkpi"].append(one.opkpi_code)
        return mon
    finally:
        session.close()


def update_monitor_indicators(mon_code=None, kpi=None, opkpi=None):

    if not kpi and not opkpi:
        return None

    session = Session()
    for_delete = [list(), list()]
    for_add = [list(), list()]
    try:
        indrs = get_monitor_indicators(mon_code=str(mon_code))
    except Exception as e:
        print "update_monitor_indicators(). Ошибка получения данных для монитора: %s." % str(mon_code), str(e.message)
        raise str(e)
    else:
        for one in kpi:
            if one not in indrs["kpi"]:
                for_add[0].append(one)

        for one in opkpi:
            if one not in indrs["opkpi"]:
                for_add[1].append(one)

        for one in indrs["kpi"]:
            if one not in kpi:
                for_delete[0].append(one)

        for one in indrs["opkpi"]:
            if one not in opkpi:
                for_delete[1].append(one)

        print for_delete
        print for_add

        try:
            if for_delete[0]:
                resp_kpi = session.query(Monitor).filter(and_(Monitor.kpi_code.in_(for_delete[0]),
                                                              Monitor.mon_code == mon_code)).all()
                for one in resp_kpi:
                    session.delete(one)
                session.commit()

            if for_delete[1]:
                resp_opkpi = session.query(Monitor).filter(and_(Monitor.opkpi_code.in_(for_delete[1]),
                                                                Monitor.mon_code == mon_code)).all()
                for one in resp_opkpi:
                    session.delete(one)
                session.commit()
        except Exception as e:
            print "Ошибка удаления показателя из монитора. %s" % str(e)
            raise e

        for one in for_add[0]:
            new = Monitor()
            new.mon_code = mon_code
            new.kpi_code = one
            try:
                session.add(new)
                session.commit()
            except Exception as e:
                print "Ошибка добавления стратегического показателя в монитор. %s " % str(e)
                raise e

        for one in for_add[1]:
            new = Monitor()
            new.mon_code = mon_code
            new.opkpi_code = one
            try:
                session.add(new)
                session.commit()
            except Exception as e:
                print "Ошибка добавления операционного показателя в монитор. %s " % str(e)
                raise e
        return "ok"
    finally:
        session.close()


class MotivationCardData(Base):

    __tablename__="motivation_card_data"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    user_id = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    group_id = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    user_approve = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    boss_approve = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    salary = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    salary_fix_p = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    salary_var_p = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    salary_fix = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    salary_var = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    edge1 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    edge2 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    edge3 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    var_edge_1 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    var_edge_2 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    var_edge_3 = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    status = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    date = sqlalchemy.Column(sqlalchemy.DATETIME())
    version = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def __init__(self):
        u = uuid.uuid4().get_hex().__str__()
        self.code = "mc" + "".join(random.sample(u, 4))
        self.user_id = 0
        self.group_id = 0
        self.user_approve = 0
        self.boss_approve = 0
        self.salary = 0
        self.salary_fix = 0
        self.salary_fix_p = 0
        self.salary_var = 0
        self.salary_var_p = 0
        self.edge1 = 0
        self.edge2 = 0
        self.edge3 = 0
        self.var_edge_1 = 0
        self.var_edge_2 = 0
        self.var_edge_3 = 0
        self.status = 0
        self.date = datetime.datetime.now()
        self.version = VERSION


def create_motivation_card(card_fields):
    """
    Создание карты мотивации

    :param card_fields: поля для заполнения.
    :return:
    """

    session = Session()
    new_card = MotivationCardData()
    try:
        for key in card_fields.keys():
            new_card.__dict__[key] = card_fields[key]
        session.add(new_card)
        session.commit()
    except Exception as e:
        print "Ошибка в функции BMTObjects.create_motivation_card(). Мотивационная карта не записана. %s" % str(e)
        raise e
    else:
        return ["ok", new_card.id]
    finally:
        session.close()


def get_motivation_cards(card_code=None, user_code=None):
    """
    Возвращает данные мотивационных карт. Если указан card_code, то возвращвет конкретный объект или None.

    :param card_code: код карты
    :param user_code: ИД пользователя
    :return:
    """

    session = Session()

    if card_code:
        # Ищем карту по коду
        try:
            resp = session.query(MotivationCardData).filter(MotivationCardData.code == card_code).one()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "Ничего не найдено get_motivation_cards() для карты: %s. %s" % (card_code, str(e))
            return dict()
        except sqlalchemy.orm.exc.MultipleResultsFound as e:
            print "Ошибка в функции get_motivation_cards(). Найдено много карт с кодом: %s. %s" %\
                  (card_code, str(e))
            raise e
        except Exception as e:
            print "Ошибка в функции get_motivation_cards(). %s" % str(e)
            raise e
        else:
            return resp
        finally:
            session.close()

    if user_code:
        # Ищем карту для пользователя
        try:
            resp = session.query(MotivationCardData).filter(MotivationCardData.user_id == user_code).all()
        except sqlalchemy.orm.exc.NoResultFound as e:
            print "Ничего не найдено get_motivation_cards() для пользователя: %s. %s" % (user_code, str(e))
            return dict()
        except Exception as e:
            print "Ошибка в функции get_motivation_cards(). %s" % str(e)
            raise e
        else:
            cards = dict()
            for one in resp:
                cards[one.code] = one
            return cards
        finally:
            session.close()

    # Ищем и возвращаем конкретную карту
    try:
        resp = session.query(MotivationCardData).all()
    except sqlalchemy.orm.exc.NoResultFound as e:
        print "Ничего не найдено get_motivation_cards(). %s" % str(e)
        return dict()
    except Exception as e:
        print "Ошибка в функции get_motivation_cards(). %s" % str(e)
        raise e
    else:
        cards = dict()
        for one in resp:
            cards[one.code] = one
        return cards
    finally:
        session.close()


class MotivationCardRecord(Base):
    __tablename__ = "motivation_card"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    kpi_code = sqlalchemy.Column(sqlalchemy.String(10), default="")
    weight = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    motivation_card_code = sqlalchemy.Column(sqlalchemy.String(10), default="")


def get_motivation_card_records(motivation_card):
    """
    Получить все записи о показателях для карты

    :param motivation_card:
    :return:
    """

    session = Session()
    records = dict()
    try:
        resp = session.query(MotivationCardRecord).filter(MotivationCardRecord.motivation_card_code ==
                                                          motivation_card).all()

    except Exception as e:
        print "Ошибка в функции update_kpi_in_motivation_card(). %s" % str(e)
        raise e
    else:
        for one in resp:
            records[one.kpi_code] = one
        return records
    finally:
        session.close()


def add_kpi_to_motivation_card(motivation_card, weight, kpi):
    """
    Добавление показателя в карту мотивации

    :param motivation_card:
    :param weight:
    :param kpi:
    :return:
    """

    session = Session()
    new_kpi = MotivationCardRecord()
    new_kpi.kpi_code = kpi
    new_kpi.motivation_card_code = motivation_card
    new_kpi.weight = weight
    try:
        session.add(new_kpi)
        session.commit()
    except Exception as e:
        print "Ошибка в функции add_kpi_to_motivation_card(). %s" % str(e)
        raise e
    finally:
        session.close()


def delete_kpi_from_motivation_card(motivation_card, kpi):
    """
    Удаляет показатель из карты мотивации

    :param motivation_card:
    :param kpi:
    :return:
    """

    session = Session()
    try:
        resp = session.query(MotivationCardRecord).filter(and_(MotivationCardRecord.kpi_code == kpi,
                                                               MotivationCardRecord.motivation_card_code ==
                                                               motivation_card)).one()
    except Exception as e:
        print "Ошибка в функции delete_kpi_from_motivation_card(). %s" % str(e)
        raise e
    else:
        session.delete(resp)
        session.commit()
    finally:
        session.close()


def update_kpi_in_motivation_card(motivation_card, weight, kpi):
    """
    Обновляет занчение веса показателя в карте мотивации

    :param motivation_card:
    :param weight:
    :param kpi:
    :return:
    """

    session = Session()
    try:
        resp = session.query(MotivationCardRecord).filter(and_(MotivationCardRecord.kpi_code == kpi,
                                                               MotivationCardRecord.motivation_card_code ==
                                                               motivation_card)).one()
    except Exception as e:
        print "Ошибка в функции update_kpi_in_motivation_card(). %s" % str(e)
        raise e
    else:
        resp.weight = weight
        session.commit()
    finally:
        session.close()

