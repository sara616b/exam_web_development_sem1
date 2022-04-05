from bottle import get, view, request, redirect, response
import sqlite3
import jwt
import datetime
import json

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@get("/profile/<profile_username>")
@view("profile.html")
def _(profile_username):
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        return redirect("/login")
    else:
        db = None
        try:
            ##### logged in user
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

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
            
            ##### select all likes data            
            all_likes_data = db.execute(f"""
                SELECT fk_user_id AS user_id, fk_tweet_id AS tweet_id
                FROM likes
                """).fetchall()

            
            ##### select all follow data            
            all_followers_data = db.execute(f"""
                SELECT fk_user_id_follower AS user_id_follower, fk_user_id_to_follow AS user_id_to_follow
                FROM followers
                """).fetchall()

            ##### organize tweet data into tweets dictionary
            tweets = {}
            for tweet in all_tweets_data:
                ##### tweet data to dictionary 
                tweet_object = {}
                for index, value in enumerate(tweet_values):
                    tweet_object[value] = tweet[index]
                
                ##### has the user liked the tweet and list of likes
                tweet_likes = []
                tweet_object["has_liked_tweet"] = False
                for index, like in enumerate(all_likes_data):
                    if like[1] == tweet_object["tweet_id"]:
                        tweet_likes.append(like)
                        if like[0] == user_id:
                            tweet_object["has_liked_tweet"] = True
                
                ##### number of likes
                tweet_object["tweet_likes"] = len(tweet_likes)

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
                
                ##### has the user liked the tweet and list of likes
                user_followed_by = []
                user_dict["is_following"] = False
                for index, follow in enumerate(all_followers_data):
                    if follow[1] == user_dict["user_id"]:
                        user_followed_by.append(follow)
                    if follow[1] == user_dict["user_id"] and follow[0] == user_id:
                        user_dict["is_following"] = True
                
                ##### number of likes
                user_dict["followers"] = len(user_followed_by)
            
            ###### specify user profile to display
            user_profile_to_display = None
            for user in users:
                if user["user_username"] == profile_username:
                    user_profile_to_display = user

            ##### check whether there's a need for loading header and footer
            is_xhr = True if request.headers.get('spa') else False

            ##### return view
            return dict(
                user_id=user_id,    # user who's logged in
                users=users,        # all users to display 'who to follow'
                tweets=tweets,      # all tweets for feed
                url=f"/profile/{profile_username}",        # url
                title=profile_username,       # title
                modal=None,         # what modal is opened
                is_xhr=is_xhr,      # load header and footer?
                user_profile_to_display=user_profile_to_display,
                )

        except Exception as ex:
            print(ex)
            response.status = 500
            return

        finally:
            if db != None:
                db.close()