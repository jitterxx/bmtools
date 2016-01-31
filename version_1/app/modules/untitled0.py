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
import bmtools_objects as BMTObjects

reload(sys)
sys.setdefaultencoding("utf-8")
"""
start_date = "01.01.2016"
plan_period = 18
start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y").date()
print "Количество периодов: %s" % int(plan_period)
print "Стартовая дата: %s" % start_date
period_date = dict()
period_name = dict()

for one in range(1, int(plan_period) + 1):
    print "Год отчетного периода: %s" % (start_date.year + (one // 12))
    print "Месяц отчетного периода: %s" % (((start_date.month % 12) + one) - 12*(one // 12))
    print "Период: %s" % one

    period_date[one] = datetime.datetime(start_date.year + (one // 12),
                                         ((start_date.month % 12) + one) - 12*(one // 12), 1)

    if (period_date[one].month - 1) == 0:
        period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                           str(period_date[one].year - 1)
    else:
        period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                           str(period_date[one].year)

    print "Название отчетного периода: %s" % period_name[one]
    print "Отчетная дата периода: %s" % period_date[one]
    print "-----------------------------------------------------"
"""

BMTObjects.create_auto_target_values("kp79c4")
#BMTObjects.calculate_auto_target_values(for_kpi="kp79c4", for_period=1012016)