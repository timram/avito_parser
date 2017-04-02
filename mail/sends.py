from mail.sender import Sender
from mailAuthorizationReader import readAuthorizationInfo
import time

RECEIVERS = ["rjckec@gmail.com"]#, "izmaylov.rusl@yandex.ru"]
authInfo = readAuthorizationInfo("mail_authorization.info")
print(authInfo)

def sendingDecorator(origin_func):
	def wrapper(self, *args, **kwargs):
		result = origin_func(self, *args, **kwargs)
		self.lock.acquire()
		if result is None:
			self.logger.info("Theris not new %s after: %s\n", self.subject, self.currTime)
			self.lock.release()
			return result
	
		body = self.getBody(result)

		self.logger.info("New posts of %s appeared\n %s", self.subject, body)
		
		for receiver in RECEIVERS:
			sender = Sender(sender=authInfo["login"], password=authInfo["password"], 
				receiver=receiver, subject=self.subject)
			sender.addBody(body)
			sender.send()

		time.sleep(1)
		self.lock.release()
		return result
	
	return wrapper


def sendErrorReport(error):
	sender = Sender(sender=authInfo["login"], password=authInfo["password"],
		receiver="rjckec@gmail.com", subject="ПАРСЕР СДОХ")
	sender.addBody("ПАРСЕР СДОХ, {0}".format(error))
	sender.send()
	del sender