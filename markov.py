import markovify 
import json
import twitter

def get_keys_and_secrets():
    """
    Function to aggregate all keys and secrets for simplicity and return an easy tuple to parse
    """
    ## Need to add your own details.json with your keys and secrets ##
    credentials = {}
    with open("/home/cjoe/Projects/CS411A2-4-Group-Project/details.json",'r') as file:
        credentials = json.load(file)[0]
        consumer_key = credentials["consumer_key"]
        consumer_secret = credentials["consumer_secret"]
        access_token_key = credentials["access_token_key"]
        access_token_secret = credentials["access_token_secret"]
        return (consumer_key, consumer_secret, access_token_key, access_token_secret)

def main():
	key_tuple = get_keys_and_secrets()
	api = twitter.Api(consumer_key=key_tuple[0],
                  consumer_secret=key_tuple[1],
                  access_token_key=key_tuple[2],
                  access_token_secret=key_tuple[3])

	statuses = api.GetUserTimeline(screen_name="realDonaldTrump", count="200")

	print(statuses[0])

	last_id = statuses[199].id

	older_statuses = api.GetUserTimeline(screen_name="realDonaldTrump", count="200", max_id=last_id)

	text_model = ""

	for status in statuses:
		text_model = text_model + " " + status.text + " "

	for old_status in older_statuses:
		text_model = text_model + " " + old_status.text + " "

	# print(len(statuses))
	# print(len(older_statuses))
	mkText = markovify.Text(text_model)

	tweet = mkText.make_short_sentence(140)
	print(tweet)

if __name__ == "__main__":
	main()