# Post Like Me
The project should take an aggregation of the user’s social media posts and retain frequency of words that he or she has used. Then, using the gathered data, this project should be able to create a word cloud generated by the user’s posts and then create either a post, a paragraph, or a letter generated from the data provided by the user. 

Post Like Me is a useless webapp that does nothing of importance. Using Markov chains, the webapp creates simulated tweets of the user and generates their word cloud of most frequent words used in their posts. Optionally, the user is allowed to tweet from this webapp but we are not sure why anybody would do that over posting on Twitter. These features can be extended to any Twitter user that can be searched publicly.

## Keys and Secrets
This webapp requires keys and secrets from api.twitter.com in order to do requests from Twitter. 

## Usage
Install and run mongodb, then run flask_app.py in order to host your webserver locally. By default, the server runs on localhost:5000. 

## Requirements
The webapp is built on Python, using flask as the frontend and mongodb as the backend. The dependencies include:
```
python-twitter
flask_oauthlib
pymongo
```
The rest of the libraries should be included by default with any installation of Python 3+. 
