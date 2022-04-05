from bottle import redirect, request, put, post, response
import time
import sqlite3
import os
import imghdr
import uuid
import jwt

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@put("/tweets/<tweet_id>")
def _(tweet_id):
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        return redirect("/login")
    else:
        db = None
        redirectPath = "/"

        try:
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
            
            updated_tweet_data = {"tweet_id":tweet_id}

            # connect database
            db = sqlite3.connect("database/database.db")

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
            if not tweet_text:
                # text is required in tweets
                redirectPath = f"/tweets/edit/{tweet_id}?error=empty"
                return
            if len(request.forms.get("tweet_text")) > 250:
                redirectPath = f"/tweets/edit/{tweet_id}?error=long"
                return
            if tweet_text:
                updated_tweet_data["tweet_text"] = tweet_text
            
            current_image = db.execute(f"""
                SELECT tweet_image
                FROM tweets
                WHERE tweet_id == :tweet_id
                """, (tweet_id,)).fetchone()[0]

            # image - remove, add new
            new_image_name = None
            image_name = request.forms.get("image_name")
            if not current_image or current_image != image_name:
                if os.path.exists(f"assets/images/{current_image}"):
                    os.remove(f"assets/images/{current_image}")
                updated_tweet_data["tweet_image"] = None

                new_image = request.files.get("tweet_image")
                if new_image:
                    # get extention and validate
                    file_name, file_extension = os.path.splitext(new_image.filename)
                    if file_extension.lower() == ".jpg": file_extension = ".jpeg"
                    if file_extension.lower() not in (".png", ".jpg", ".jpeg"):
                        # redirectPath = f"/tweets/edit/{tweet_id}?error=image-not-allowed"
                        return

                    # image name
                    new_image_name = f"{str(uuid.uuid4())}{file_extension}"

                    # save image
                    new_image.save(f"{get_file_path()}/static/images/tweets/{new_image_name}")
                    imghdr_extension = imghdr.what(f"{get_file_path()}/static/images/tweets/{new_image_name}")

                    # is the image valid
                    if file_extension != f".{imghdr_extension}":
                        # delete the invalid image 
                        os.remove(f"{get_file_path()}/static/images/tweets/{new_image_name}")
                        new_image_name = None
                        # redirectPath = f"/tweets/new?error=image-not-allowed"
                        return

                if new_image_name:
                    updated_tweet_data["tweet_image"] = new_image_name

            # set updated at time
            updated_tweet_data["tweet_updated_at"] = time.time()

            # create string for all that needs to be set in the database query
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

            return 

        except Exception as ex:
            print(ex)
            response.status = 500
            return redirect("/")

        finally:
            if db != None:
                db.close()
            return redirect("/home")
