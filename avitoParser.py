import logging
import threading
from bs4 import BeautifulSoup
from datetime import datetime, timedelta	
from multiprocessing.dummy import Pool as ThreadPool
from get.getters import getHtml, getTitle, getLink, getPublicationTime, getPrice, getName
from check.checkers import checkNoutPost, checkTvPost
from mail.sends import sendingDecorator, sendErrorReport
from loghandlers.handlers import getFileHandler, getConsoleHandler
import time

check_funcs = {"noutbuki":checkNoutPost, "televizory_i_proektory":checkTvPost, "monitory":checkNoutPost}

class AvitoParser(threading.Thread):

	def __init__(self, **kwargs):
		threading.Thread.__init__(self)
		self.baseUrl = "https://www.avito.ru" 
		self.city = kwargs["city"]
		self.maxPrice = kwargs["maxPrice"]
		self.minPrice = kwargs["minPrice"]
		self.subject = kwargs["subject"] 
		self.url = kwargs["url"] 
		self.prodType = self.url.split('/')[-1]
		self.checkFunc = check_funcs[self.prodType]
		self.numOfRequests = 0
		self.startTime = datetime.now()
		diff = self.startTime - timedelta(days=1)
		self.currTime = datetime(diff.year, diff.month, diff.day, 23, 30, 0)
		self.todayFoundPosts = []
		self.logger = logging.getLogger(self.prodType)
		self.logger.setLevel(logging.DEBUG)
		self.logger.addHandler(getFileHandler(self.prodType))
		self.logger.addHandler(getConsoleHandler())
		

	def run(self):
		while True:
			try:
				self.getNewPosts()
				time.sleep(1200)
			except Exception as e:
				self.logger.error(e)
				sendErrorReport(str(e) + self.subject)
				break

	@sendingDecorator
	def getNewPosts(self):
		self.numOfRequests += 1
		self.logger.info("%d request to %s", self.numOfRequests, self.url)
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

	def getBody(self, posts):
		body = []
		for post in sorted(posts, key=lambda rec: rec["time"]):
			if post["price"] == 0:
				post["price"] = "Цена договорная"
			body.append("Цена: {} руб.\nИмя продовца: {}\nОписние: {}\nВремя публикации: {}\nСсылка: {}\n".format(post["price"], post["name"], 
				post["title"], post["time"], post["link"]))
		return '\n'.join(body)

	def restCurrTime(self):
		if datetime.now().day != self.startTime.day:
			self.startTime = datetime.now()
			diff = self.startTime - timedelta(days=1)
			self.currTime = datetime(diff.year, diff.month, diff.day, 23, 30, 0)
			self.todayFoundPosts = [post for post in self.todayFoundPosts if post["time"] > self.currTime]
			self.logger.handlers[0].stream.close()
			self.logger.removeHandler(self.logger.handlers[0])
			self.logger.addHandler(getFileHandler(self.prodType))