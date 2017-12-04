# coding: utf-8
from pprint import pprint
import markovify 
from flask import Flask
from flask import g, session, request, url_for, flash
from flask import redirect, render_template
from flask_oauthlib.client import OAuth
from flask_bootstrap import Bootstrap
from pymongo import MongoClient # Database connector
import twitter
import json
import re
import collections

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

##################

def get_keys_and_secrets():
    """
    Function to aggregate all keys and secrets for simplicity and return an easy tuple to parse
    """
    ## Need to add your own details.json with your keys and secrets ##
    credentials = {}
    with open("details.json",'r') as file:
        credentials = json.load(file)[0]
        consumer_key = credentials["consumer_key"]
        consumer_secret = credentials["consumer_secret"]
        access_token_key = credentials["access_token_key"]
        access_token_secret = credentials["access_token_secret"]
        return (consumer_key, consumer_secret, access_token_key, access_token_secret)

####################

## Init db ##
client = MongoClient('localhost', 27017)    #Configure the connection to the database
db = client.twitterdb #Select the database
tweet_db = db.tweets
result = tweet_db.delete_many({}) # Reset every instance because why not


## API calling here ##
key_tuple = get_keys_and_secrets()
api = twitter.Api(consumer_key=key_tuple[0],
                  consumer_secret=key_tuple[1],
                  access_token_key=key_tuple[2],
                  access_token_secret=key_tuple[3])

oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key=key_tuple[0],
    consumer_secret=key_tuple[1],
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize'
)

@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


## Index page ##
@app.route("/", methods=['GET'])
def index():
    markov_t, mkTweet, s = '', '', ''
    statuses, tweets = None, None
    prev_tweet_list = []
    words = []
    word_frequency = {"blank":0}
    largest_occurence = 0
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json')
        
        if resp.status == 200:
            tweets = resp.data

        try:
            statuses = api.GetUserTimeline(screen_name=g.user['screen_name'], count="200")
            s = statuses[0:12]
            status_bodies = []
            
            for status in statuses:
                status_text = status.text.strip('\"')
                status_bodies.append(status_text)
            
                markov_t = markov_t + " " + status_text + " "
                mkText = markovify.Text(markov_t)
                mkTweet = mkText.make_short_sentence(140)
            
        except Exception as e:
            mkTweet = "Not enough tweets to display Markov tweet."

        rgx = re.compile("(\w[\w']*\w|\w)")

        for tweet in status_bodies:
            words_in_tweets = rgx.findall(tweet)
            for word in words_in_tweets:
                words.append(word)
        word_frequency = collections.Counter(words)

    cursor = tweet_db.find({})
    for document in cursor: 
        if document['tweet'] not in prev_tweet_list:
            prev_tweet_list.append(document['tweet'])
    
    try:
        tweet_db.insert({ "name":g.user['screen_name'], 'tweet':mkTweet })
    except Exception as e:
        print(e)

    return render_template('index.html', tweets=s, mkv=mkTweet,prev_t=prev_tweet_list, 
        words_in_tweets=list(set(words)), number_of_words = len(words), word_frequency=collections.Counter(words),
        largest_occurence=max(word_frequency.values()))



@app.route('/tweet', methods=['POST'])
def tweet():
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={'status': status})

    if resp.status == 403:
        flash("Error: #%d, %s " % (
            resp.data.get('errors')[0].get('code'),
            resp.data.get('errors')[0].get('message'))
        )
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))

blackList = [ "the", "of", "and", "a", "to", "in", "is", 
        "you", "that", "it", "he", "was", "for", "on", "are", "as", "with", 
        "his", "they", "i", "at", "be", "this", "have", "from", "or", "one", 
        "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", 
        "your", "can", "said", "there", "use", "an", "each", "which", "she", 
        "do", "how", "their", "if", "will", "up", "other", "about", "out", "many", 
        "then", "them", "these", "so", "some", "her", "would", "make", "like", 
        "him", "into", "time", "has", "look", "two", "more", "write", "go", "see", 
        "number", "no", "way", "could", "people",  "my", "than", "first", "water", 
        "been", "call", "who", "oil", "its", "now", "find", "long", "down", "day", 
        "did", "get", "come", "made", "may", "part"]

## Results page - this is where we POST ##
@app.route("/results", methods=['GET','POST'])
def results():
    if request.method == "POST":
        user = request.form['search_input']

    statuses = ""
    mkTweet = ""
    markov_t = ""
    s = ''
    words = []
    word_frequency = {"blank":0}
    largest_occurence = 0
    ## Basic API call ##
    try:
        statuses = api.GetUserTimeline(screen_name=user, count="200")
        s = statuses[0:12]
        status_bodies = []
        for status in statuses:
            status_text = status.text.strip('\"')
            status_bodies.append(status_text)
            
            markov_t = markov_t + " " + status_text + " "
            mkText = markovify.Text(markov_t)
            mkTweet = mkText.make_short_sentence(140)

            rgx = re.compile("(\w[\w']*\w|\w)")

            for tweet in status_bodies:
                http_url_location = [(m.start(0), m.end(0)) for m in re.finditer("http",tweet)]
                
                if len(http_url_location) > 0:
                    for loc in http_url_location:
                        start = loc[0]
                        end = loc[1]

                        next_space = -1
                        for i in range(start,len(tweet)):
                            if tweet[i] == " ":
                                next_space = i
                        
                        if next_space == -1:
                            next_space = end

                        tweet = tweet[0:start] + tweet[next_space:]

            words_in_tweets = rgx.findall(tweet)
            for word in words_in_tweets:
                if word not in blackList and len(word) > 3:
                    words.append(word)
            word_frequency = collections.Counter(words)
    except Exception as e:
        statuses = ""
        mkTweet = ""
        print(e)

    ## Build page ##
    return render_template('results.html', user=user, tweets=s, mkv=mkTweet,
        words_in_tweets=list(set(words)), number_of_words = len(words), word_frequency=collections.Counter(words),
        largest_occurence=max(word_frequency.values()))

if __name__ == '__main__':
    app.run()
