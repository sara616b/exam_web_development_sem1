from bottle import get, view, request, redirect, response
import sqlite3
import jwt
import datetime
import json

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@get("/profile/<profile_username>")
@view("profile.html")
def _(profile_username):
    db = None
    try:
        # if logged in, get user_id from jwt cookie
        user_id = None
        if check_if_logged_in():
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        else:
            redirect("/")
        
        # connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        # get all tweets TODO use join
        tweets_from_user = db.execute("""
            SELECT *
            FROM tweets
            JOIN users
            WHERE tweets.tweet_user_id = users.user_id AND users.user_username = :username
            ORDER BY tweet_created_at DESC
            """, (profile_username,)).fetchall()
        
        
        profile_user_data = db.execute("""
            SELECT user_display_name, user_username, user_created_at
            FROM users
            WHERE user_username = :username
            """, (profile_username,)).fetchone()

        profile_user = {
            "user_display_name": profile_user_data[0],
            "user_username": profile_user_data[1],
            "user_created_at": profile_user_data[2],
        }

        # convert tweets data to dictionaries in tweets list with tweet and user informaiton
        tweets = {}
        for tweet in tweets_from_user:
            # get user info about the tweet's creator
            (user_username, user_display_name) = db.execute("""
                SELECT user_username, user_display_name
                FROM users
                WHERE user_id = :user_id
                """, (tweet[5],)).fetchone()

            tweets[tweet[0]] = {
                "tweet_text": tweet[1],
                "tweet_created_at": tweet[2],
                "tweet_time_since_created": time_since_from_epoch(tweet[2]),
                "tweet_updated_at": tweet[3],
                "tweet_updated_at_datetime": date_text_from_epoch(tweet[3]) if tweet[3] else None,
                "tweet_image": tweet[4],
                "tweet_user_id": tweet[5],
                "tweet_user_username": user_username,
                "tweet_user_display_name": user_display_name,
            }

        # get all users
        all_users = db.execute("""
            SELECT *
            FROM users
            WHERE user_id != :user_id
            ORDER BY user_created_at DESC
            """, (user_id,)).fetchall()
        users = []
        for user in all_users:
            users.append({
                "user_id": user[0],
                "user_display_name": user[1],
                "user_username": user[2],
            })

        if user_id:
            (user_id, user_display_name, user_username) = db.execute("""
                SELECT user_id, user_display_name, user_username
                FROM users
                WHERE  user_id = :user_id 
                """, (user_id,)).fetchone()
            db.commit()

            user = {
                "user_id": user_id,
                "user_display_name": user_display_name,
                "user_username": user_username,
            }

            return dict(user=user, tweets=tweets, other_users=users, profile_user=profile_user)
        return redirect("/")
        # return dict(tweets=tweets, user_id=user_id, is_logged_in=check_if_logged_in())

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/")

    finally:
        if db != None:
            db.close()

    # db = None
#     try:
#         if not check_if_logged_in():
#             return redirect("/login")

#         user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

#         db = sqlite3.connect("database/database.sqlite")
#         (user_first_name, user_last_name, user_username, user_email, user_created_at) = db.execute("""
#             SELECT user_first_name, user_last_name, user_username, user_email, user_created_at
#             FROM users
#             WHERE user_id = :user_id
#         """, (user_id,)).fetchone()

#         user = {
#             "user_first_name": user_first_name,
#             "user_last_name": user_last_name,
#             "user_username": user_username,
#             "user_email": user_email,
#             "user_created_at": datetime.datetime.fromtimestamp(int(user_created_at.split('.')[0])).strftime('%d/%m/%Y %H:%M'),
#         }

#         tweetsData = db.execute("""
#             SELECT tweet_id, tweet_text, tweet_created_at, tweet_updated_at, tweet_image, tweet_user_id, user_first_name, user_last_name, user_username
#             FROM tweets
#             JOIN users
#             WHERE tweets.tweet_user_id = users.user_id AND users.user_id = :user_id
#             ORDER BY tweet_created_at DESC
#             """, (user_id,)).fetchall()

#         tweets = {}
#         for tweet in tweetsData:
#             tweets[tweet[0]] = {
#                 "tweet_text": tweet[1],
#                 "tweet_created_at": tweet[2],
#                 "tweet_created_at_datetime": date_text_from_epoch(tweet[2]),
#                 "tweet_updated_at": tweet[3],
#                 "tweet_updated_at_datetime": date_text_from_epoch(tweet[3]) if tweet[3] else None,
#                 "tweet_image": tweet[4],
#                 "tweet_user_id": tweet[5],
#                 "tweet_user_first_name": tweet[6],
#                 "tweet_user_last_name": tweet[7],
#                 "tweet_user_username": tweet[8],
#             }
#         return dict(is_logged_in=check_if_logged_in(), user=user, user_id=user_id, tweets=tweets)

#     except Exception as ex:
#         print(ex)
#         response.status = 500
#         return redirect("/")
#     finally:
#         if db != None:
#             db.close()