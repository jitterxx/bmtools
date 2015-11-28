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


s = "Цель для подразделения 1 ее надо перенести"
ss = ""
print len(s)
for m in s.split(" "):
    print m
    if len(m) > 10:
        ss += "\n" + m
    else:
        ss += " " + m

print ss