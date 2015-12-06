# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:23:47 2015

@author: sergey
"""

sql_uri = 'mysql://bmtools:Cthutq123@localhost/bmtools?charset=utf8'
def_industry = {"1": "Дистрибьюция"}
industry_goals = {"1": ["g1", "g2", "g3", "g4"]}
persons = {0: "", 1: "замените меня", 2: "замените меня", 3: "замените меня", 4: "замените меня"}

perspectives = {0: "Финансы", 1: "Клиенты", 2: "Процессы", 3: "Персонал"}
PERSPECTIVE_COLORS = ["#CC6666", "#669966", "#336699", "#CC9966"]

enterprise_strategic_map = "ent0"
current_strategic_map = enterprise_strategic_map
KPI_SCALE_TYPE = {0: "Красный/Зеленый", 1: "Зеленый/Красный", 2: "Шкала (Красный/Желтый/Зеленый)",
                  3: "Шкала (Зеленый/Желтый/Красный)", 4: "Шкала (Красный/Зеленый/Красный)"}
CYCLES = {0: "Неделя", 1: "Месяца(ев)", 2: "Квартал", 3: "Полгода", 4: "Год"}

MEASURES = {0: "Штуки", 1: "Проценты", 2: "Рубли", 3: "Баллы"}

GOAL_TYPE = {0: "lib", 1: "custom"}

GOAL_EDIT_FLAG = {0: "Нельзя изменять KPI", 1: "Можно изменять KPI"}

PERIOD_NAME = ["Декабрь", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

VERSION = 0

QUEUE_NAME = ''
QUEUE_BROKER = 'amqp://guest@localhost//'
QUEUE_BROKER_BACKEND = 'rpc://'
