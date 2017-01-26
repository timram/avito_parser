from mail.sender import Sender

RECEIVERS = ["rjckec@gmail.com"]#, "izmaylov.rusl@yandex.ru"]

def sendingDecorator(origin_func):
	def wrapper(self, *args, **kwargs):
		result = origin_func(self, *args, **kwargs)

		if result is None:
			self.logger.info("Theris not new %s after: %s\n", self.subject, self.currTime)
			return result
	
		body = self.getBody(result)

		self.logger.info("New posts of %s appeared\n %s", self.subject, body)
		
		for receiver in RECEIVERS:
			sender = Sender(sender="timurramazanov2@yandex.ru", password="2413timur", receiver=receiver, subject=self.subject)
			sender.addBody(body)
			sender.send()
			del sender

		return result
	
	return wrapper


def sendErrorReport(error):
	sender = Sender(sender="timurramazanov2@yandex.ru", password="2413timur", receiver="rjckec@gmail.com", subject="ПАРСЕР СДОХ")
	sender.addBody("ПАРСЕР СДОХ, {0}".format(error))
	sender.send()
	del sender