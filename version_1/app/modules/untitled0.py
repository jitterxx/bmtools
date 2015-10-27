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


user = BMTObjects.get_user_by_login("test")
user.read()
print "Группы: %s" % user.list_access_groups

session.close()