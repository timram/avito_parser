import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
from multiprocessing.dummy import Pool as ThreadPool
from get.getters import getHtml, getTitle, getLink, getPublicationTime, getPrice
from check.checkers import checkNoutPost, checkTvPost
from mail.mail import Sender
import time

logging.basicConfig(
	format="%(levelname)s: %(asctime)s : %(message)s",
	datefmt="%m/%d/%Y %I:%M:%S %p", 
	filename="loggers/avito_parser.log", 
	filemode='w',
	level=logging.DEBUG
)

RECEIVERS = ["rjckec@gmail.com", "izmaylov.rusl@yandex.ru"]

def sending(origin_func):
	def wrapper(self, *args, **kwargs):
		result = origin_func(self, *args, **kwargs)
		if result is None:
			print("Theris not new {0} after: {1}".format(self.subject, self.currTime))
			logging.info("Theris not new %s after: %s\n", self.subject, self.currTime)
			return result
		body = []
		for post in sorted(result, key=lambda rec: rec["time"]):
			if post["price"] == 0:
				post["price"] = "Цена договорная"
			body.append("Цена: {0} руб.\nОписние: {1}\nВремя публикации: {2}\nСсылка: {3}\n".format(post["price"], post["title"], 
				post["time"], post["link"]))
		body = '\n'.join(body)
		print("New posts of %s appeared\n %s\n", self.subject, body)
		logging.info("New posts of %s appeared\n %s", self.subject, body)
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

class AvitoParser(object):

	def __init__(self, **kwargs):
		self.baseUrl = "https://www.avito.ru" 
		self.city = kwargs["city"]
		self.maxPrice = kwargs["maxPrice"]
		self.minPrice = kwargs["minPrice"]
		self.subject = kwargs["subject"] 
		self.url = kwargs["url"] 
		self.checkFunc = kwargs["check_func"]
		self.numOfRequests = 0
		self.startTime = datetime.now()
		diff = self.startTime - timedelta(days=1)
		self.currTime = datetime(diff.year, diff.month, diff.day, 23, 30, 0)
		self.todayFoundPosts = []
		

	@sending
	def getNewPosts(self):
		self.numOfRequests += 1
		logging.info("%d request to %s", self.numOfRequests, self.url)
		soup = BeautifulSoup(getHtml(self.url), "lxml")
		catalog = soup.find("div", class_="catalog-list")
		records = catalog.find_all("div", class_="item")
		descriptions = [record.find("div", class_="description") for record in records]
		posts = [{"title":getTitle(description), "link":self.baseUrl + getLink(description), "time":getPublicationTime(description), 
		"price":getPrice(description)} for description in descriptions] 
		suitablePosts = [post for post in posts if self.checkFunc(self, post) and post not in self.todayFoundPosts]
		self.todayFoundPosts.extend(suitablePosts)
		self.restCurrTime()
		if len(suitablePosts) == 0:
			return None
		return suitablePosts

	def restCurrTime(self):
		if datetime.now().day != self.startTime.day:
			self.startTime = datetime.now()
			diff = self.startTime - timedelta(days=1)
			self.currTime = datetime(diff.year, diff.month, diff.day, 23, 30, 0)
			self.todayFoundPosts = [post for post in self.todayFoundPosts if post["time"] > self.currTime]

if __name__ == "__main__":
	os.system("clear")
	noutsParams = {
		"city": "sevastopol", 
		"subject": "НОУТБУКИ СЕВАСТОПОЛЬ", 
		"maxPrice": 20000, 
		"minPrice": 2700, 
		"url": "https://www.avito.ru/sevastopol/noutbuki",
		"check_func": checkNoutPost
	}

	tvParams = {
		"city": "sevastopol", 
		"subject": "ТЕЛЕВИЗОРЫ СЕВАСТОПОЛЬ", 
		"maxPrice": 25000, 
		"minPrice": 0, 
		"url": "https://www.avito.ru/sevastopol/audio_i_video/televizory_i_proektory",
		"check_func": checkTvPost
	}

	monitorParams = {
		"city": "sevastopol", 
		"subject": "МОНИТОРЫ СЕВАСТОПОЛЬ", 
		"maxPrice": 5000, 
		"minPrice": 0, 
		"url": "https://www.avito.ru/sevastopol/tovary_dlya_kompyutera/monitory",
		"check_func": checkNoutPost
	}
	logging.info("\nStart new parse session\n")
	nouts = AvitoParser(**noutsParams)
	tvs = AvitoParser(**tvParams)
	monitors = AvitoParser(**monitorParams)
	while True:
		try:
			nouts.getNewPosts()
			tvs.getNewPosts()
			monitors.getNewPosts() 
			time.sleep(1200)
		except Exception as e:
			logging.error("%s\n", e)
			break
