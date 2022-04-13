from bottle import request, response, redirect
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
                ##### find the users who match the jwt session cookie
                session_matches_user = str(db.execute("""
                        SELECT user_current_session, user_id
                        FROM users
                        WHERE user_current_session = :user_current_session
                        """, (str(jwt_cookie),)).fetchone())

                ##### if it matches a user, return true - someone is logged in with a valid session
                if session_matches_user != None:
                    if session_matches_user[0]:
                        return True
                
        return False

    except Exception as ex:
        print(f"Exception: {ex}")
        return False

    finally:
        if db != None:
            db.close()

def time_since_from_epoch(epoch):
    time_since_seconds = int(time.time()) - int(epoch.split('.')[0])
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
    
    time_since = f"{str(datetime.datetime.fromtimestamp(int(epoch.split('.')[0])).strftime('%B %d'))}"
    return time_since

def date_text_from_epoch(epoch):
    return datetime.datetime.fromtimestamp(int(epoch.split('.')[0])).strftime('%d/%m/%Y %H:%M')

def get_file_path():
    try:
      import production
      return "/home/buzzer/site"
    except:
      return "."

def create_dictionary_from_data(values, data):
    result_dict = {}
    for index, value in enumerate(values):
        result_dict[value] = data[index]
    return result_dict

def is_uuid(id):
  if not id: return False
  regex_uuid4 = "^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
  if not re.match(regex_uuid4, id) : return False
  return True

def get_all_tweets(user_id): # if user_id == None, likes data won't be included
    
    # print('get all tweets')

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
        # print(all_retweets_data)

    ##### organize tweet data into tweets dictionary
    tweets = {}
    for tweet in all_tweets_data:
        ##### tweet data to dictionary 
        tweet_dict = create_dictionary_from_data(tweet_values, tweet)

        if user_id:
            ##### has the user liked the tweet and list of likes
            tweet_dict["tweet_likes"] = 0
            tweet_dict["has_liked_tweet"] = False
            for like in all_likes_data:
                ##### if like['tweet_id'] is current tweet's id increse likes amount +1
                if like[1] == tweet_dict["tweet_id"]:
                    tweet_dict["tweet_likes"] += 1
                    ##### if also like['user_id'] is the logged in user, set has_liked_tweet to True
                    if like[0] == user_id:
                        tweet_dict["has_liked_tweet"] = True
            
            ##### retweets
            tweet_dict["tweet_retweets"] = 0
            tweet_dict["has_retweeted_tweet"] = False
            for retweet in all_retweets_data:
                ##### if like['tweet_id'] is current tweet's id increse likes amount +1
                if retweet[2] == tweet_dict["tweet_id"]:
                    tweet_dict["tweet_retweets"] += 1
                    ##### if also like['user_id'] is the logged in user, set has_liked_tweet to True
                    if retweet[1] == user_id:
                        tweet_dict["has_retweeted_tweet"] = True

        ##### time since created and updated time
        tweet_dict["tweet_time_since_created"] = time_since_from_epoch(tweet_dict["tweet_created_at"])
        tweet_dict["tweet_updated_at_datetime"] = date_text_from_epoch(tweet_dict["tweet_updated_at"]) if tweet_dict["tweet_updated_at"] else None

        ##### add tweet to all tweets dictionary
        tweets[tweet_dict["tweet_id"]] = tweet_dict
    
    db.close()

    return tweets

def get_all_users(user_id): # if user_id == None, follower data won't be included
    ###### connect to database
    db = sqlite3.connect(f"{get_file_path()}/database/database.db")

    ###### select all users and add to list
    users_values = ["user_id", "user_display_name", "user_username"]
    all_users = db.execute(f"""
        SELECT {','.join(users_values)}
        FROM users
        ORDER BY user_created_at DESC
        """).fetchall()
    
    if user_id:
        ##### select all follow data            
        all_followers_data = db.execute(f"""
            SELECT fk_user_id_follower AS user_id_follower, fk_user_id_to_follow AS user_id_to_follow
            FROM followers
            """).fetchall()

    users = []
    for user in all_users:
        user_dict = create_dictionary_from_data(users_values, user)

        if user_id:
            ##### user followers and followings
            user_dict["followers"] = 0
            user_dict["is_following"] = False
            for follow in all_followers_data:
                if follow[1] == user_dict["user_id"]:
                    user_dict["followers"] += 1
                    if follow[0] == user_id:
                        user_dict["is_following"] = True

        users.append(user_dict)
    
    db.close()

    return users

def get_all_posts(user_id, only_include_from_user_id=None):
    try:
        if not is_uuid(user_id):
            response.status = 500
            return

        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        
        if only_include_from_user_id != None:
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

        db.close()

        posts = []

        for retweet in all_retweets_data:
            retweet_dict = create_dictionary_from_data(["retweet_id", "user_id", "tweet_id", "retweeted_at"], retweet)
            retweet_dict["latest_updated_at"] = retweet_dict["retweeted_at"]
            retweet_dict["type"] = "retweet"
            posts.append(retweet_dict)

        tweets = get_all_tweets(user_id)
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

        sorted_posts = sorted(posts, key=lambda d: d["latest_updated_at"], reverse=True)
        return sorted_posts
    
    except Exception as ex:
        print(f"Exception: {ex}")
        response.status = 500
        return

def check_the_image(image_file):
    image_name = None
    if image_file:
        # get extention and validate
        file_name, file_extension = os.path.splitext(image_file.filename)
        if file_extension.lower() == ".jpg": file_extension = ".jpeg"
        if file_extension.lower() not in (".png", ".jpg", ".jpeg"):
            redirectPath = f"/tweets/new?error=image-not-allowed"
            return redirectPath, image_name

        # image name
        image_name = f"{str(uuid.uuid4())}{file_extension}"

        # save image
        image_file.save(f"{get_file_path()}/static/images/tweets/{image_name}")

        # is the image valid
        imghdr_extension = imghdr.what(f"{get_file_path()}/static/images/tweets/{image_name}")
        if file_extension != f".{imghdr_extension}":
            # delete the invalid image 
            os.remove(f"{get_file_path()}/static/images/tweets/{image_name}")
            redirectPath = f"/tweets/new?error=image-not-allowed"
            return redirectPath, image_name
    return None, image_name

def validate_tweet_text(tweet_text, tweet_id):
    if not tweet_text:
        # text is required in tweets
        response.status = 204
        redirectPath = f"/tweets/{tweet_id}?error=empty"
        return None, redirectPath
    if len(tweet_text) < 2:
        response.status = 400
        redirectPath = f"/tweets/{tweet_id}?error=short&text={tweet_text}"
        return None, redirectPath
    if len(tweet_text) > 250:
        response.status = 400
        redirectPath = f"/tweets/{tweet_id}?error=long&text={tweet_text}"
        return None, redirectPath

    if tweet_text:
        return tweet_text, None
    
    return None, None

##### delete tweet, all connected likes, and any possible image
def delete_tweet(tweet_id):
    if not is_uuid(tweet_id):
        response.status = 500
        return
    # connect to database
    db = sqlite3.connect(f"{get_file_path()}/database/database.db")

    # find image and delete it from the folder if it exists
    tweet_image = db.execute("""
        SELECT tweet_image
        FROM tweets
        WHERE tweet_id = :tweet_id
        """, (tweet_id,)).fetchone()[0]
    if tweet_image:
        if os.path.exists(f"{get_file_path()}/static/images/tweets/{tweet_image}"):
            os.remove(f"{get_file_path()}/static/images/tweets/{tweet_image}")

    # delete tweet from database
    counter = db.execute("""
        DELETE FROM tweets
        WHERE tweet_id = :tweet_id
        """, (tweet_id,)).rowcount

    # delete tweet likes from database
    db.execute("""
        DELETE FROM likes
        WHERE fk_tweet_id = :tweet_id
        """, (tweet_id,))
    
    # delete tweet retweet from database
    db.execute("""
        DELETE FROM retweets
        WHERE fk_tweet_id = :tweet_id
        """, (tweet_id,))

    db.commit()
    db.close()
    return counter

##### delete tweet, all connected likes, and any possible image
def delete_retweet(retweet_id):
    # connect to database
    db = sqlite3.connect(f"{get_file_path()}/database/database.db")

    # delete tweet from database
    counter = db.execute("""
        DELETE FROM retweets
        WHERE retweet_id = :retweet_id
        """, (retweet_id,)).rowcount
        
    db.commit()
    db.close()
    return counter

def only_update_body():
    only_update_body = True if request.headers.get('spa') else False
    return only_update_body

# from bottle import response
# import sqlite3
# import re

# _errors = {
#   "en_server_error":"server error",
#   "dk_server_error":"server fejl",
#   "sv_server_error":"serverfel",
#   "en_json_error":"invalid json",
#   "dk_json_error":"ugyldigt json",  
# }

# ##############################
# def _send(status = 400, error_message = "unknown error"):
#   response.status = status
#   return {"info":error_message}

# ##############################
# def _is_item_name(text=None, language="en"):
#   min, max = 2, 20
#   errors = {
#     "en":f"item_name {min} to {max} characters. No spaces", 
#     "dk":f"item_name {min} til {max} tegn. Uden mellemrum",
#     "sv":f"item_name {min} till {max} tegn. Inga mellanrum ",
#   }
#   if not text: return None, errors[language]
#   text = re.sub("[\n\t]*", "", text)
#   text = re.sub(" +", " ", text)
#   text = text.strip()
#   if len(text) < min or len(text) > max : return None, errors[language]
#   # if " " in text : return None, errors[language]
#   text = text.capitalize()
#   return text, None

# ##############################
# def _is_item_description(text=None, language="en"):
#   min, max = 10, 500
#   errors = {
#     "en":f"item_description {min} to {max} characters", 
#     "dk":f"item_description {min} til {max} tegn",
#     "sv":f"item_description {min} till {max} tegn",
#   }
#   if not text: return None, errors[language]
#   # text = re.sub("[\n\t]*", "", text)
#   # text = re.sub(" +", " ", text)
#   text = text.strip()
#   if len(text) < min or len(text) > max : return None, errors[language]
#   return text, None

# ##############################
# def _is_item_price(text=None, language="en"):
#   errors = {
#     "en":f"item_price must be a number with two decimals divided by a comma, and cannot start with zero", 
#     "dk":f"item_price skal være et tal med to decimaler divideret med et komma, og må ikke starte med nul",
#     "sv":f"item_price måste vara ett tal med två decimaler delat med ett kommatecken och får inte börja med noll"
#   }
#   if not text : return None, errors[language]
#   if not ',' in text:
#     text = f"{text},00"
#   if not re.match("^[1-9][0-9]*[,][0-9]{2}$", text) : return None, errors[language]
#   return text, None

# ##############################
# def _is_uuid4(text=None, language="en"):
#   errors = {
#     "en":f"item_id must be uuid4", 
#     "dk":f"item_id skal være uuid4",
#     "sv":f"item_id måste vara uuid4"
#   }
#   if not text: return None, errors[language]
#   regex_uuid4 = "^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
#   if not re.match(regex_uuid4, text) : return None, errors[language]
#   return text, None

# ##############################
# def create_json_from_sqlite_result(cursor, row):
#   d = {}
#   for idx, col in enumerate(cursor.description):
#     d[col[0]] = row[idx]
#   return d

# ##############################
# def _db_connect(db_name):
#   db = sqlite3.connect(db_name)
#   db.row_factory = create_json_from_sqlite_result
#   return db
