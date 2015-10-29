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


st, shift = BMTObjects.get_structure_sorted()
for one in st:
    print one.id, one.parentid, one.org_name

print shift.__len__()

session.close()