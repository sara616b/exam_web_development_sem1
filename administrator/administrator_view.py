from bottle import get, view, request, redirect, response
import sqlite3
import jwt
import json

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY


@get("/administrator")
@view("administrator.html")
def _():
    db = None
    try:
        ###### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        
        ###### select all tweets with user information
        tweet_values = ["tweet_id", "tweet_text", "tweet_created_at", "tweet_updated_at", "tweet_image", "tweet_user_id", "user_username", "user_display_name"]

        all_tweets_data = db.execute(f"""
            SELECT {','.join(tweet_values)}
            FROM tweets
            JOIN users
            WHERE tweets.tweet_user_id = users.user_id
            ORDER BY tweet_created_at DESC
            """).fetchall()
        
        ##### organize tweet data into tweets dictionary
        tweets = {}
        for tweet in all_tweets_data:
            ##### tweet data to dictionary 
            tweet_object = {}
            for index, value in enumerate(tweet_values):
                tweet_object[value] = tweet[index]

            ##### time since created and updated time
            tweet_object["tweet_time_since_created"] = time_since_from_epoch(tweet_object["tweet_created_at"])
            tweet_object["tweet_updated_at_datetime"] = date_text_from_epoch(tweet_object["tweet_updated_at"]) if tweet_object["tweet_updated_at"] else None
            tweets[tweet_object["tweet_id"]] = tweet_object

        ###### select all users and add to list
        users_values = ["user_id", "user_display_name", "user_username"]
        all_users = db.execute(f"""
            SELECT {','.join(users_values)}
            FROM users
            ORDER BY user_created_at DESC
            """).fetchall()

        users = []
        for user in all_users:
            user_dict = {}
            for index, value in enumerate(users_values):
                user_dict[value] = user[index]
            users.append(user_dict)

        ##### return view
        return dict(
            users=users,        # all users to display 'who to follow'
            tweets=tweets,      # all tweets for feed
            url="/administrator",        # url
            title="Administrator",       # title
            )

    except Exception as ex:
        print(ex)
        response.status = 500
        return

    finally:
        if db != None:
            db.close()