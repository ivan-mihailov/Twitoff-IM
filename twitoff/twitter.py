import os
from dotenv import load_dotenv
import tweepy
import numpy as np
import spacy
import en_core_web_sm
from .models import db, User, Tweet

# Authenticate user to allow use of the Twitter API
load_dotenv()
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_SECRET_KEY = os.getenv("TWITTER_SECRET_KEY")

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_SECRET_KEY)
api = tweepy.API(auth)

# NLP model load
nlp = spacy.load('en_core_web_sm')

# Function to transform tweet text into vector for use in Logistic Reg model
def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector

def add_or_update_user(username):

    """
    Takes a username and adds it to web app User database.
    Then downloads the same number of tweets from username and
    adds them to the Tweet database. 
    """
    try:
        twitter_user = api.get_user(username)

        if User.query.get(twitter_user.id):
            db_user = User(id=twitter_user.id, username=twitter_user)

            tweets = twitter_user.timeline(
                count=200,
                exclude_replies=True,
                include_rts=False,
                tweet_mode="extended"
            )

            for tweet in tweets:
                # Run vectorize_tweet function
                tweet_vector = vectorize_tweet(tweet.full_text)
                # Creating a Tweet object to add to Tweet database
                db_tweet = Tweet(id=tweet.id, text=tweet.full_text, \
                vect=tweet_vector)
                # Connects the tweet to the user through this tweets list 
                # (user.tweets)
                db_user.tweets.append(db_tweet)
                # Note: If we added before appending we would likely get an error
                db.session.add(db_tweet)
    
        else:
            db_user = User(id=twitter_user.id, username=username)
            db.session.add(db_user)

            tweets = twitter_user.timeline(
                count=200,
                exclude_replies=True,
                include_rts=False,
                tweet_mode="extended"
                #since_id=twitter_user.newest_tweet_id
            )
            if tweets:
                db_user.newest_tweet_id = tweets[0].id
            
            for tweet in tweets:
                # Run vectorize_tweet function
                tweet_vector = vectorize_tweet(tweet.full_text)
                # Creating a Tweet object to add to Tweet database
                db_tweet = Tweet(id=tweet.id, text=tweet.full_text, \
                vect=tweet_vector)
                # Connects the tweet to the user through this tweets list 
                # (user.tweets)
                db_user.tweets.append(db_tweet)
                # Note: If we added before appending we would likely get an error
                db.session.add(db_tweet)
    
    except Exception as e:
            print(f"Error Processing {username}: {e}")
            raise e
    
    else:
        db.session.commit()
