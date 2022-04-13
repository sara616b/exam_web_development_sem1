from bottle import redirect, request, response, delete
import uuid
import os
import jwt
import time
import sqlite3
import imghdr

from settings import get_file_path, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@delete("/tweets/like/<tweet_id>")
def _(tweet_id):
    
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    db = None
    try:
        # decode jwt cookie to get user id for new tweet
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        
        # connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        # delete like from database
        db.execute("""
            DELETE FROM likes
            WHERE fk_tweet_id = :tweet_id
            AND fk_user_id = :user_id
            """, (tweet_id, user_id))
        db.commit()
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/home")

    finally:
        if db != None:
            db.close()