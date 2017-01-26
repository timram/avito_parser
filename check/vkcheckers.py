import time

excpectedNoutTerms = ["ноутбук", "ноут", "samsung", "lenovo", "dell", "dexp", "asus", "acer", "hp", "toshiba", "dns", "packard", "bell"
"sony", "vaio", "msi", "самсунг", "леново", "делл", "дексп", "асус", 
"асер", "хп", "тошиба", "днс", "паккард", "пакерд", "белл", "болл", "сони", "ваио", "мси"]

prohibitedTerms = ["мать", "плата", "мат", "материнка", "блок", "системный", "комп"]

def checkVkNouts(parser, post):
	if int(post["date"]) < int(time.mktime(parser.currTime.timetuple())):
		return False

	isIn = lambda term: term in post["text"].lower() 

	expectedTermInPost = map(isIn, excpectedNoutTerms)
	if True in expectedTermInPost:
		prohibitedTermsInPost = map(isIn, prohibitedTerms)
		return not True in prohibitedTermsInPost

	return False


def checkVkTv(post):
	pass

def checkVkMonitors(post):
	pass