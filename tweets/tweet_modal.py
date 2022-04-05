from bottle import get, redirect, request, view, response
import sqlite3
import jwt

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

# @get("/tweets")
@get("/tweets/<tweet_id>")
@view("home.html")
def _(tweet_id):
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        return redirect("/login")
    else:
        db = None
        redirectPath = None
        try:
            ###### connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")

            ##### get user id
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

            if tweet_id != 'new':
                ##### check that the tweet belongs to the user logged in
                tweet_and_user_id_match = len(db.execute(f"""
                    SELECT *
                    FROM tweets
                    WHERE tweet_id == :tweet_id AND tweet_user_id == :user_id
                    """, (tweet_id, user_id)).fetchall())
                if tweet_and_user_id_match != 1:
                    # redirectPath = "/home?error=notyourtweet"
                    redirectPath = "/home"
                    return

            ###### select all tweets with user information
            tweet_values = ["tweet_id", "tweet_text", "tweet_created_at", "tweet_updated_at", "tweet_image", "tweet_user_id", "user_username", "user_display_name"]
            all_tweets_data = db.execute(f"""
                SELECT {','.join(tweet_values)}
                FROM tweets
                JOIN users
                WHERE tweets.tweet_user_id = users.user_id
                ORDER BY tweet_created_at DESC
                """).fetchall()

            ###### select all likes 
            all_likes_data = db.execute(f"""
                SELECT fk_user_id AS user_id, fk_tweet_id AS tweet_id
                FROM likes
                """).fetchall()
    
            ###### organize tweets data with likes and time updates
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


            ##### select all follow data            
            all_followers_data = db.execute(f"""
                SELECT fk_user_id_follower AS user_id_follower, fk_user_id_to_follow AS user_id_to_follow
                FROM followers
                """).fetchall()

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

            is_xhr = True if request.headers.get('spa') else False
            if tweet_id == "new":
                return dict(
                    user_id=user_id,
                    users=users,
                    tweets=tweets,
                    tweet_id=tweet_id,
                    url="/tweets/" + tweet_id,
                    title="New tweet",
                    modal='tweet',
                    tweet=None,
                    is_xhr=is_xhr,
                    )
            
            tweet_to_edit = {}
            error = request.params.get("error")
            
            # get tweet info from database
            tweet = db.execute("""
                SELECT tweet_text, tweet_image
                FROM tweets
                WHERE tweet_id = :tweet_id
            """,(tweet_id,)).fetchone()

            # if tweet is found, set info that's needed to display the editing inputs
            if tweet:
                tweet_to_edit = {
                    "tweet_id": tweet_id,
                    "tweet_text": tweet[0],
                    "tweet_image": tweet[1]
                }
            
            # TODO redirect if tweet doesn't exist
            if not tweet:
                return redirect("/home")

            return dict(
                user_id=user_id,
                users=users,
                tweets=tweets,
                tweet_id=tweet_id,
                tweet=tweet_to_edit,
                url="/tweets/" + tweet_id,
                title="Edit tweet",
                modal='tweet',
                is_xhr=is_xhr
                )
                

        except Exception as ex:
            print(ex)
            response.status = 500
            # return redirect("/")
        finally:
            if db != None:
                db.close()
            if redirectPath:
                return redirect(redirectPath)