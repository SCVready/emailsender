
import sqlite3

class sqlite_database:
	def __init__(self):
		self.con = None
		self.cur = None

	def connect(self):
		if not self.con:
			self.con = sqlite3.connect('/home/root/emailsender/email_data.db')
			self.cur = self.con.cursor()

	def create_email_table(self):
		self.cur.execute("CREATE TABLE IF NOT EXISTS EMAIL_DATA("  \
			"ID					INTEGER		PRIMARY KEY," \
			"ACTIVATE			INTEGER		NOT NULL," \
			"EMAIL_FROM			CHAR(250)	NOT NULL," \
			"PASSWORD			CHAR(250)	NOT NULL," \
			"EMAIL_TO			CHAR(250)	NOT NULL," \
			"SMTP_SERVER_URL	CHAR(250)	NOT NULL," \
			"SMTP_SERVER_PORT	INTEGER		NOT NULL);")
		self.con.commit()

	def get_email_data(self):
		self.cur.execute('SELECT * FROM EMAIL_DATA')
		return self.cur.fetchone()

	def set_email_data(self,activate,email_from,password,email_to,smtp_server_url,smtp_server_port):
		try:
			self.cur.execute('INSERT INTO EMAIL_DATA (ID,ACTIVATE,EMAIL_FROM,PASSWORD,EMAIL_TO,SMTP_SERVER_URL,SMTP_SERVER_PORT) \
				VALUES (%u, %u, "%s", "%s", "%s", "%s",%u);' % (0,activate,email_from,password,email_to,smtp_server_url,smtp_server_port))
			self.con.commit()
			return 0
		except:
			return 1


	def update_email_data(self,email_from,password,email_to,smtp_server_url,smtp_server_port):
		self.cur.execute('UPDATE EMAIL_DATA SET ' \
			'EMAIL_FROM="%s",PASSWORD="%s",EMAIL_TO="%s",SMTP_SERVER_URL="%s",SMTP_SERVER_PORT=%u '  \
			'WHERE ID=0;' % (email_from,password,email_to,smtp_server_url,smtp_server_port))
		self.con.commit()

	def activate_email_send(self,activate):
		self.cur.execute('UPDATE EMAIL_DATA SET ACTIVATE=%u WHERE ID=0;' % (activate))
		self.con.commit()
