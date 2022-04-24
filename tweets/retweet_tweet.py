from bottle import redirect, request, response, post
import uuid
import jwt
import time
import sqlite3
from common import get_file_path, confirm_user_is_logged_in, is_uuid, JWT_KEY

@post("/tweets/retweet/<tweet_id>")
def _(tweet_id):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    db = None
    redirect_path = None
    try:
        ##### check whether the id is a uuid4
        if is_uuid(tweet_id) == False:
            redirect_path = "/home?alert-info=Trying to retweet the tweet failed. Please try again."
            return

        ##### user id of logged in user
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if not user_id or is_uuid(user_id) == False:
            redirect_path = "/home?alert-info=Trying to retweet the tweet failed. Please try again."
            return

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ##### insert retweet tweet to database
        counter = db.execute("""
            INSERT INTO retweets
            VALUES(
                :retweet_id,
                :user_id,
                :tweet_id,
                :retweeted_at)
                """, (str(uuid.uuid4()), str(user_id), str(tweet_id), str(time.time()).split('.')[0])).rowcount

        ##### check that 1 and only 1 retweet was inserted
        if counter != 1:
            redirect_path = "/home?alert-info=Couldn't retweet tweet. Please try again."
            return

        db.commit()
        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return

    finally:
        if db != None:
            db.close()
        if redirect_path != None:
            return redirect(redirect_path)