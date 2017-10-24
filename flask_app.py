##################
## Dependencies ##
##################
import flask
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import twitter
import json

# import subprocess 
# This is whether we want to open an entire Python file with this flask app

##################

## Need to add your own details.json with your keys and secrets ##
def get_keys_and_secrets():
    credentials = {}
    with open("details.json",'r') as file:
        credentials = json.load(file)[0]
        consumer_key = credentials["consumer_key"]
        consumer_secret = credentials["consumer_secret"]
        access_token_key = credentials["access_token_key"]
        access_token_secret = credentials["access_token_secret"]
        return (consumer_key, consumer_secret, access_token_key, access_token_secret)
key_tuple = get_keys_and_secrets()

## TBD: Move this to a more secure location ##
api = twitter.Api(consumer_key=key_tuple[0],
                  consumer_secret=key_tuple[1],
                  access_token_key=key_tuple[2],
                  access_token_secret=key_tuple[3])

########################################
## Creating the base backend skeleton ##
########################################
def create_app():
	app = Flask(__name__)
	Bootstrap(app)
	return app
app = create_app()

###########
## Pages ##
###########

## Index page ##
@app.route("/", methods=['GET'])
def index():
	return render_template('index.html')

## Results page - this is where we POST ##
@app.route("/results", methods=['GET','POST'])
def results():

	if request.method == "POST":
		user = request.form['search_input']

	## Basic API call ##
	statuses = api.GetUserTimeline(screen_name=user)

	## Build page ##
	return render_template('results.html', user=user, statuses=statuses)

#############
## Run App ##
#############

if __name__ == "__main__":
	app.run()