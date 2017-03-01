from datetime import datetime, timedelta

expectedTitles = ["samsung", "lenovo", "dell", "dexp", "asus", "acer", "hp", "toshiba", "dns", "packard", "bell"
"sony", "vaio", "msi", "самсунг", "леново", "делл", "дексп", "асус", 
"асер", "хп", "тошиба", "днс", "пакард", "пакерд", "белл", "болл", "сони", "ваио", "мси"]

prohibitedTitles = ["vk", "agent", "trade", "salon", "ноутбуки", "вк", "вконтакте", "агент", "традер", "салон", "большой выбор",
"широкий выбор"]

def isAppropriateData(title, name, description):
	for titles in prohibitedTitles:
		if titles in title.lower() or titles in name.lower() or titles in description.lower():
			return False
	isAppropriate = False
	for titles in expectedTitles:
		if titles in title.lower() or titles in description.lower():
			return True
			break
	return False

def estimate(title, diff, description, salerType, salerExp):
	rating = 10
	if diff.days > 2:
		rating -= 1
	if salerType == "Company":
		rating -= 1
	salerExpDiff = datetime.now() - salerExp
	if salerExpDiff.days >= 365:
		rating -= 1
	if  salerExpDiff.days >= 200:
		rating -= 1
	if salerExpDiff.days >= 100:
		rating -= 1
	if salerExpDiff.days >= 50:
		rating -= 1
	if salerExpDiff.days >= 14:
		rating -= 1
	return rating


def checkNoutPost(parser, post):
	return post["time"] > parser.currTime and int(post["price"]) <= parser.maxPrice and int(post["price"]) >= parser.minPrice\
	and "VK" not in post["name"].upper() and "TRADE" not in post["name"].upper()

def checkTvPost(parser, post):
	return post["time"] > parser.currTime and int(post["price"]) <= parser.maxPrice and int(post["price"]) >= parser.minPrice \
	and "телевизор" in post["title"].lower()	
