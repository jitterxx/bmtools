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



goal = BMTObjects.load_custom_goals_kpi("dg7cd3")[0]

dd = {"name": str(goal.goal_name)}

print dd['name']
s = str(dd['name'])

j = 0
for i in s:
    print i
if j > 9 and s[i] == " ":
    j = 0
    print i, s[i]
else:
    j += 1
