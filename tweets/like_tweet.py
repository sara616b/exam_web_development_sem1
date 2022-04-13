from bottle import redirect, request, response, post
import uuid
import os
import jwt
import time
import sqlite3
import imghdr

from settings import get_file_path, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@post("/tweets/like/<tweet_id>")
def _(tweet_id):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    db = None
    try:
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