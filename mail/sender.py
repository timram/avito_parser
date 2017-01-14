# -*- coding: utf-8 -*-
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
"""this class can connect to gmail server and send mails to any adress """

class Sender(object):
	def __init__(self, **kwargs):
		self.password = kwargs["password"]
		self.sender = kwargs["sender"]
		self.receiver = kwargs["receiver"]
		self.message = MIMEMultipart()
		self.message["From"] = self.sender
		self.message["To"] = self.receiver
		self.message["Subject"] = kwargs["subject"]

	def addBody(self, body):
		self.message.attach(MIMEText(body, "plain"))

	def addFile(self, filename):
		attachment = open(filename, "rb")

		part = MIMEBase("application", "octet-stream")
		part.set_payload(attachment.read())
		encoders.encode_base64(part)
		part.add_header("Content-Disposition", "attachment; filename= %s" % filename)

		self.message.attach(part)

	def send(self):
		server = smtplib.SMTP_SSL("smtp.yandex.com", 465)	
		print("Connected to the yandex server")
		server.ehlo()
		server.login(self.sender, self.password)
		server.sendmail(self.message["From"], self.message["To"], self.message.as_string())
		print("message delivered to %s" %self.receiver)
		server.quit()

if __name__ == "__main__":
	import sys
	sender = Sender(sender="timurramazanov2@yandex.ru", password="2413timur", receiver="rjckec@gmail.com", subject="TEST")
	sender.addBody("САМОЕ Тестовое письмо димочке 2 ")
	sender.send()
