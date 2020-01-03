#!/usr/bin/env python3

import threading
import pymysql
from datetime import datetime,timedelta
#连接数据库

db = pymysql.connect("localhost", "root", "root", "MarkManagement", charset='utf8')

cursor = db.cursor()






def deleteToken():
	now = datetime.now()
	old = now - timedelta(days=30)
	time = str(old)
	sql = "DELETE FROM t_Token WHERE create_time < '%s'" %(time)
	try:
		print('delete success')
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
	timer = threading.Timer(24*60*60,deleteToken)
	timer.start()
	
if __name__ == "__main__":

	deleteToken()
