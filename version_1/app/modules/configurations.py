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
current_strategic_map = "ent0"
KPI_SCALE_TYPE = {0: "Красный/Зеленый", 1: "Зеленый/Красный", 2: "Шкала (Красный/Желтый/Зеленый)",
                  3: "Шкала (Зеленый/Желтый/Красный)", 4: "Шкала (Красный/Зеленый/Красный)"}
CYCLES = {0: "Неделя", 1: "Месяц", 2: "Полгода", 3: "Год"}

MEASURES = {0: "Число", 1: "Проценты", 2: "Баллы"}

QUEUE_NAME = ''
QUEUE_BROKER = 'amqp://guest@localhost//'
QUEUE_BROKER_BACKEND = 'rpc://'
