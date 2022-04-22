from bottle import request, response
import jwt
from jwt.exceptions import InvalidSignatureError
import sqlite3
import uuid
import time
import os
import re
import imghdr
import datetime

JWT_KEY = f"{str(uuid.uuid4())}-{str(uuid.uuid4())}-{str(uuid.uuid4())}"
REGEX_EMAIL = '^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
REGEX_NO_SPECIAL_CHARACTERS = '^[A-Za-z0-9 ]+$'
REGEX_HEX_COLOR = '^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'

##### file paths are different in development and production
def get_file_path():
    try:
      import production
      return "/home/buzzer/site"
    except:
      return "."

##### if a user is logged in it returns true otherwise it returns false
def confirm_user_is_logged_in():
    db = None
    try:
        ##### get cookie
        jwt_cookie = request.get_cookie("jwt", secret="secret")
        if (jwt_cookie):
            ##### try to decode or return if signature verfication fails
            try: 
                jwt.decode(
                    jwt_cookie,
                    JWT_KEY, algorithms=["HS256"]
                ) or None

            except InvalidSignatureError as error:
                print(f"Invalid signature error: {error}")
                return False

            else:
                db = sqlite3.connect(f"{get_file_path()}/database/database.db")
                ##### find the users who matches the jwt session cookie
                session_matches_user = str(db.execute("""
                        SELECT user_current_session, user_id
                        FROM users
                        WHERE user_current_session = :user_current_session
                        """, (str(jwt_cookie),)).fetchone())

                ##### if it matches a user, return true - someone is logged in with a valid session
                if session_matches_user != None:
                    return True

        return False

    except Exception as ex:
        print("Exception: " + str(ex))
        return False

    finally:
        if db != None:
            db.close()

##### get string of amount of time since posting from epoch value
def time_since_from_epoch(epoch):
    time_since_seconds = int(time.time()) - int(epoch.split('.')[0]) # now minus posting time
    if time_since_seconds < 60:
        return f"{str(time_since_seconds).split('.')[0]}s"

    time_since_minutes = time_since_seconds / 60
    if time_since_minutes < 60:
        return f"{str(time_since_minutes).split('.')[0]}m"

    time_since_hours = time_since_minutes / 60
    if time_since_hours < 24:
        return f"{str(time_since_hours).split('.')[0]}h"

    time_since_days = time_since_hours / 24
    if time_since_days < 7:
        return f"{str(time_since_days).split('.')[0]}d"

    date_string = f"{str(datetime.datetime.fromtimestamp(int(epoch.split('.')[0])).strftime('%B %d'))}"
    return date_string

##### returns dictionary based on a list of values strings and sqlite data
def create_dictionary_from_sqlite_data(values, data):
    result_dict = {}
    for index, value in enumerate(values):
        result_dict[value] = data[index]
    return result_dict

##### check id against uuid4 regex
def is_uuid(id):
  if not id: return False
  regex_uuid4 = "^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
  if not re.match(regex_uuid4, id): return False
  return True

##### get all tweets as dictionary
def get_all_tweets(user_id): # if user_id == None, likes data won't be included
    db = None
    try:
        ###### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ###### select all tweets joined with user information
        tweet_values = ["tweet_id", "tweet_text", "tweet_created_at", "tweet_updated_at", "tweet_image", "tweet_user_id", "user_username", "user_display_name"]
        all_tweets_data = db.execute(f"""
            SELECT {','.join(tweet_values)}
            FROM tweets
            JOIN users
            WHERE tweets.tweet_user_id = users.user_id
            ORDER BY tweet_created_at DESC
            """).fetchall()

        if user_id:
            ##### check if the user_id is a uuid4
            if not is_uuid(user_id):
                response.status = 500
                return    
            ##### select all likes data            
            all_likes_data = db.execute(f"""
                SELECT fk_user_id AS user_id, fk_tweet_id AS tweet_id
                FROM likes
                """).fetchall()
        
            ##### select all retweets data           
            all_retweets_data = db.execute(f"""
                SELECT retweet_id, fk_user_id AS user_id, fk_tweet_id AS tweet_id, retweeted_at
                FROM retweets
                """).fetchall()

        ##### organize tweets data into tweets dictionary
        tweets = {}
        for tweet in all_tweets_data:
            ##### tweet data to dictionary 
            tweet_dict = create_dictionary_from_sqlite_data(tweet_values, tweet)

            if user_id:
                ##### has the user liked the tweet and amount of likes
                tweet_dict["tweet_likes"] = 0
                tweet_dict["has_liked_tweet"] = False
                for like in all_likes_data:
                    ##### if like['tweet_id'] is current tweet's id increase likes amount +1
                    if like[1] == tweet_dict["tweet_id"]:
                        tweet_dict["tweet_likes"] += 1
                        ##### if also like['user_id'] is the logged in user, set has_liked_tweet to True
                        if like[0] == user_id:
                            tweet_dict["has_liked_tweet"] = True

                ##### retweets
                tweet_dict["tweet_retweets"] = 0
                tweet_dict["has_retweeted_tweet"] = False
                for retweet in all_retweets_data:
                    ##### if retweet['tweet_id'] is current tweet's id increase retweet amount +1
                    if retweet[2] == tweet_dict["tweet_id"]:
                        tweet_dict["tweet_retweets"] += 1
                        ##### if also retweet['user_id'] is the logged in user, set has_retweeted_tweet to True
                        if retweet[1] == user_id:
                            tweet_dict["has_retweeted_tweet"] = True

            ##### time since created and updated
            tweet_dict["tweet_time_since_created"] = time_since_from_epoch(tweet_dict["tweet_created_at"])
            tweet_dict["tweet_time_since_updated"] = time_since_from_epoch(tweet_dict["tweet_updated_at"]) if tweet_dict["tweet_updated_at"] else None

            ##### add tweet to all tweets dictionary
            tweets[tweet_dict["tweet_id"]] = tweet_dict

        return tweets
    
    except Exception as ex:
        print("Exception: " + str(ex))
        return False

    finally:
        if db != None:
            db.close()

##### get all users data as dictionary
def get_all_users(user_id): # if user_id == None, follower data won't be included
    db = None
    try:
        ###### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ###### select all users
        users_values = ["user_id", "user_display_name", "user_username", "user_profile_image", "user_profile_header", "user_is_verified"]
        all_users = db.execute(f"""
            SELECT {','.join(users_values)}
            FROM users
            ORDER BY user_created_at DESC
            """).fetchall()

        if user_id:
            ##### check if the user_id is a uuid4
            if not is_uuid(user_id):
                response.status = 500
                return
            ##### select all follow data            
        ##### select all follow data            
            ##### select all follow data            
        ##### select all follow data            
            ##### select all follow data            
            all_followers_data = db.execute(f"""
                SELECT fk_user_id_follower AS user_id_follower, fk_user_id_to_follow AS user_id_to_follow
                FROM followers
                """).fetchall()

        ##### organize users data in list
        users = []
        for user in all_users:
            user_dict = create_dictionary_from_sqlite_data(users_values, user)

            if user_id:
                ##### user followers and followings
                user_dict["followers"] = 0
                user_dict["is_following"] = False
                for follow in all_followers_data:
                    ##### if follow['user_id_to_follow'] is this user, add to followers amount
                    if follow[1] == user_dict["user_id"]:
                        user_dict["followers"] += 1
                        ##### if follow['user_id_follower'] is the logged in user set is_following to True
                        if follow[0] == user_id:
                            user_dict["is_following"] = True

            users.append(user_dict)

        return users

    except Exception as ex:
        print("Exception: " + str(ex))
        return False

    finally:
        if db != None:
            db.close()

##### get all posts (tweets and retweets) in a chronologically ordered list 
def get_all_posts(user_id, only_include_from_user_id=None):
    db = None
    try:
        ##### check that the user_id is a uuid4
        if not is_uuid(user_id):
            response.status = 500
            return

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        
        ##### get all retweets data (either all or only all from one user)
        if only_include_from_user_id != None:
            if not is_uuid(only_include_from_user_id):
                response.status = 500
                return
            all_retweets_data = db.execute(f"""
                SELECT retweet_id, fk_user_id AS user_id, fk_tweet_id AS tweet_id, retweeted_at
                FROM retweets
                WHERE fk_user_id = :user_id
                ORDER BY retweeted_at DESC
                """, (only_include_from_user_id,)).fetchall()
            
        else:
            all_retweets_data = db.execute(f"""
                SELECT retweet_id, fk_user_id AS user_id, fk_tweet_id AS tweet_id, retweeted_at
                FROM retweets
                ORDER BY retweeted_at DESC
                """).fetchall()

        ##### get all tweets data
        tweets = get_all_tweets(user_id)

        posts = []

        ##### are there even tweets and retweets?
        if len(tweets) == 0 and len(all_retweets_data) == 0:
            return posts

        ##### add retweets to posts list
        for retweet in all_retweets_data:
            retweet_dict = create_dictionary_from_sqlite_data(["retweet_id", "user_id", "tweet_id", "retweeted_at"], retweet)
            retweet_dict["latest_updated_at"] = retweet_dict["retweeted_at"]
            retweet_dict["type"] = "retweet"
            posts.append(retweet_dict)

        ##### add tweets to posts list
        for tweet in tweets:
            post = {
                "tweet_id": tweets[tweet]['tweet_id'],
                "tweet_user_id": tweets[tweet]['tweet_user_id'],
                "latest_updated_at": tweets[tweet]["tweet_updated_at"] if tweets[tweet]["tweet_updated_at"] != None else tweets[tweet]["tweet_created_at"],
                "type": "tweet",
            }
            if only_include_from_user_id != None and tweets[tweet]["tweet_user_id"] == only_include_from_user_id:
                posts.append(post)
            elif only_include_from_user_id == None:
                posts.append(post)

        ##### sort all posts by the lasted time updated
        sorted_posts = sorted(posts, key=lambda d: d["latest_updated_at"], reverse=True)
        return sorted_posts
    
    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return
    
    finally:
        if db != None:
            db.close()

##### check an image based on extention and corruption - returns a redirection path if an error is found and the image name
def check_the_image(image_file, type):
    try:
        image_name = None
        if image_file:
            # get extention and validate
            file_name, file_extension = os.path.splitext(image_file.filename)
            if file_extension.lower() == ".jpg": file_extension = ".jpeg"
            if file_extension.lower() not in (".png", ".jpg", ".jpeg"):
                redirect_path = f"?error=image-not-allowed"
                return redirect_path, image_name

            # image name
            image_name = f"{str(uuid.uuid4())}{file_extension}"

            # save image
            image_file.save(f"{get_file_path()}/static/images/{type}/{image_name}")

            # is the image corrupted/valid
            imghdr_extension = imghdr.what(f"{get_file_path()}/static/images/{type}/{image_name}")
            if file_extension != f".{imghdr_extension}":
                # delete the corrupted/invalid image
                os.remove(f"{get_file_path()}/static/images/{type}/{image_name}")
                redirect_path = f"?error=image-not-allowed"
                return redirect_path, image_name

        return None, image_name
    
    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return

##### validate tweet text - returns the text and a redirection path if an error is found
def validate_tweet_text(tweet_text, tweet_id):
    if not tweet_text:
        # text is required in tweets
        response.status = 204
        redirect_path = f"/tweets/{tweet_id}?error=empty"
        return None, redirect_path

    if len(tweet_text) < 2:
        # text must be longer than 2 characters
        response.status = 400
        redirect_path = f"/tweets/{tweet_id}?error=short&text={tweet_text}"
        return None, redirect_path

    if len(tweet_text) > 250:
        # text must be shorter than 250 characters
        response.status = 400
        redirect_path = f"/tweets/{tweet_id}?error=long&text={tweet_text}"
        return None, redirect_path

    if tweet_text:
        return tweet_text, None

    return None, None

##### delete tweet, all connected likes, retweets, and any possible image
def delete_tweet(tweet_id):
    db = None
    try:
        ##### check if id is a uuid4
        if not is_uuid(tweet_id):
            response.status = 500
            return

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ##### find image and delete it from the folder if it exists
        tweet_image = db.execute("""
            SELECT tweet_image
            FROM tweets
            WHERE tweet_id = :tweet_id
            """, (tweet_id,)).fetchone()[0]
        if tweet_image:
            if os.path.exists(f"{get_file_path()}/static/images/tweets/{tweet_image}"):
                os.remove(f"{get_file_path()}/static/images/tweets/{tweet_image}")

        ##### delete tweet from database
        counter = db.execute("""
            DELETE FROM tweets
            WHERE tweet_id = :tweet_id
            """, (tweet_id,)).rowcount

        ##### delete tweet likes from database
        db.execute("""
            DELETE FROM likes
            WHERE fk_tweet_id = :tweet_id
            """, (tweet_id,))
        
        ##### delete tweet retweet from database
        db.execute("""
            DELETE FROM retweets
            WHERE fk_tweet_id = :tweet_id
            """, (tweet_id,))

        db.commit()

        ##### return the count of tweets deleted (should be 1)
        return counter
    
    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return
    
    finally:
        if db != None:
            db.close()

##### delete retweet
def delete_retweet(retweet_id):
    db = None
    try:
        ##### check if id is a uuid4
        if not is_uuid(retweet_id):
            response.status = 500
            return

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ##### delete retweet from database
        counter = db.execute("""
            DELETE FROM retweets
            WHERE retweet_id = :retweet_id
            """, (retweet_id,)).rowcount

        db.commit()

        ##### return count of retweets deleted (should be 1)
        return counter

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return

    finally:
        if db != None:
            db.close()

##### check request headers for containing 'spa' and thereby if only the body needs to updated in the view
def only_update_body():
    only_update_body = True if request.headers.get('spa') else False
    return only_update_body
