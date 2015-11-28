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

sql = "ALTER TABLE strategic_maps_desc ADD COLUMN draw_data TEXT NULL AFTER department;"

connection = BMTObjects.Engine.connect()
result = connection.execute(sql)
print result

connection.close()
