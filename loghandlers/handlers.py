import logging
import os
from datetime import datetime

def getFileHandler(fileName):
	directory = os.getcwd()
	starttime = datetime.now()
	filename = os.path.join(directory, "loggers/%s_%d-%d-%d.log" %(fileName, 
		starttime.year, starttime.month, starttime.day))
	fileHandler = logging.FileHandler(filename, mode='w')
	fileHandler.setLevel(logging.DEBUG)
	formatter = logging.Formatter("%(levelname)s: %(asctime)s : %(message)s", 
		datefmt="%m/%d/%Y %I:%M:%S %p")
	fileHandler.setFormatter(formatter)
	return fileHandler

def getConsoleHandler():
	consoleHandler = logging.StreamHandler()
	formatter = logging.Formatter("%(levelname)s: %(asctime)s : %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
	consoleHandler.setLevel(logging.DEBUG)
	consoleHandler.setFormatter(formatter)
	return consoleHandler

