#!/usr/bin/env python

import time
import json
import syslog

from email_client import email_client
from sqlite_db import sqlite_database
from redis_db import redis_database

#Global Variables
activate			= None
email_from			= None
password			= None
email_to			= None
smtp_server_url		= None
smtp_server_port	= None

#Init syslog
syslog.openlog(logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL1)

#Create clases
sqlite_db = sqlite_database()
redis_db = redis_database()
email_sender = email_client()

#Connect to DBs
sqlite_db.connect()
redis_db.connect()

#Init SQlite Table
sqlite_db.create_email_table()
sqlite_db.set_email_data(0,'','','','',0)

#Read SQlite Table
data = sqlite_db.get_email_data()

activate 			= data[1]
email_from			= data[2]
password			= data[3]
email_to			= data[4]
smtp_server_url		= data[5]
smtp_server_port	= data[6]

#Update RedisDB
redis_db.set_var('send_email_activate',activate)
redis_db.set_var('email_from',email_from)
redis_db.set_var('password',password)
redis_db.set_var('email_to',email_to)
redis_db.set_var('smtp_server_url',smtp_server_url)
redis_db.set_var('smtp_server_port',smtp_server_port)

#Config email sender class
email_sender.conf_email(email_from,password,email_to,smtp_server_url,smtp_server_port)

redis_db.subscribe('email_activate')
redis_db.subscribe('email_change_data')
redis_db.subscribe('email_send_det')
redis_db.subscribe('email_send_test')

syslog.syslog(syslog.LOG_NOTICE, 'Email sender Started successfully')

while True:
		message = redis_db.get_message()
		if message and message['type'] == 'pmessage':
			if message['channel'] == 'email_change_data':
				data = json.loads(message['data'])

				email_from			= data['email_from']
				password			= data['password']
				email_to			= data['email_to']
				smtp_server_url		= data['smtp_server_url']
				smtp_server_port	= int(data['smtp_server_port'])
				
				#Update SQlite Table
				sqlite_db.update_email_data(email_from,password,email_to,smtp_server_url,smtp_server_port)

				#Update Redis values
				redis_db.set_var('email_from',email_from)
				redis_db.set_var('password',password)
				redis_db.set_var('email_to',email_to)
				redis_db.set_var('smtp_server_url',smtp_server_url)
				redis_db.set_var('smtp_server_port',smtp_server_port)

				email_sender.conf_email(email_from,password,email_to,smtp_server_url,smtp_server_port)

				redis_db.publish('event_success','Email data changed')
				syslog.syslog(syslog.LOG_NOTICE, 'Email data changed successfully')

			elif message['channel'] == 'email_send_det':
				if activate:
					error = email_sender.send_email('WARNING: An intrusion occurs','PresenceOS has detected motion on the camera spot.' \
					 'Please Check PresenceOS Web to verify the detection.')
					if not error:
						syslog.syslog(syslog.LOG_NOTICE, 'Email sended successfully')
					else:
						syslog.syslog(syslog.LOG_ERR, 'ERROR sending email')

			elif message['channel'] == 'email_send_test':
				error = email_sender.send_email('Test','Prueba')
				if not error:
					syslog.syslog(syslog.LOG_NOTICE, 'Email sended successfully')
					redis_db.publish('event_success','Email sended successfully')
				else:
					syslog.syslog(syslog.LOG_ERR, 'ERROR sending email')
					redis_db.publish('event_error','ERROR sending email')
			elif message['channel'] == 'email_activate':
				if message['data'] == '1':
					activate = 1
					syslog.syslog(syslog.LOG_NOTICE, 'Emailsender activated')
				elif message['data'] == '0':
					activate = 0
					syslog.syslog(syslog.LOG_NOTICE, 'Emailsender deactivated')
				sqlite_db.activate_email_send(activate)
				redis_db.set_var('send_email_activate',activate)
		else:
			time.sleep(0.05)