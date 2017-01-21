import logging
import threading
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
from get.getters import getHtml, getTitle, getLink, getPublicationTime, getPrice, getName
from check.checkers import checkNoutPost, checkTvPost
from mail.sends import sendingDecorator, sendErrorReport
from loghandlers.handlers import getFileHandler, getConsoleHandler
import time

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

LOGGER.addHandler(getFileHandler())

LOGGER.addHandler(getConsoleHandler())

FINISHED = False
ERROR = "error"

class AvitoParser(threading.Thread):

	def __init__(self, **kwargs):
		threading.Thread.__init__(self)
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
		

	def run(self):
		global FINISHED
		while not FINISHED:
			try:
				self.getNewPosts()
				time.sleep(1200)
			except Exception as e:
				FINISHED = True
				ERROR = str(e)

	@sendingDecorator
	def getNewPosts(self):
		self.numOfRequests += 1
		logging.info("%d request to %s", self.numOfRequests, self.url)
		soup = BeautifulSoup(getHtml(self.url), "lxml")
		catalog = soup.find("div", class_="catalog-list")
		records = catalog.find_all("div", class_="item")
		descriptions = [record.find("div", class_="description") for record in records[:5]]
		pool = ThreadPool(4)
		posts = pool.map(self.getPostData, descriptions)
		pool.close()
		pool.join()
		suitablePosts = [post for post in posts if self.checkFunc(self, post) and post not in self.todayFoundPosts]
		self.todayFoundPosts.extend(suitablePosts)
		self.restCurrTime()
		if len(suitablePosts) == 0:
			return None
		return suitablePosts

	def getPostData(self, description):
		post = {"title":getTitle(description), "link":self.baseUrl + getLink(description), "time":getPublicationTime(description), 
		"price":getPrice(description)}
		post["name"] = getName(post["link"])
		return post

	def restCurrTime(self):
		if datetime.now().day != self.startTime.day:
			self.startTime = datetime.now()
			diff = self.startTime - timedelta(days=1)
			self.currTime = datetime(diff.year, diff.month, diff.day, 23, 30, 0)
			self.todayFoundPosts = [post for post in self.todayFoundPosts if post["time"] > self.currTime]
			LOGGER.handlers[0].stream.close()
			LOGGER.removeHandler(LOGGER.handlers[0])
			LOGGER.addHandler(getFileHandler())


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
	parsers = [AvitoParser(**noutsParams), AvitoParser(**tvParams), AvitoParser(**monitorParams)]
	
	for parser in parsers:
		parser.start()

	for parser in parsers:
		parser.join()

	sendErrorReport(ERROR)

	"""
	while True:
		try:
			nouts.getNewPosts()
			tvs.getNewPosts()
			monitors.getNewPosts() 
			time.sleep(1200)
		except Exception as e:
			logging.error("%s\n", e)
			sendErrorReport(str(e))
			break
	"""