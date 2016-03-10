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

p = BMTObjects.make_periods_for_kpi_new(start_date=datetime.datetime.strptime("01.01.%s" % 2016, "%d.%m.%Y"),
                                        plan_period=12)


for one in p.values():
    print one[0]
    print one[1]
    print one[2]
    print "-----------------------"


print BMTObjects.define_period_new(date=datetime.datetime.now())

session.close()