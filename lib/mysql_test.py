# -*- coding: utf-8 -*-

import MySQLdb
import os
#os.startfile('myfile.py')

con = MySQLdb.connect(host='45.78.57.254', user='', passwd='', db='poem')

cursor = con.cursor()

sql = "select * from pluralpoem"

cursor.execute(sql)

row = cursor.fetchone()
rows = cursor.fetchall()
for i in rows:
    print "list::", i
print row

cursor.close()

con.close()
