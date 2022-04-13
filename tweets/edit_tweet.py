from bottle import redirect, request, put, post, response
import time
import sqlite3
import os
import imghdr
import uuid
import jwt

from settings import get_file_path, validate_tweet_text, check_the_image, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@put("/tweets/<tweet_id>")
def _(tweet_id):
        
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    db = None
    redirectPath = None

    try:
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        
        updated_tweet_data = {"tweet_id":tweet_id}

        ##### connect database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ##### check that the tweet belongs to the user logged in
        tweet_and_user_id_match = len(db.execute(f"""
            SELECT *
            FROM tweets
            WHERE tweet_id == :tweet_id AND tweet_user_id == :user_id
            """, (tweet_id, user_id)).fetchall())
        if tweet_and_user_id_match != 1:
            return

        # tweet text - get + if found, validate and add to update values
        tweet_text = request.forms.get("tweet_text")
        tweet_text, redirect_error_path = validate_tweet_text(tweet_text, tweet_id)
        if redirect_error_path:
            redirectPath = redirect_error_path
            return
        
        if tweet_text:
            updated_tweet_data["tweet_text"] = tweet_text

        # image - remove, add new
        current_image = db.execute(f"""
            SELECT tweet_image
            FROM tweets
            WHERE tweet_id == :tweet_id
            """, (tweet_id,)).fetchone()[0]

        new_image_name = None
        image_name = request.forms.get("image_name")
        if not current_image or current_image != image_name:
            if os.path.exists(f"assets/images/{current_image}"):
                os.remove(f"assets/images/{current_image}")
            updated_tweet_data["tweet_image"] = None
            
            ##### check if there's an image in request.files and if so, validate it 
            redirect_image_error, new_image_name = check_the_image(request.files.get("tweet_image"))
            if redirect_image_error:
                redirectPath = f"{redirect_image_error}&text={tweet_text}"
                return

            if new_image_name:
                updated_tweet_data["tweet_image"] = new_image_name

        # set updated at time
        updated_tweet_data["tweet_updated_at"] = time.time()

        # create string for all values that need to be set in the database query
        set_parts = []
        for value in updated_tweet_data:
            if str(value) != "tweet_id":
                set_parts.append(f"{str(value)} = :{str(value)}")
        set_parts = ",".join(set_parts)

        # update tweet in database
        db.execute(f"""
            UPDATE tweets
            SET {set_parts}
            WHERE tweet_id = :tweet_id
            """, updated_tweet_data)
        db.commit()

        response.status = 200
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/home")

    finally:
        if db != None: db.close()
        if redirectPath: return redirect(redirectPath)
