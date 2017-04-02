def readAuthorizationInfo(fileName):
	file = open(fileName, 'r')
	login = file.readline()
	password = file.readline()
	return {"login": login.strip(), "password": password.strip()}