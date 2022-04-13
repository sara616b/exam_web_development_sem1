from bottle import redirect, request, response, post
import uuid
import os
import jwt
import time
import sqlite3
import imghdr

from settings import get_file_path, check_the_image, validate_tweet_text, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@post("/tweets/new")
def _():
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    db = None
    redirectPath = None
    try:
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        
        # text
        new_tweet_text, redirect_error_path = validate_tweet_text(request.forms.get("tweet_text"), "new")
        if redirect_error_path:
            redirectPath = redirect_error_path
            return
        new_tweet_text = new_tweet_text.replace("\n", "<br />")

        ##### check if there's an image in request.files and if so, validate it 
        redirect_image_error, image_name = check_the_image(request.files.get("tweet_image"))
        if redirect_image_error:
            redirectPath = f"{redirect_image_error}&text={new_tweet_text}"
            return

        # append new tweet with values
        new_tweet = {
            "tweet_id": str(uuid.uuid4()),
            "tweet_text": new_tweet_text,
            "tweet_created_at": str(time.time()),
            "tweet_updated_at": None,
            "tweet_image": image_name if image_name else None,
            "tweet_user_id": user_id,
        }

        # connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        # insert new tweet to database
        db.execute("""
            INSERT INTO tweets
            VALUES(
                :tweet_id,
                :tweet_text,
                :tweet_created_at,
                :tweet_updated_at,
                :tweet_image,
                :tweet_user_id)
            """, new_tweet)
        db.commit()

        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return

    finally:
        if db != None: db.close()
        if redirectPath: return redirect(redirectPath)