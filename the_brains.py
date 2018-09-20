from flask import Flask
from flask_cors import CORS
import tweepy

#Variables
consumer_key = 'db3QhNKdND5TjQZIro9O1lVd6'
consumer_secret = '8v1GcJYKJOTK3n3SW3Qrxz5oWBCiF1YPHghwXUaJK5bFHCIcec'

access_token = '950112932540514304-S7aEqe4D3tyI4NmLrCCcADQgHQdRzMT'
access_token_secret = 'mZGfJJJequ8gxrwiPis1kx1fTP96EPhnmRpwCJ6DAmaEs'

# Creating the access token to be sent to Twitter API
# Uses the Tweepy Library

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

API = tweepy.API(auth)

app = Flask(__name__)
CORS(app)



@app.route('/')
def hello_world():
    return 'Hello, World!'
