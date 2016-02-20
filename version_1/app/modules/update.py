# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 17:04:18 2015

@author: sergey
"""
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import bmtools_objects as BMTObjects

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

sql4 = "ALTER TABLE `kpi_target_values`" \
       "ADD COLUMN `period_name` VARCHAR(256) NULL AFTER `period_code`;"


sql5 = "CREATE TABLE `motivation_card_data` (  `id` int(11) NOT NULL AUTO_INCREMENT,  `code` varchar(10) DEFAULT NULL," \
       "  `user_id` int(11) DEFAULT '0',  `group_id` int(11) DEFAULT '0',  `user_approve` int(11) DEFAULT '0'," \
       "  `boss_approve` int(11) DEFAULT '0',  `salary` int(11) DEFAULT '0',  `salary_fix_p` int(11) DEFAULT '0'," \
       "  `salary_var_p` int(11) DEFAULT '0',  `salary_fix` int(11) DEFAULT '0',  `salary_var` int(11) DEFAULT '0'," \
       "  `edge1` int(11) DEFAULT '0',  `edge2` int(11) DEFAULT '0',  `edge3` int(11) DEFAULT '0'," \
       "  `var_edge_1` int(11) DEFAULT '0',  `var_edge_2` int(11) DEFAULT '0',  `var_edge_3` int(11) DEFAULT '0'," \
       "  `status` int(11) DEFAULT '0',  `date` datetime DEFAULT NULL,  `version` int(11) DEFAULT '0'," \
       "  PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;" \
       "  CREATE TABLE `motivation_card` ( `id` int(11) NOT NULL AUTO_INCREMENT,  " \
       "  `kpi_code` varchar(10) DEFAULT NULL,  `weight` int(11) DEFAULT NULL," \
       "  `motivation_card_code` varchar(10) DEFAULT NULL,  PRIMARY KEY (`id`)" \
       ") ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;"


sql6 = "ALTER TABLE `kpi_target_values` ADD COLUMN `formula` VARCHAR(256) NULL AFTER `second_value`;" \
       "UPDATE `kpi_target_values` SET `second_value`= `first_value` WHERE id >0;"

sql7 = "DROP TABLE `fact_value`;"

sql8 = "ALTER TABLE `custom_kpi` ADD COLUMN `fact_cycle` INT(11) NOT NULL DEFAULT 2 AFTER `fact_responsible`;"

sql9 = "ALTER TABLE `fact_values` CHANGE COLUMN `period` `period_code` VARCHAR(256) NULL DEFAULT NULL ;"





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
    print result
    session = BMTObjects.Session()

    resp = session.query(BMTObjects.KPITargetValue).all()
    for one in resp:
        one.period_code = str(one.date.month) + str(one.date.year)
        if not one.period_name:
            if (one.date.month - 1) == 0:
                one.period_name = str(BMTObjects.PERIOD_NAME[one.date.month - 1]) + " " + str(one.date.year - 1)
            else:
                one.period_name = str(BMTObjects.PERIOD_NAME[one.date.month - 1]) + " " + str(one.date.year)

    session.commit()

    session.close()

try:
    result = connection.execute(sql5)
except Exception as e:
    print e.message, e.args
else:
    print result

# Добавление поля формула в целевые значения для вычисления квартальны, полу и годовых показателей автоматически
# Скопировать все first_value в second_value для KPI Target values
try:
    result = connection.execute(sql6)
except Exception as e:
    print e.message, e.args
else:
    print result

# Подготовка БД для хранения фактических результатов. Удаление старой таблицы факта, создание новой
try:
    result = connection.execute(sql7)
except Exception as e:
    print e.message, e.args
else:
    print result

BMTObjects.create_tables()

# Добавление поля fact_cycle - цикл сбора факта, для показателя
try:
    result = connection.execute(sql8)
except Exception as e:
    print e.message, e.args
else:
    print result

# Создание новых таблиц для объектов Monitor
BMTObjects.create_tables()

# исправления в названии столбца в таблице fact_values
try:
    result = connection.execute(sql9)
except Exception as e:
    print e.message, e.args
else:
    print result



connection.close()

