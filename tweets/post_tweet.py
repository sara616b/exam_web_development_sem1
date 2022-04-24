from bottle import redirect, request, response, post
import uuid
import jwt
import time
import sqlite3
from common import get_file_path, check_the_image, is_uuid, validate_tweet_text, confirm_user_is_logged_in, JWT_KEY

@post("/tweets/new")
def _():
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    db = None
    redirect_path = None
    try:
        ##### user id of logged in user
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if not user_id or is_uuid(user_id) == False:
            redirect_path = "/home?alert-info=Trying to post tweet failed. Please try again."
            return
        
        ##### text - get and validate
        new_tweet_text, redirect_error_path = validate_tweet_text(request.forms.get("tweet_text"), "new")
        if redirect_error_path:
            redirect_path = redirect_error_path
            return
        new_tweet_text = new_tweet_text

        ##### check if there's an image in request.files and if so, validate it 
        redirect_image_error, image_name = check_the_image(request.files.get("tweet_image"), "tweets")
        if redirect_image_error:
            redirect_path = f"/tweets/new{redirect_image_error}&text={new_tweet_text}"
            return

        ##### append new tweet with values
        new_tweet = {
            "tweet_id": str(uuid.uuid4()),
            "tweet_text": new_tweet_text,
            "tweet_created_at": str(time.time()).split('.')[0],
            "tweet_updated_at": None,
            "tweet_image": image_name if image_name else None,
            "tweet_user_id": user_id,
        }

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ##### insert new tweet to database
        counter = db.execute("""
            INSERT INTO tweets
            VALUES(
                :tweet_id,
                :tweet_text,
                :tweet_created_at,
                :tweet_updated_at,
                :tweet_image,
                :tweet_user_id)
            """, new_tweet).rowcount
        
        ##### check that 1 and only 1 tweet was inserted
        if counter != 1:
            redirect_path = "/home?alert-info=Couldn't like tweet. Please try again."
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