import requests
from bs4 import BeautifulSoup
import os
import sys
import csv
from datetime import datetime, timedelta
import time
from get.getters import getHtml, getTotalPages, getLink, getTitle, getPrice, getSalerType, getPublicationTime,\
getExtendProductData
from check.noutcheckers import isAppropriateData, estimate
from write.writers import write, writeText
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool


class AvitoParser(object):

	def __init__(self, **kwargs):
		self.baseLink = "https://www.avito.ru" 
		if "city" in kwargs:
			self.city = kwargs["city"]
		else:
			self.city = "sevastopol"
		if "productName" in kwargs:
			self.productName = kwargs["productName"]
		else:
			self.productName = "noutbuki"
		if "sortParam" in kwargs:
			self.sortParam = kwargs["sortParam"]
		else:
			self.sortParam = 0
		if "maxPrice" in kwargs:
			self.maxPrice = kwargs["maxPrice"]
		else:
			self.maxPrice = 20000
		if "minPrice" in kwargs:
			self.minPrice = kwargs["minPrice"]
		else:
			self.minPrice = 2000
		if "period" in kwargs:
			self.period = kwargs["period"]
		else:
			self.period = 10
		self.baseUrl = "{0}/{1}/{2}".format(self.baseLink, self.city, self.productName)
		self.totalPages = getTotalPages(getHtml(self.baseUrl))
		self.suitableRecords = []

	def parseData(self):
		pagePart = "p="
		sortPart = "s=" + str(self.sortParam)
		pageUrls = [self.baseUrl + '?' + pagePart + str(i+1) + "&" + sortPart for i in range(self.totalPages)]
		pool = ThreadPool(13)
		results = pool.map(self.parsePage, pageUrls)
		pool.close()
		pool.join()
		for result in results:
			self.suitableRecords.extend(result)

		
	def parsePage(self, url):
		print(url)
		html = getHtml(url)
		soup = BeautifulSoup(html, "lxml")
		catalog = soup.find("div", class_="catalog-list")
		records = catalog.find_all("div", class_="item")	
		suitRecords = []
		for record in records:
			try:
				description = record.find("div", class_="description")
				price = getPrice(description)
				publicTime = getPublicationTime(description)
				diff = datetime.now() - publicTime
				if int(price) <= self.maxPrice and int(price) >= self.minPrice and diff.days <= self.period: 
					link = self.baseLink + getLink(description)
					title = getTitle(description)
					salerType = getSalerType(description)
					name, salerExp, prodDescription = getExtendProductData(link)
					if prodDescription is None:
						continue
					if isAppropriateData(title, name, prodDescription):
						suitRecords.append({"link":link, "title":title, "price":int(price), "saler_type":salerType,
							"publication_time":"{0}/{1}/{2}".format(publicTime.day, publicTime.month, publicTime.year),
							"name":name, "saler_exp":"{0}/{1}".format(salerExp.month, salerExp.year),
							"description":prodDescription, "raiting":estimate(title, diff, prodDescription, salerType, salerExp)})
			except Exception as e:
				print(e)
		return suitRecords

if __name__ == "__main__":
	os.system("clear")
	if len(sys.argv) == 1:
		parser = AvitoParser()
	else:
		kwargs = {}
		for i in range(len(sys.argv)):
			if sys.argv[i] == "-c":
				kwargs["city"] = sys.argv[i+1]
			if sys.argv[i] == "-p":
				kwargs["productName"] = sys.argv[i+1]
			if sys.argv[i] == "--min":
				kwargs["minPrice"] = int(sys.argv[i+1])
			if sys.argv[i] == "--max":
				kwargs["maxPrice"] = int(sys.argv[i+1])
			if sys.argv[i] == "--per":
				kwargs["period"] = int(sys.argv[i+1])
			if sys.argv[i] == "-s":
				kwargs["sortParam"] = int(sys.argv[i+1])
		parser = AvitoParser(**kwargs)				

	start = time.time()
	parser.parseData()
	records = parser.suitableRecords
	print(time.time() - start)
	writeText(records)