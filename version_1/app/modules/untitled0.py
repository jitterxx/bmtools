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

kpi = BMTObjects.calculate_target_values(for_kpi="kp635a", for_period=12016)

print kpi

session.close()