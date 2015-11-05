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

QUEUE_NAME = ''
QUEUE_BROKER = 'amqp://guest@localhost//'
QUEUE_BROKER_BACKEND = 'rpc://'
