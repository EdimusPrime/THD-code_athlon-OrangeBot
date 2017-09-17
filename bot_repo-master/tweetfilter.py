import tweepy
import json
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six
import time
import config
import googlemaps
import random

from oauth2client.client import GoogleCredentials
credentials = GoogleCredentials.get_application_default()


class MyStreamListener(tweepy.StreamListener):
    count = 0

    def __init__(self):
        self.dict_error = {
            "count500Codes": [0, [500, 502, 503, 504]],
            "count420Codes": [60, [420, 429]],
            "count400Codes": [5, [400, 401, 403, 404, 406, 410, 422]]
        }

        self.dict_commands = {
            "locate": ["nearby", "nearest", "near", "location", "closeby"],
            "joke": ["joke", "jokes"],
            "promotion": ["facebook", "twitter", "instagram", "social", "media"],
            "hours": ["hours", "open", "close", "time"]
        }

        self.jokes = {
            1: "Q: What did the duck say when he bought lipstick?\nA: \"Put it on my bill.",
            2: "I bought some shoes from a drug dealer. I don't know what he laced them with, but I've been tripping all day.",
            3: "I told my girlfriend she drew her eyebrows too high. She seemed surprised.",
            4: "I bought my friend an elephant for his room.\nHe said \"Thanks\"\nI said \"Don't mention it\"",
            5: "Why did the old man fall in the well?\nBecause he couldn't see that well."
        }

    def on_status(self, status):
        print(status.text)

    def on_data(self, data):
        MyStreamListener.__init__(self)
        dict_data = json.loads(data)
        MyStreamListener.count += 1

        # filter out RTs
        if "RT @" not in dict_data["text"] and dict_data["user"]["screen_name"] != tweepy.API(auth).me()._json["screen_name"]:

            def feedback(tweet):
                # def google sentiment analytics
                def sentiment_text(text):
                    # Detects sentiment in the text.
                    client = language.LanguageServiceClient()
                    if isinstance(text, six.binary_type):
                        text = text.decode('utf-8')

                    # Instantiates a plain text document.
                    document = types.Document(
                        content=text,
                        type=enums.Document.Type.PLAIN_TEXT)

                    # Detects sentiment in the document.
                    sentiment = client.analyze_sentiment(document).document_sentiment
                    return sentiment.score

                # pass tweet through google sentiment analytics
                sentiment = sentiment_text(tweet)

                # sentiment logic
                sentiment_type = "neutral"
                middleStr = "glad you enjoyed yourself at @HomeDepot"
                if sentiment < 0:
                    # negative
                    sentiment_type = "negative"
                    middleStr = "sorry your visit didn't go as planned"
                elif sentiment != 0:
                    sentiment_type = "positive"

                # reply to tweet
                screenName = dict_data["user"]["screen_name"]
                charLeft = 60 - len(middleStr)
                if len(screenName) > charLeft:
                    screenName = screenName[:charLeft - 1]
                string = "Hello @{0}. We're {1}. Let us know about your recent experience: https://goo.gl/H5khzW".format(screenName, middleStr)
                nullArg = tweepy.API(auth).update_status(status=string, in_reply_to_status_id=dict_data["id"])

                printTweet()
                print("Sentiment: {}".format(sentiment_type))
                print("Score: {}".format(sentiment))
                print("")

            def locate(location):
                client = googlemaps.Client(key="AIzaSyAts9uxjLmeWbS0nfPskZC9Ou8YlMBe4Ow")
                latitude = location[1]
                longitude = location[0]
                screenName = dict_data["user"]["screen_name"]
                currentRadius = 500
                holdExit = True
                while holdExit:
                    dict_map = client.places_nearby(location="{0},{1}".format(latitude, longitude), radius=currentRadius, keyword="The Home Depot")
                    print(dict_map)
                    try:
                        name = dict_map["results"][0]["name"]
                        vicinity = dict_map["results"][0]["vicinity"]
                        rating = dict_map["results"][0]["rating"]
                        holdExit = False
                    except:
                        currentRadius *= 2

                string = "Hello @{0}.\nThe nearest @HomeDepot to you is {1}. Rated {2}/5.".format(screenName, vicinity, rating)
                nullArg = tweepy.API(auth).update_status(status=string, in_reply_to_status_id=dict_data["id"])

                printTweet()
                print(name)
                print(vicinity)
                print(rating)

            def replyTweet(string, replyTo):
                nullArg = tweepy.API(auth).update_status(status=string, in_reply_to_status_id=replyTo)

            def printTweet():
                print("User: {}".format(dict_data["user"]["screen_name"]))
                print("Tweet: {}".format(dict_data["text"]))
                print("Count: {}".format(MyStreamListener.count))

            tweet = dict_data["text"]
            for word in tweet.lower().split(" "):
                for keyList in self.dict_commands.values():
                    for punc in ".,;:?!'\"-":
                        word = word.strip(punc)
                    if word in keyList:
                        if word in self.dict_commands["locate"] and dict_data["place"]:
                            print("Location Reply")
                            locate(dict_data["place"]["bounding_box"]["coordinates"][0][0])
                            return None
                        elif word in self.dict_commands["joke"]:
                            print("Joke Reply")
                            joke = self.jokes[random.randint(1, len(self.jokes))]
                            string = "Hey @{0}. {1}".format(dict_data["user"]["screen_name"], joke)
                            replyTweet(string, dict_data["id"])
                            printTweet()
                            return None
                        elif word in self.dict_commands["promotion"]:
                            print("Promotion Reply")
                            string = "Hi @{}! You can find us on FB: HomeDepot, @HomeDepot, INSTA: @HomeDepot, and YT: https://goo.gl/U8gRCp.".format(dict_data["user"]["screen_name"])
                            replyTweet(string, dict_data["id"])
                            printTweet()
                            return None
                        elif word in self.dict_commands["hours"]:
                            print("Hours Reply")
                            string = "Hola @{}. Our hours are Mon-Sat: 6:00am - 10:00pm and on Sun: 8:00am - 8:00pm.".format(dict_data["user"]["screen_name"])
                            replyTweet(string, dict_data["id"])
                            printTweet()
                            return None
            print("Feedback Reply")
            feedback(dict_data["text"])

    # error handling
    def on_error(self, status_code):
        # check for error code
        timeDelay = 0
        for var in self.dict_error.keys():
            if status_code in self.dict_error["count500Codes"][1] and (.25 * self.dict_error["count500Codes"][0] < 16):
                self.dict_error["count500Codes"][0] += 1
                timeDelay = self.dict_error["count500Codes"][0] * .25
            elif status_code in self.dict_error["count420Codes"][1] or (status_code in self.dict_error["count400Codes"][1] and ((self.dict_error["count400Codes"][0] * 2) < 320)):
                self.dict_error[var][0] *= 2
                timeDelay = self.dict_error[var][0]
            else:
                return None
            # if time delay is known, delay so as to not run_limit.
            if timeDelay:
                print("Error Code: {}".format(status_code))
                print("Time: {}".format(timeDelay))
                return time.sleep(timeDelay + (timeDelay * .05))


def main():
    # set twitter keys/tokens
    global auth
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)

    # class
    myStreamListener = MyStreamListener()

    # set stream details
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)

    # print(tweepy.API(auth).rate_limit_status())
    # print("\n")
    # print(tweepy.API(auth).rate_limit_status()['resources']['users']['/users/lookup'])
    try:
        myStream.filter(track=["homedepot", "home depot", "homedepotassist", "home depot's"], async=True, languages=["en"])
    except tweepy.TweepError:
        myStream.on_error(tweepy.TweepError.message[0]['code'])


# runs at start
if __name__ == "__main__":
    main()
