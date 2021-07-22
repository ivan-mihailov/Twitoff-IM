""""Main routing file for Twitoff Project"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from .models import db, User, Tweet
from .twitter import add_or_update_user
from .predict import predict_user

def create_app():
    """Create and configure an instance of the Flask appication."""
    
    app = Flask(__name__)
    
    load_dotenv()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URI')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    
    #Create tables
    with app.app_context():
        db.create_all()

    @app.route('/')
    def root():
        return render_template("base.html", title='home', \
            users = User.query.all())

    @app.route('/compare', methods=['POST'])
    def compare():
        # Get users and hypothetical tweet text from web app client
        user0, user1 = sorted([request.values['user0'], \
            request.values['user1']])
        hypo_tweet_text = request.values['tweet_text']

        # Raise an error if client tries to compare a user to themselves
        if user0 == user1:
            message = "Cannot compare users to themselves!"
        
        else:
            prediction = predict_user(user0, user1, hypo_tweet_text)
            message = '"{}" is more likely to be said by {} than by \
                {}'.format(
                    hypo_tweet_text, 
                    user1 if prediction else user0, 
                    user0 if prediction else user1
                    )

        return render_template('prediction.html', title='Prediction', message=message)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values["user_name"]
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = f"User {name} successfully added!"

            tweets = User.query.filter(User.username == name).one().tweets
        
        except Exception as e:
            message = f"Error adding {name}: {e}"
            tweets = []

        return render_template("user.html", title=name, tweets=tweets, message=message)

    @app.route('/populate')
    def populate():
        add_or_update_user("kimkardashian")
        add_or_update_user("jaden")
        return render_template("base.html", title="Home", users=User.query.all())

    @app.route('/reset')
    def reset():
        db.drop_all()
        db.create_all()
        return render_template("base.html", title="Home", users=User.query.all())

    @app.route('/update')
    def update():
        for user in User.query.all():
            add_or_update_user(user.username)

        return render_template('base.html', title='All users tweets were updated!', users=User.query.all())

    return app
    