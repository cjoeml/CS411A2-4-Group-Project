##################
## Dependencies ##
##################
import flask
from flask import Flask, render_template, request
from flask_oauthlib.client import OAuth
from flask_bootstrap import Bootstrap
import twitter
import json


# import subprocess 
# This is whether we want to open an entire Python file with this flask app

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

## API calling here ##
key_tuple = get_keys_and_secrets()
api = twitter.Api(consumer_key=key_tuple[0],
                  consumer_secret=key_tuple[1],
                  access_token_key=key_tuple[2],
                  access_token_secret=key_tuple[3])

## TODO: add Facebook here ##

########################################
## Creating the base backend skeleton ##
########################################
def create_app():
    app = Flask(__name__)
    app.secret_key = 'development key'
    Bootstrap(app)
    return app

app = create_app()
oauth = OAuth()
twitter = oauth.remote_app('twitter',
    # unless absolute urls are used to make requests, this will be added
    # before all URLs.  This is also true for request_token_url and others.
    base_url='https://api.twitter.com/1/',
    # where flask should look for new request tokens
    request_token_url='https://api.twitter.com/oauth/request_token',
    # where flask should exchange the token with the remote application
    access_token_url='https://api.twitter.com/oauth/access_token',
    # twitter knows two authorizatiom URLs.  /authorize and /authenticate.
    # they mostly work the same, but for sign on /authenticate is
    # expected because this will give the user a slightly different
    # user interface on the twitter side.
    authorize_url='https://api.twitter.com/oauth/authenticate',
    # the consumer keys from the twitter application registry.
    consumer_key=key_tuple[0],
    consumer_secret=key_tuple[1])

@twitter.tokengetter
def get_twitter_token():
  if current_user.is_authenticated():
      return (current_user.token, current_user.secret)
  else:
      return None


###########
## Pages ##
###########

@app.route('/login')
def login():
  if current_user.is_authenticated():
      return redirect('/')
  return twitter.authorize(callback=url_for('oauth_authorized',
      next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
  next_url = request.args.get('next') or url_for('index')
  if resp is None:
      return redirect(next_url)

  this_account = Account.query.filter_by(username = resp['screen_name']).first()
  if this_account is None:
      new_account = Account(resp['screen_name'], "", resp['oauth_token'], resp['oauth_token_secret'])
      db.session.add(new_account)
      db.session.commit()
      login_user(new_account)
  else:
      login_user(this_account)

  return redirect(next_url)


## Index page ##
@app.route("/", methods=['GET'])
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    access_token = access_token[0] 

    return render_template('index.html')

## Results page - this is where we POST ##
@app.route("/results", methods=['GET','POST'])
def results():
    if request.method == "POST":
        user = request.form['search_input']

    statuses = ""

    ## Basic API call ##
    try:
        statuses = api.GetUserTimeline(screen_name=user)
    except:
        user = ""

    ## Build page ##
    return render_template('results.html', user=user, statuses=statuses)

#############
## Run App ##
#############

if __name__ == "__main__":
    app.run()