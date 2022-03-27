from bottle import get, view, request, redirect
import sqlite3
import jwt

from settings import *

@get("/home")
@view("home.html")
def _():
    db = None
    try:
        # connect to database
        # db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        # # get all tweets
        # all_tweets_data = db.execute("""
        #     SELECT *
        #     FROM tweets
        #     ORDER BY tweet_created_at DESC
        #     """).fetchall()

        # if logged in, get user_id from jwt cookie
        user_id = None
        # if check_if_logged_in():
        #     user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

        # convert tweets data to dictionaries in tweets list with tweet and user informaiton
        tweets = {}
        # for tweet in all_tweets_data:
        #     # get user info about the tweet's creator
        #     (user_username, user_first_name, user_last_name) = db.execute("""
        #         SELECT user_username, user_first_name, user_last_name
        #         FROM users
        #         WHERE user_id = :user_id
        #         """, (tweet[5],)).fetchone()

        #     tweets[tweet[0]] = {
        #         "tweet_text": tweet[1],
        #         "tweet_created_at": tweet[2],
        #         "tweet_created_at_datetime": date_text_from_epoch(tweet[2]),
        #         "tweet_updated_at": tweet[3],
        #         "tweet_updated_at_datetime": date_text_from_epoch(tweet[3]) if tweet[3] else None,
        #         "tweet_image": tweet[4],
        #         "tweet_user_id": tweet[5],
        #         "tweet_user_username": user_username,
        #         "tweet_user_first_name": user_first_name,
        #         "tweet_user_last_name": user_last_name,
        #     }

        return
        # return dict(tweets=tweets, user_id=user_id, is_logged_in=check_if_logged_in())

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/")

    finally:
        if db != None:
            db.close()
