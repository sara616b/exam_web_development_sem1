from bottle import redirect, request, response, delete
import uuid
import os
import jwt
import time
import sqlite3
import imghdr

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@delete("/tweets/like/<tweet_id>")
def _(tweet_id):
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        return redirect("/login")
    else:
        db = None
        try:
            user_id = None
            # decode jwt cookie to get user id for new tweet
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
            
            # connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")

            # delete tweet from database
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