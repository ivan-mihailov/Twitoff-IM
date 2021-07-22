"""SQLAlchemy models and utility functions for Twitoff Application"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Create a 'user' table
class User(db.Model):
    """
    Twitter User Table that will correspond to tweets - SQLAlchemy syntax
    """
    id = db.Column(db.BigInteger, primary_key = True) # id as Primary Key
    username = db.Column(db.Unicode(100), nullable = False) # username
    # stores most recent tweet_id
    newest_tweet_id = db.Column(db.BigInteger)
    
    def __repr__(self):
        return "<User: {}>".format(self.name)

# Create a 'tweet' table
class Tweet(db.Model):
    """Tweet text data associated with Users Table"""
    # id for Tweet as Primary Key
    id = db.Column(db.BigInteger, primary_key = True)
    # Text of the Tweet
    text = db.Column(db.Unicode(300))
    # Text of Tweet after running SpaCy Model
    vect = db.Column(db.PickleType, nullable=False)
    # user_id foreign key column for 'tweet'
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), \
        nullable = False)
    # Creating a realtionship between tweets and users
    user = db.relationship('User', backref = db.backref('tweets', \
        lazy =  True))
    
    def __repr__(self):
        return "<Tweet: {}>".format(self.text)
