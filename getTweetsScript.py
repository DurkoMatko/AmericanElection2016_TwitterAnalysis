# -*- coding: utf-8 -*-
import sys
import re #regex
import tweepy
import operator
import unicodedata  #smileys
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from collections import defaultdict
import pickle
import datetime

#yields data chronologicaly from the dictionary
def sortdict(d):
    for key in sorted(d): yield key,d[key]


def downloadTweets():
	auth = tweepy.OAuthHandler("zzzpwKuwGyls73SOKqL47upvH", "smd6wmph00nLSdDaASpEU4Pr1lwSr7jhUFvFCaC66zdAbBx7PO")
	auth.set_access_token("827898364217982976-9e4EabQIFOMHmxuVSMiBShbp6xG4iNH", "vkIRpveBVnZh1yu8vzEOCHBi1e2DuopziwudsoZbGjZYv")
	api = tweepy.API(auth,wait_on_rate_limit=True)

	#file handles
	f2 = open('election-day.txt', 'r')
	content = f2.readlines()
	f2.close

	tweets_dictionary = defaultdict(list)

	i=0
	total=0
	sliced=0
	numberOfTweetsPerTimeInterval = 250
	tweetsTimeInterval = 90000

	for tweetID in content[sliced:]:
	#for tweet in tweepy.Cursor(api.user_timeline).items(200):
		i=i+1
		if i==numberOfTweetsPerTimeInterval:
			i=0
			sliced = sliced + tweetsTimeInterval
			print sliced
			#if next 300 will exceed the bounds
			if sliced>(len(content)-numberOfTweetsPerTimeInterval):
				break
		try:
			#get tweet object by id
			tweet = api.get_status(tweetID)
			#if it's not retweet, save it
			if not tweet.retweeted and 'RT @' not in tweet.text:
				if tweet.created_at in tweets_dictionary:
					tweets_dictionary[tweet.created_at].append(tweet.text)
				else:
					tweets_dictionary[tweet.created_at] = []
					tweets_dictionary[tweet.created_at].append(tweet.text)
		except tweepy.TweepError, e:
			pass

	with open("tweets_dictionary.txt", "wb") as myDictFile:
   		pickle.dump(tweets_dictionary, myDictFile)

def wordCloudGraph():

	#regexes for emoticons and hashtags
	emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
	hashtag_pattern = re.compile(r"#(\w+)")

	#strings to store all the words from tweets
	emojis = ""
	hashtags = ""
	words = ""

	#dataset with sentiment-wise evaluated words using values within interval <-5,5>
	sentiment_dict = {}
	for line in open('AFFINN-111.txt'):
		word, score = line.split('\t')
		sentiment_dict[word] = int(score)

	#values for tweet emotions
	worstEmotion = 0
	bestEmotion = 0
	#axes for line chart
	x=[]
	y=[]

	#read dictionary with all the tweets
	with open("tweets_dictionary_backup.txt", "rb") as myDictFile:
		tweets_dictionary = pickle.load(myDictFile)

	#yields data chronologicaly from the dictionary
	for timestamp,tweets in sortdict(tweets_dictionary):
		print timestamp
		for tweet in tweets:
			overalTweetEmotion = 0
			#iterate over words in tweets
			for word in tweet.split():
				if emoji_pattern.match(word):
					emojis = emojis + ", " + word
				elif hashtag_pattern.match(word):
					hashtags = hashtags + ", " + word
				else:
					#get rid of prepositions etc
					if(len(word) > 3):
						#analyze emotion semantics of particular word
						overalTweetEmotion = overalTweetEmotion + sentiment_dict.get(word,0)
						words = words + ", " + word	
			x.append(timestamp)
			y.append(overalTweetEmotion)
			if(overalTweetEmotion > 7 or overalTweetEmotion < -7):
				print tweet
			if(overalTweetEmotion < worstEmotion):
				worstEmotion = overalTweetEmotion
				worstTweet = tweet
			if(overalTweetEmotion > bestEmotion):
				bestEmotion = overalTweetEmotion
				bestTweet = tweet

	wordcloud = WordCloud(stopwords=STOPWORDS).generate(hashtags)
	wordcloud2 = WordCloud(stopwords=STOPWORDS,background_color='white',width=1200,height=1000).generate(words)
	createPlot(wordcloud,wordcloud2,x,y)

	print worstTweet
	print bestTweet


def createPlot(wordCloud,hashcloud,x,y):
	plt.subplot(221)
	plt.title('Words wordcloud')
	plt.axis('off')
	plt.imshow(wordCloud)

	plt.subplot(222)
	plt.title('Hashtags wordcloud')
	plt.axis('off')
	plt.imshow(hashcloud)
	
	plt.subplot(313)
	plt.plot(x,y,'-')
	plt.title('Sentiment analysis over time')
	plt.show()



def main(argv):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	#downloadTweets()
	wordCloudGraph()


if __name__ == "__main__":
	main(sys.argv)
