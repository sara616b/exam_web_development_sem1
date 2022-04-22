from bottle import redirect, request, put, response
import time
import sqlite3
import os
import jwt
from common import get_file_path, validate_tweet_text, check_the_image, confirm_user_is_logged_in, is_uuid, JWT_KEY

@put("/tweets/<tweet_id>")
def _(tweet_id):
        
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    db = None
    redirect_path = None
    try:
        ##### check whether the id is a uuid4
        if is_uuid(tweet_id) == False:
            redirect_path = "/home?alert-info=Trying to edit the tweet failed. Please try again."
            return
        
        ##### user id of logged in user
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        
        ##### tweet id stays the same
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
            redirect_path = "/home?alert-info=Tweet doesn't exsist or isn't yours."
            return

        ##### tweet text - get + if found, validate and add to update values
        tweet_text = request.forms.get("tweet_text")
        tweet_text, redirect_error_path = validate_tweet_text(tweet_text, tweet_id)
        if redirect_error_path != None:
            redirect_path = redirect_error_path
            return
        
        if tweet_text:
            updated_tweet_data["tweet_text"] = tweet_text

        ##### image - remove, add new
        current_image = db.execute(f"""
            SELECT tweet_image
            FROM tweets
            WHERE tweet_id == :tweet_id
            """, (tweet_id,)).fetchone()[0]

        new_image_name = None
        image_name = request.forms.get("image_name")

        ##### if there's no image or the image name isn't the same as the current image name, delete current image
        if not image_name or current_image != image_name:
            if os.path.exists(f"{get_file_path()}/static/images/tweets/{current_image}"):
                os.remove(f"{get_file_path()}/static/images/tweets/{current_image}")
            updated_tweet_data["tweet_image"] = None
            
            ##### check if there's an image in request.files and if so, validate it 
            redirect_image_error, new_image_name = check_the_image(request.files.get("tweet_image"), "tweets")
            if redirect_image_error:
                redirect_path = f"/tweets/{tweet_id}{redirect_image_error}&text={tweet_text}"
                return

            ##### set new image name
            if new_image_name:
                updated_tweet_data["tweet_image"] = new_image_name

        ##### set updated at time
        updated_tweet_data["tweet_updated_at"] = time.time()

        ##### create string for all values that need to be set in the database query
        set_parts = []
        for value in updated_tweet_data:
            if str(value) != "tweet_id":
                set_parts.append(f"{str(value)} = :{str(value)}")
        set_parts = ",".join(set_parts)

        ##### update tweet in database
        counter = db.execute(f"""
            UPDATE tweets
            SET {set_parts}
            WHERE tweet_id = :tweet_id
            """, updated_tweet_data).rowcount
        
        ##### check that 1 and only 1 tweet was updated
        if counter != 1:
            redirect_path = "/home?alert-info=Editing tweet failed. Please try again."
            return

        db.commit()

        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return redirect("/home")

    finally:
        if db != None:
            db.close()
        if redirect_path != None: 
            return redirect(redirect_path)
