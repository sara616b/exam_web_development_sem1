from bottle import get, view, request, redirect, response
import sqlite3
import jwt
import json

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY


@get("/home")
@view("home.html")
def _():

    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        return redirect("/login")
    else:
        db = None
        try:
            ###### connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")
            print("after check login")
            
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
            print(jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"])
            print(user_id)
            ###### select all tweets with user information
            tweet_values = ["tweet_id", "tweet_text", "tweet_created_at", "tweet_updated_at", "tweet_image", "tweet_user_id", "user_username", "user_display_name"]

            all_tweets_data = db.execute(f"""
                SELECT {','.join(tweet_values)}
                FROM tweets
                JOIN users
                WHERE tweets.tweet_user_id = users.user_id
                ORDER BY tweet_created_at DESC
                """).fetchall()
            
            # TODO - get all likes and add array of users who've liked the tweet to tweet (or a liked bool and the length of users who's liked it)
            
            all_likes_data = db.execute(f"""
                SELECT fk_user_id AS user_id, fk_tweet_id AS tweet_id
                FROM likes
                """).fetchall()

            tweets = {}
            for tweet in all_tweets_data:
                tweet_object = {}
                tweet_likes = []
                for index, value in enumerate(tweet_values):
                    tweet_object[value] = tweet[index]
                tweet_object["has_liked_tweet"] = False
                for index, like in enumerate(all_likes_data):
                    if like[1] == tweet_object["tweet_id"]:
                        tweet_likes.append(like)
                        if like[0] == user_id:
                            tweet_object["has_liked_tweet"] = True
                
                tweet_object["tweet_likes"] = len(tweet_likes)

                tweet_object["tweet_time_since_created"] = time_since_from_epoch(tweet_object["tweet_created_at"])
                tweet_object["tweet_updated_at_datetime"] = date_text_from_epoch(tweet_object["tweet_updated_at"]) if tweet_object["tweet_updated_at"] else None
                tweets[tweet_object["tweet_id"]] = tweet_object

            ###### select all users
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

            is_xhr = True if request.headers.get('spa') else False
            return dict(
                user_id=user_id,
                users=users,
                tweets=tweets,
                url="/home",
                title="Home",
                modal=None,
                is_xhr=is_xhr,
                )

        except Exception as ex:
            print(ex)
            print("exception")
            response.status = 500
            return

        finally:
            print("finally")
            if db != None:
                db.close()