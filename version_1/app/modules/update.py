# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 17:04:18 2015

@author: sergey
"""
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import bmtools_objects as BMTObjects
import cherrypy
import datetime
import json
import re

#sql = "ALTER TABLE strategic_maps_desc ADD COLUMN draw_data TEXT NULL AFTER department;"
sql1 = "ALTER TABLE custom_kpi " \
       "ADD COLUMN data_source VARCHAR(256) NULL AFTER cycle, " \
       "ADD COLUMN kpi_scale_type INT(11) NULL DEFAULT 0 AFTER data_source;"

sql2 = "ALTER TABLE kpi_target_values " \
       "DROP COLUMN data_source, DROP COLUMN kpi_scale_type;" \
       "ALTER TABLE kpi_target_values " \
       "ADD COLUMN period_code INT(11) NULL AFTER date;"

sql3 = "ALTER TABLE strategic_maps_desc " \
       "ADD COLUMN start_date DATETIME NULL AFTER department," \
       "ADD COLUMN cycle INT(11) NULL DEFAULT 0 AFTER start_date," \
       "ADD COLUMN cycle_count INT(11) NULL DEFAULT 0 AFTER cycle;"

sql4 = "ALTER TABLE `bmtools`.`kpi_target_values`" \
       "ADD COLUMN `period_name` VARCHAR(256) NULL AFTER `period_code`;"


connection = BMTObjects.Engine.connect()
# result = connection.execute(sql)
# print result

# result = connection.execute(sql1)
# print result
try:
    result = connection.execute(sql2)
except Exception as e:
    print e.message, e.args
else:
    print result

try:
    result = connection.execute(sql3)
except Exception as e:
    print e.message, e.args
else:
    print result

try:
    result = connection.execute(sql4)
except Exception as e:
    print e.message, e.args
else:
    session = BMTObjects.Session()

    resp = session.query(BMTObjects.KPITargetValue).all()
    for one in resp:
        if one.period_name:
            if (one.date.month - 1) == 0:
                one.period_name = str(BMTObjects.PERIOD_NAME[one.date.month - 1]) + " " + str(one.date.year - 1)
            else:
                one.period_name = str(BMTObjects.PERIOD_NAME[one.date.month - 1]) + " " + str(one.date.year)

    session.commit()

    session.close()
    print result

connection.close()

