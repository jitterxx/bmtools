# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:23:47 2015

@author: sergey
"""

sql_uri = 'mysql://bmtools:Cthutq123@localhost/bmtools?charset=utf8'
def_industry = {"1": "Дистрибьюция"}
industry_goals = {"1": ["g1", "g2", "g3", "g4"]}
persons = {0: "", 1: "Фомин Сергей", 2: "Жукова Вера"}
perspectives = {0: "Финансы", 1: "Клиенты", 2: "Процессы", 3: "Персонал"}
enterprise_strategic_map = "ent0"
current_strategic_map = enterprise_strategic_map
KPI_SCALE_TYPE = {0: "Красный/Зеленый", 1: "Зеленый/Красный", 2: "Шкала (Красный/Желтый/Зеленый)",
                  3: "Шкала (Зеленый/Желтый/Красный)", 4: "Шкала (Красный/Зеленый/Красный)"}
CYCLES = {0: "Неделя", 1: "Месяц", 2: "Полгода", 3: "Год"}

MEASURES = {0: "Число", 1: "Проценты", 2: "Баллы"}

VERSION = 0

QUEUE_NAME = ''
QUEUE_BROKER = 'amqp://guest@localhost//'
QUEUE_BROKER_BACKEND = 'rpc://'

users = dict()


class User():
    id = int()
    name = str()
    login = str()

    def __init__(self):
        self.id = 0
        self.name = ""
        self.login = ""

    def create(self, id, name, login):
        self.id = id
        self.name = name
        self.login = login
        return self

users[0] = User()
users[1] = User().create(1, "Фомин Сергей", "sergey")
users[2] = User().create(2, "Жукова Вера", "vera")
users[3] = User().create(3, "Тестовый пользователь", "test")