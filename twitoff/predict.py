"""Prediction Model"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import vectorize_tweet

def predict_user(user0_name, user1_name, hypo_tweet_text):

    """
    Determines which user is more likely to have tweeted the hypothetical 
    tweet text supplied by the web app client.
    """
    # Captures users from our database
    user0 = User.query.filter(User.username == user0_name).one()
    user1 = User.query.filter(User.username == user1_name).one()

    # Captures the tweets from the users selected above
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    # Stack user vectored tweets in a single array
    vects = np.vstack([user0_vects, user1_vects])

    # Create labels for the stacked array
    labels = np.concatenate([np.zeros(len(user0.tweets)), \
        np.ones(len(user1.tweets))])
    
    # Set up and train Logistic Regression model
    log_reg = LogisticRegression().fit(vects, labels)

    # Vectorize hypothetical tweet and reshape array to match model
    hypo_tweet_vect = vectorize_tweet(hypo_tweet_text).reshape(1, -1)

    return log_reg.predict(hypo_tweet_vect)
