import re, twitch, nooblist
from socket import gethostbyname_ex as checkhost
from urllib.parse import urlparse
from time import clock

rlinkstring = '(?:(?:[a-z0-9$-_@.&+]{1,256})\.)+[a-z]{2,6}'
nbotpstr = '[a-zA-Z0-9]{1,25}\s->\s(?P<Name>[a-zA-Z0-9]{1,25})\shas\sbeen\sgranted\spermission\sto\spost\sa\slink\sfor\s60\sseconds\.'
regperm = re.compile(nbotpstr)
regaddr = re.compile('02481', re.IGNORECASE)
reglink = re.compile(rlinkstring, re.IGNORECASE)

permitcache = {}

def containsLink(message):
	links = reglink.findall(message)
	result = False
	if links:
		for x in links:
			try:
				if not x.startswith('http'): x = 'http://'+x
				url = urlparse(x)
				checkhost(url.hostname)
				result = True
				break
			except:
				continue
	return result

def isNoob(name, cid):
	age = nooblist.getUserAge(nooblist.getUserDate(twitch.getUserData(name, cid)))
	return age<43200, age

def containsAddress(message):
	if regaddr.search(message):
		return True
	else:
		return False

def isSpamBot(name, message, cid):
	if name.lower()=='nightbot':
		me = regperm.match(message)
		if me:
			permitcache[me.group('Name').lower()] = clock()
		return False, False, None
	
	if name.lower() in permitcache and clock()-permitcache[name.lower()]<300:
		links = False
	else:
		links = containsLink(message)
		
		
	addr = containsAddress(message)
	if links or addr:
		noob, age = isNoob(name, cid)
		if noob:
			return True, addr, age
	return False, False, None

