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
sql1 = "ALTER TABLE custom_kpi ADD COLUMN data_source VARCHAR(256) NULL AFTER cycle, " \
       "ADD COLUMN kpi_scale_type INT(11) NULL DEFAULT 0 AFTER data_source;"

sql2 = "ALTER TABLE kpi_target_values DROP COLUMN data_source, DROP COLUMN kpi_scale_type;" \
       "ALTER TABLE kpi_target_values ADD COLUMN period_code INT(11) NULL AFTER date;"


connection = BMTObjects.Engine.connect()
#result = connection.execute(sql)
#print result

result = connection.execute(sql1)
print result

result = connection.execute(sql2)
print result

connection.close()
