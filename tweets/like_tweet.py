from bottle import redirect, request, response, post
import uuid
import os
import jwt
import time
import sqlite3
import imghdr

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@post("/tweets/like/<tweet_id>")
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
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
            

            # connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")

            # insert new tweet to database
            db.execute("""
                INSERT INTO likes
                VALUES(
                    :user_id,
                    :tweet_id)
                """, (str(user_id), str(tweet_id)))
            db.commit()

            return

        except Exception as ex:
            print(ex)
            response.status = 500
            return redirect("/home")

        finally:
            if db != None:
                db.close()