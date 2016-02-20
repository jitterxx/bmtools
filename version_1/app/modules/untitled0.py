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


session = BMTObjects.Session()

p = BMTObjects.make_periods_for_kpi_new(start_date=datetime.datetime.now(), plan_period=12)

for one in p.values():
    print one[0]
    print one[1]
    print one[2]
    print "-----------------------"


print BMTObjects.define_period_new(date=datetime.datetime.now())


try:
    resp = session.query(BMTObjects.KPITargetValue).all()
except Exception as e:
    raise e

for one in resp:
    p_month = int(one.period_code) // 10000
    p_year = int(one.period_code) % 10000
    new = list()

    if 12 >= p_month >= 1:
        print "Старый код периода: %s" % one.period_code
        print "Старое название: %s" % one.period_name

        if p_month == one.date.month:
            print "Это старый расчет периода. Пересчитываем!"
            if p_month - 1 == 0:
                p_month = 12
                p_year -= 1
            else:
                p_month -= 1

            print "Новый код: %s" % (str(p_month) + str(p_year))
            new.append(str(p_month) + str(p_year))
            print "Новое название: %s" % (BMTObjects.PERIOD_NAME[p_month] + str(p_year))
            new.append(BMTObjects.PERIOD_NAME[p_month] + " " + str(p_year))
            print "--------------------------"
            try:
                one.period_code = new[0]
                session.commit()
            except Exception as e:
                raise e
        else:
            print "Это новый расчет. Дальше."


try:
    resp = session.query(BMTObjects.KPIFactValue).all()
except Exception as e:
    raise e

for one in resp:
    p_month = int(one.period_code) // 10000
    p_year = int(one.period_code) % 10000
    if p_month - 1 == 0:
        p_month = 12
        p_year -= 1
    else:
        p_month -= 1

    print "Old: %s" % one.period_code
    print "New: %s" % (str(p_month) + str(p_year))

    try:
        one.period_code = str(p_month) + str(p_year)
        # session.commit()
    except Exception as e:
        raise e



session.close()
