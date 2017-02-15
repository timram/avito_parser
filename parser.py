import threading
import os
import sys
import time
from avitoParser import AvitoParser
from vkParser import VkParser

if __name__ == "__main__":
	os.system("clear")
	noutsParams = {
		"city": "sevastopol", 
		"subject": "НОУТБУКИ СЕВАСТОПОЛЬ", 
		"maxPrice": 20000, 
		"minPrice": 2700, 
		"url": "https://www.avito.ru/sevastopol/noutbuki"
	}

	tvParams = {
		"city": "sevastopol", 
		"subject": "ТЕЛЕВИЗОРЫ СЕВАСТОПОЛЬ",
		"maxPrice": 25000, 
		"minPrice": 0, 
		"url": "https://www.avito.ru/sevastopol/audio_i_video/televizory_i_proektory"
	}

	monitorParams = {
		"city": "sevastopol", 
		"subject": "МОНИТОРЫ СЕВАСТОПОЛЬ", 
		"maxPrice": 5000, 
		"minPrice": 0, 
		"url": "https://www.avito.ru/sevastopol/tovary_dlya_kompyutera/monitory"
	}

	vkNoutParams = {
		"prodType":"nouts",
		"subject":"ВК НОУТБУКИ",
		"count":15
	}

	lock = threading.Lock()

	parsers = [AvitoParser(lock, **noutsParams), AvitoParser(lock, **tvParams), AvitoParser(lock, **monitorParams), 
	VkParser(lock, **vkNoutParams)]
	#parsers = [VkParser(**vkNoutParams)]
	
	for parser in parsers:
		parser.start()

	for parser in parsers:
		parser.join()