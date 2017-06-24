# -*- encoding: utf-8 -*-
from pyquery import PyQuery as pq
from selenium import webdriver
import time, requests, json, os, urlparse
import twitter

CONSUMER_KEY = "xxxxxxx"
CONSUMER_SECRET = "xxxxxxx"
ACCESS_TOKEN = "xxxxxxxxx"
ACCESS_SECRET = "xxxxxxxx"

def formateDate(date):
	date = time.localtime(date)
	return ("%d" % date[0])+("%02d" % date[1])+("%02d" % date[2])

class Tool(object):
	def __init__(self):
		self.baseDir = 'temp/'
		self.mkDir(self.baseDir)

	def mkDir(self, path):
		if not os.path.exists(self.baseDir):
			os.makedirs(self.baseDir)

	def savePostedStories(self, stories, date):
		path = self.baseDir + date + '.json'
		f = open(path, 'w+')
		jsonStr = json.dumps(stories)
		f.write(jsonStr)
		f.close()

	def readPostedStories(self, date):
		path = self.baseDir + date + '.json'
		if not os.path.exists(path):
			return None
		f = open(path, 'r')
		jsonStr = None
		jsonStr = f.read()
		f.close()
		if len(jsonStr):
			stories = json.loads(jsonStr)
			return stories
		return None




class TwitterClient(object):
	def __init__(self):
		self.api = twitter.Api(consumer_key=CONSUMER_KEY,
							consumer_secret=CONSUMER_SECRET,
							access_token_key=ACCESS_TOKEN,
							access_token_secret=ACCESS_SECRET)
	def postStrory(self, story):
		storyText = story['title'] + '\n' + story['detail']
		stroyUrl = story['url']
		# print storyText,'\n,',story['url']
		if len(storyText.decode('utf-8'))>(138 - len(stroyUrl)):
			storyText = storyText.decode('utf-8')[0:(138-len(stroyUrl))].encode('utf-8')
		storyText = storyText + '  ' + stroyUrl
		# print storyText, len(storyText)
		status = self.api.PostUpdate(storyText.decode('utf-8'))
		print status.text.encode('utf-8')

	def postStories(self, stories):
		for story in stories:
			self.postStrory(story)

class Solidot(object):

	def __init__(self):
		self.domain = 'http://www.solidot.org'
		self.base_url = 'http://www.solidot.org?issue='
		# self.browser = webdriver.PhantomJS()

	'''
	date is a string like 20170622
	'''
	def pageOfDate(self, date):
		url = self.base_url + date
		start = time.time()
		# self.browser.get(url)
		# page_source = self.browser.page_source.encode('utf-8')
		page_source = requests.get(url).content
		end = time.time()
		print 'fetch time: ', (end - start)
		doc = pq(page_source)
		items = doc('.block_m').items()
		stories = []
		for item in items:
			story = {}
			story['title'] = item('.ct_tittle').text().encode('utf-8')
			story['detail'] = item('.p_content').text().encode('utf-8')
			story['url'] = self.domain + item('.talkm_mid a').eq(0).attr.href
			# print '*'*100
			# print item('.ct_tittle').text()
			# print '-'*100
			# print item('.p_content').text()
			stories.append(story)
		end2 = time.time()
		print 'parse time: ', (end2 - end)
		# self.browser.close()
		return stories


print '*'*50, 'begin', '*'*50
beginTime = time.time()

twitterClient = TwitterClient()

solidot = Solidot()

dateStr = formateDate(time.time())
print dateStr

stories = solidot.pageOfDate(dateStr)[0:8]
stories.reverse()
for story in stories:
	print story['title']

tool = Tool()
todayPostedStories = tool.readPostedStories(dateStr)
print todayPostedStories
if todayPostedStories == None:
	todayPostedStories = []

storiesNotPosted = []
for story in stories:
	print story['url']
	parsed = urlparse.urlparse(story['url'])
	params = urlparse.parse_qs(parsed.query)
	# print params
	storyId = params['sid'][0]
	if not storyId in todayPostedStories:
		storiesNotPosted.append(story)
		todayPostedStories.append(storyId)

print len(storiesNotPosted), 'stories need post'
try:
	twitterClient.postStories(storiesNotPosted)
	tool.savePostedStories(todayPostedStories, dateStr)
except Exception as e:
	print e.message

finishedTime = time.time()
print '*'*50, 'finished', '*'*50
print 'total time: %f s' % (finishedTime - beginTime)