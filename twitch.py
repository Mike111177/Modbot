from urllib import request
import json

cid = None

def getChatters(name, cid=cid):
	return json.loads((request.urlopen("http://tmi.twitch.tv/group/user/%s/chatters"%name).read().decode("utf-8")))["chatters"]["viewers"]

def getUserDisplayName(user, cid=cid):
	return getUserData(user, cid)['display_name']

def getUserData(name, cid=cid):
	try:
		req = request.Request("https://api.twitch.tv/kraken/users/%s"%name,  headers={'Client-ID': cid}) #LOOK AT ME IM TWITCH! I REQUIRE A FUCKING CLIENT ID NOW TO USE MY API
		return json.loads(request.urlopen(req).read().decode())
	except:
		try:
			req = request.Request("https://api.twitch.tv/kraken/users/%s"%name,  headers={'Client-ID': cid}) #LOOK AT ME IM TWITCH! I REQUIRE A FUCKING CLIENT ID NOW TO USE MY API
			return json.loads(request.urlopen(req).read().decode())
		except:
			pass


class Twitch(object):

	def __init__(self, cid):
		self.cid = cid

	def getChatters(self, name):
		return json.loads((request.urlopen("http://tmi.twitch.tv/group/user/%s/chatters"%name).read().decode("utf-8")))["chatters"]["viewers"]

	def getUserDisplayName(self, user):
		return self.getUserData(user)['display_name']

	def getUserData(self, name):
		try:
			req = request.Request("https://api.twitch.tv/kraken/users/%s"%name,  headers={'Client-ID': self.cid}) #LOOK AT ME IM TWITCH! I REQUIRE A FUCKING CLIENT ID NOW TO USE MY API
			return json.loads(request.urlopen(req).read().decode())
		except:
			try:
				req = request.Request("https://api.twitch.tv/kraken/users/%s"%name,  headers={'Client-ID': self.cid})
				return json.loads(request.urlopen(req).read().decode())
			except:
				pass	