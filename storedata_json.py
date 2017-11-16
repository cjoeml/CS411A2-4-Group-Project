

import sys
import json
from pymongo import MongoClient


data = json.load(open('data.json'))  #Assuming file name is data.json(Subject to change)
connection = MongoClient('mongodb://localhost/twitterdb')  #My localhost to store data in my database:twitterdb
connection.database_names()
db = connection.database
posts = db.posts
post_id = posts.insert_many(data).inserted_id
