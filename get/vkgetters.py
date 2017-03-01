
def getGroupId(api, gid):
	groupData = api.groups.getById(group_id=gid)
	return groupData[0]["gid"]

def getNoutPostId(api):
	noutPicture = "https://pp.userapi.com/c627823/v627823829/16d57/CsciuABHisg.jpg"
	posts = api.wall.get(domain="sevads", filter="owner", count=50)
	noutPost = None
	for post in posts[1:]:
		"""for key in post:
			print(key, post[key], '\n')
		print('\n')"""
		try:
			if post["attachment"]["photo"]["src"] == noutPicture:
				noutPost = post
				break
		except Exception as e:
			continue
	return noutPost["id"]

def getTechnPostId(api):
	technPicture = "https://pp.vk.me/c615830/v615830829/10ad3/CtHlVwzYniU.jpg"
	posts = api.wall.get(domain="sevads", filter="owner", count=50)
	technPost = None
	for post in posts[1:]:

		try:
			if post["attachment"]["photo"]["src"] == technPicture:
				technPost = post
				break
		except Exception as e:
			continue

	return technPost["id"]


def getComments(api, gid, pid, count):
	comments = api.wall.getComments(owner_id=-gid, post_id=pid, sort="desc", count=count)
	return comments

def getUserData(api, userid):
	userData = api.users.get(user_ids=userid)
	return userData[0]