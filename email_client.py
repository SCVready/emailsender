
import smtplib

class email_client:
	def __init__(self):
		self.email_from			= None
		self.password			= None
		self.email_to			= None
		self.smtp_server_url	= None
		self.smtp_server_port	= None

	def conf_email(self,email_from,password,email_to,smtp_server_url,smtp_server_port):
		self.email_from			= email_from
		self.password			= password
		self.email_to			= email_to
		self.smtp_server_url	= smtp_server_url
		self.smtp_server_port	= smtp_server_port

	def send_email(self,subject,body):
		email_text = """\
From: %s  
To: %s  
Subject: %s
%s
""" % (self.email_from, self.email_to, subject, body)		
		try:  
			server = smtplib.SMTP_SSL(self.smtp_server_url, self.smtp_server_port,timeout=3)
			server.ehlo()
			server.login(self.email_from, self.password)
			server.sendmail(self.email_from, self.email_to, email_text)
			server.close()
			return 0
		except:  
			return -1


