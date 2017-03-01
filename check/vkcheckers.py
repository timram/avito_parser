import time

excpectedNoutTerms = ["ноутбук", "ноут", "samsung", "lenovo", "dell", "dexp", "asus", "acer", 
"hp", "toshiba", "dns", "packard", "bell", "sony", "vaio", "msi", "самсунг", "леново", "делл", 
"дексп", "асус", "асер", "хп", "тошиба", "паккард", "пакерд", "белл", "болл", "сони", "ваио", "мси"]

prohibitedTerms = ["мать", "плата", "мат", "материнка", "блок", "системный", "комп", 
"мышь", "мышка"]

def checkVkNouts(parser, post):
	if post["date"] < parser.currTimeInSec:
		parser.logger.info("{} {}".format(time.ctime(post["date"]), time.ctime(parser.currTimeInSec)))	
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