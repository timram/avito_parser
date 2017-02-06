import logging
import threading
from bs4 import BeautifulSoup
from datetime import datetime, timedelta	
from multiprocessing.dummy import Pool as ThreadPool
from get.vkgetters import getGroupId, getNoutPostId, getTechnPostId, getComments, getUserData
from check.vkcheckers import checkVkNouts, checkVkTv, checkVkMonitors
from mail.sends import sendingDecorator, sendErrorReport
from loghandlers.handlers import getFileHandler, getConsoleHandler
import time
import vk

prod_ids = {"nouts":getNoutPostId, "televizori":getTechnPostId, "monitori":getTechnPostId}
check_funcs = {"nouts":checkVkNouts, "televizori":checkVkTv, "monitori":checkVkMonitors}


class VkParser(threading.Thread):

	def __init__(self, **kwargs):
		threading.Thread.__init__(self)
		appId = "5812997"
		login = "rjckec@gmail.com"
		password = "2413timur"
		session = vk.AuthSession(app_id=appId, user_login=login, user_password=password)
		self.api = vk.API(session)
		self.groupId = getGroupId(self.api, "sevads")
		self.prodType = kwargs["prodType"]
		self.postId = prod_ids[self.prodType](self.api)
		self.checkFunc = check_funcs[self.prodType]
		self.subject = kwargs["subject"]
		self.count = kwargs["count"]
		self.numOfRequests = 0
		self.currTime = datetime.now()
		self.logger = logging.getLogger("vk_"+self.prodType)
		self.logger.setLevel(logging.DEBUG)
		self.logger.addHandler(getFileHandler("vk_"+self.prodType))
		self.logger.addHandler(getConsoleHandler())
		self.startTime = datetime.now()
		self.currTime = time.mktime(self.startTime.timetuple())
		#diff = self.startTime - timedelta(days=1)
		#self.todayFoundPosts = []


	def run(self):
		while True:
			try:
				self.getNewPosts()
				time.sleep(1200)
			except Exception as e:
				self.logger.error(repr(e))
				sendErrorReport(str(e) + self.subject)
				continue

	@sendingDecorator
	def getNewPosts(self):
		self.numOfRequests += 1
		self.logger.info("%d request to vk post of %s", self.numOfRequests, self.prodType)
		comments = getComments(self.api, self.groupId, self.postId, self.count)[1:]
		foundPosts = [self.getPostData(post) for post in comments if self.checkFunc(self, post)]
		#suitablePosts = [post for post in foundPosts if post not in self.todayFoundPosts]
		#self.todayFoundPosts.extend(suitablePosts)
		#self.restCurrTime()
		if len(foundPosts) == 0:
			return None
		self.currTime = time.mktime(self.datetime.now().timetuple())
		return suitablePosts

	def getPostData(self, post):
		userData = getUserData(self.api, post["uid"])
		userName = "{} {}".format(userData["first_name"], userData["last_name"])
		timeOfPost = post["date"]
		text = post["text"]
		photos = text[text.find("https://"):]
		if len(photos) == 1:
			photos = ""
		else:
			text = text[:text.find("https://")]
			photos = photos.split(' ')
			photos = ["https://vk.com/sevads?z={}%2Fwall-{}_{}".format(photo.split('/')[-1], self.groupId, post["cid"]) for photo in photos]
			photos = ',  '.join(photos)

		return {"userName":userName, "time":timeOfPost, "text":text, "photos":photos}

	def getBody(self, posts):
		body = []
		for post in sorted(posts, key=lambda rec: rec["time"]):
				body.append("Продавец: {}\nОписние: {}\nВремя публикации: {}\nФото: {}\n".format(post["userName"], post["text"], 
					time.ctime(post["time"]), post["photos"]))
		return '\n'.join(body)	

	def restCurrTime(self):
		if datetime.now().day != self.startTime.day:
			self.startTime = datetime.now()
			diff = self.startTime - timedelta(days=1)
			self.currTime = datetime(diff.year, diff.month, diff.day, 23, 30, 0)
			self.todayFoundPosts = [post for post in self.todayFoundPosts if time.ctime(int(post["time"])) > time.mktime(self.currTime.timetuple())]
			self.logger.handlers[0].stream.close()
			self.logger.removeHandler(self.logger.handlers[0])
			self.logger.addHandler(getFileHandler("vk_" + self.prodType))
