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

print(twitter)

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
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            tweets = resp.data

        try:
            statuses = api.GetUserTimeline(screen_name=g.user['screen_name'], count="200")
            s = statuses[0:12]
            for status in statuses:
                markov_t = markov_t + " " + status.text.strip('\"') + " "
            mkText = markovify.Text(markov_t)
            mkTweet = mkText.make_short_sentence(140)
        except: 
            mkTweet = "Not enough tweets to display Markov tweet."

        else:
            # flash('Unable to load tweets from Twitter. Getting statuses from api call.')
            statuses = api.GetUserTimeline(screen_name=g.user['screen_name'], count="200")
            s = statuses[0:12]
            try:
                for status in statuses:
                    markov_t = markov_t + " " + status.text + " "
                mkText = markovify.Text(markov_t)
                mkTweet = mkText.make_short_sentence(140)
            except:
                mkTweet = "Not enough tweets to display Markov tweet."
    print(mkTweet)
    cursor = tweet_db.find({})
    for document in cursor: 
        pprint(document['tweet'])
        if document['tweet'] not in prev_tweet_list:
            prev_tweet_list.append(document['tweet'])
    print(prev_tweet_list)
    try:
        tweet_db.insert({ "name":g.user['screen_name'], 'tweet':mkTweet })
    except Exception as e:
        print(e)
    return render_template('index2.html', tweets=s, mkv=mkTweet, prev_t=prev_tweet_list)


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

## Results page - this is where we POST ##
@app.route("/results", methods=['GET','POST'])
def results():
    if request.method == "POST":
        user = request.form['search_input']

    statuses = ""
    mkTweet = ""
    markov_t = ""
    s = ''
    ## Basic API call ##
    try:
        statuses = api.GetUserTimeline(screen_name=user, count="200")
        # statuses = api.GetUserTimeline(screen_name=g.user['screen_name'], count="200")
        print("LENGTH: " + str(len(statuses)))
        s = statuses[0:12]
        for status in statuses:
            markov_t = markov_t + " " + status.text.strip('\"') + " "
            mkText = markovify.Text(markov_t)
            mkTweet = mkText.make_short_sentence(140)
            print(mkTweet)
    except Exception as e:
        statuses = ""
        mkTweet = ""
        print(e)

    ## Build page ##
    return render_template('results2.html', user=user, tweets=s, mkv=mkTweet)


if __name__ == '__main__':
    app.run()