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

resp = session.query(BMTObjects.Custom_goal).filter(BMTObjects.Custom_goal.code == "dg0a4d").all()

for one in resp:
    print one

session.close()

