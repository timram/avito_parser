import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

months = {"января":1, "февраля":2, "марта":3, "апреля":4, "мая":5, "июня":6, "июля":7, "августа":8, 
		 "сентября":9, "октября":10, "ноября":11, "декабря":12}

def getHtml(url):
	print(url)
	return requests.get(url).text

def getTotalPages(html):
	soup = BeautifulSoup(html, "lxml")
	lastPage = soup.find("div", class_="pagination-pages").find_all("a", class_="pagination-page")[-1].get("href")
	totalPages = lastPage[lastPage.find('=')+1:]
	return int(totalPages)

def getLink(description):
	return description.find("a", class_="item-description-title-link").get("href")

def getTitle(description):
	return description.find("a", class_="item-description-title-link").get("title")

def getPrice(description):
	price = description.find("div", class_="about").text
	price = price[price.index('\n')+1 : price.index("руб")]
	return ''.join(price.split(' '))

def getSalerType(description):
	saler = description.find("div", class_="data").find("p")
	if not saler is None:
		return "Company"
	return "Saler"

def getPublicationTime(description):
	date = description.find("div", class_="date").text.strip()
	if "Сегодня" in date:
		curDate = datetime.now()
	elif "Вчера" in date:
		curDate = datetime.now() - timedelta(days=1)
	else:
		date = date.split(' ')[:-1]
		if datetime.now().month < months[date[1]]:
			curDate = datetime(datetime.now().year - 1, months[date[1]], int(date[0]))
		else:
			curDate = datetime(datetime.now().year, months[date[1]], int(date[0]))
	return curDate

def getExtendProductData(url):
	soup = BeautifulSoup(getHtml(url), "lxml")
	name = soup.find("div", class_="seller-info-name").text.strip()
	salerExp = soup.find("div", class_="seller-info-time").text.strip()
	salerExp = salerExp.split(' ')
	salerExp = datetime(int(salerExp[-1]), months[salerExp[-2]], 1)
	try:
		descriptions = soup.find("div", class_="item-view-block").find_all("p")
		fullDescription = '\n'.join([desc.text for desc in descriptions])
	except Exception as e:
		fullDescription = None
	return [name, salerExp, fullDescription]

	