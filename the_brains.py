from flask import Flask
from flask_cors import CORS
import tweepy
from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import numpy as np
from flask import jsonify
import sys
import tensorflow as tf

app = Flask(__name__)
CORS(app)

# Variables
consumer_key = 'db3QhNKdND5TjQZIro9O1lVd6'
consumer_secret = '8v1GcJYKJOTK3n3SW3Qrxz5oWBCiF1YPHghwXUaJK5bFHCIcec'

access_token = '950112932540514304-S7aEqe4D3tyI4NmLrCCcADQgHQdRzMT'
access_token_secret = 'mZGfJJJequ8gxrwiPis1kx1fTP96EPhnmRpwCJ6DAmaEs'

# Creating the access token to be sent to Twitter API
# Uses the Tweepy Library

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

API = tweepy.API(auth)

#model = load_model('gs://all_the_feels_models/LSTMmultiv1.h5')
model = load_model('LSTMmultiv1.h5')
model._make_predict_function()
graph = tf.get_default_graph()

sinceId = None
max_id = -1

def preprocess(tweet):
    tweet = re.sub('@\w+', ' ', tweet)
    tweet = re.sub('[^A-Za-z1-9!? ]', ' ', tweet)
    tweet = tweet.lower()
    # stop_words = set(stopwords.words('english'))
    # tweet = word_tokenize(tweet)
    # tweet = [w for w in tweet if not w in stop_words]
    # tweet = ' '.join(tweet)
    tweet = one_hot(tweet, 3000, lower=False)
    processed = pad_sequences([tweet], 35, padding='post', truncating='post')
    return processed


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/search/<string:search_term>', methods=['POST', 'GET'])
def search(search_term):
    global graph


    tweetsPerQuery = 50
    documents = []
    sentiments = []
    total_score = 0
    json_array = []
    global max_id
    global sinceId

    emotions = ['Anger', 'Anticipation', 'Disgust', 'Fear', 'Joy', "Love", 'Optimism', "Pessimism", 'Sadness', 'Suprise', "Trust"]

    if(max_id <= 0):
        if(not sinceId):
            new_tweets = API.search(q=search_term, count=tweetsPerQuery, lang='en', tweet_mode='extended')
        else:
            new_tweets = API.search(q=search_term, count=tweetsPerQuery, lang='en', since_id=sinceId, tweet_mode='extended')
    else:
        if(not sinceId):
            new_tweets = API.search(q=search_term, count=tweetsPerQuery, lang='en', tweet_mode='extended', max_id=str(max_id - 1))
        else:
            new_tweets = API.search(q=search_term, count=tweetsPerQuery, lang='en', since_id=sinceId, tweet_mode='extended', max_id=str(max_id - 1))
        
    for tweet in new_tweets:
        print(tweet.full_text, file=sys.stderr)
        #ignore retweets
        try:
            if tweet.retweeted_status:
                continue
        except:
            #preprocess the tweet
            processed = preprocess(tweet.full_text)

            #run processed tweet through the model
            with graph.as_default():
                pred = model.predict(processed)

            #store tweet with prediction scores
            pred_dict = {}
            pred_dict['title'] = tweet.full_text
            pred_dict['name'] = '@' + tweet.user.screen_name

            for i in range(11):
                pred_dict[emotions[i]] = pred[i][0].tolist()[0]

            json_array.append(pred_dict.copy())

   #print(pred_dict, file=sys.stderr)

    max_id = new_tweets[-1].id
    return jsonify(json_array)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
