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
import traceback

prod_ids = {"nouts":getNoutPostId, "televizori":getTechnPostId, "monitori":getTechnPostId}
check_funcs = {"nouts":checkVkNouts, "televizori":checkVkTv, "monitori":checkVkMonitors}


class VkParser(threading.Thread):

	def __init__(self, lock, **kwargs):
		threading.Thread.__init__(self)
		self.lock = lock
		appId = "5812997"
		login = ""
		password = ""
		session = vk.AuthSession(app_id=appId, user_login=login, user_password=password)
		self.api = vk.API(session)
		self.groupId = getGroupId(self.api, "sevads")
		self.prodType = kwargs["prodType"]
		self.checkFunc = check_funcs[self.prodType]
		self.subject = kwargs["subject"]
		self.count = kwargs["count"]
		self.numOfRequests = 0
		self.logger = logging.getLogger("vk_"+self.prodType)
		self.logger.setLevel(logging.DEBUG)
		self.logger.addHandler(getFileHandler("vk_"+self.prodType))
		self.logger.addHandler(getConsoleHandler())
		self.startTime = datetime.now()
		self.currTimeInSec = time.time() - (20 * 60 * 60)
		self.currTime = time.ctime(self.currTimeInSec)

	def run(self):
		while True:
			try:
				self.numOfRequests += 1
				self.logger.info("%d request to vk post of %s", self.numOfRequests, self.prodType)
				self.getNewPosts()
				time.sleep(1200)
			except:
				self.logger.error("{}<ERROR>: {}".format(self.subject, traceback.format_exc()))
				sendErrorReport(self.subject + '\n' + traceback.format_exc())
				#time.sleep(1200)
				break

	@sendingDecorator
	def getNewPosts(self):
		postId = prod_ids[self.prodType](self.api)
		comments = getComments(self.api, self.groupId, postId, self.count)[1:]
		foundPosts = [self.getPostData(post) for post in comments if self.checkFunc(self, post)]
		if len(foundPosts) == 0:
			return None
		self.currTimeInSec = max([post["time"] for post in foundPosts])
		self.currTime = time.ctime(self.currTimeInSec)
		return foundPosts


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
			photos = ["https://vk.com/sevads?z={}%2Fwall-{}_{}".format(photo.split('/')[-1], 
				self.groupId, post["cid"]) for photo in photos]
			photos = ',  '.join(photos)

		return {"userName":userName, "time":timeOfPost, "text":text, "photos":photos}

	def getBody(self, posts):
		body = []
		for post in sorted(posts, key=lambda rec: rec["time"]):
				body.append("Продавец: {}\nОписние: {}\nВремя публикации: {}\nФото: {}\n".format(post["userName"], post["text"], 
					time.ctime(post["time"]), post["photos"]))
		return '\n'.join(body)	

	def resetCurrTime(self):
		if datetime.now().day != self.startTime.day:
			self.startTime = datetime.now()
			self.logger.handlers[0].stream.close()
			self.logger.removeHandler(self.logger.handlers[0])
			self.logger.addHandler(getFileHandler(self.prodType))
