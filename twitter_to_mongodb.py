from __future__ import print_function
import tweepy
import json
from pymongo import MongoClient

Mongo_host = 'mongodb://localhost/twitterdb' #My local database to store data

Consumer_key = "Insert Your Consumer_key"
Consumer_secret = "Insert Your Consumer_secret"
Access_token = "Insert Your Access_token"
Access_token_secret = "Insert Your Access_token_secret"


class StreamListener(tweepy.StreamListener):
 
    def on_connect(self):
        print("Connected to Twitter API.")
 
    def on_error(self, status_code):
        print('Error code: ' + repr(status_code))
        return False
 
    def on_data(self, data):
        try:
            client = MongoClient(Mongo_host)
            db = client.twitterdb
            datajson = json.loads(data)
            created_at = datajson['created_at']
            print("Tweet collected at " + str(created_at))
            db.twitter_search.insert(datajson)
        except Exception as e:
           print(e)

auth = tweepy.OAuthHandler(Consumer_key, Consumer_secret)
auth.set_access_token(Access_token, Access_token_secret)
listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True)) 
streamer = tweepy.Stream(auth=auth, listener=listener)

streamer.filter(track=['Google'])