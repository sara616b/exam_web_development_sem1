from bottle import redirect, request, response, post
import uuid
import os
import jwt
import time
import sqlite3
import imghdr

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@post("/tweets/new")
def _():
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        return redirect("/login")
    else:
        db = None
        redirectPath = "/home"
        try:
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
            
            # text
            new_tweet_text = request.forms.get("tweet_text")
            if not new_tweet_text:
                # cant post empty tweets
                response.status = 204
                redirectPath = "/tweets/new?error=empty"
                return
            if len(new_tweet_text) < 2:
                response.status = 400
                redirectPath = f"/tweets/new?error=short&text={new_tweet_text}"
                return
            if len(new_tweet_text) > 250:
                response.status = 400
                redirectPath = f"/tweets/new?error=long&text={new_tweet_text}"
                return
            new_tweet_text = new_tweet_text.replace("\n", "<br />")

            # image 
            image = request.files.get("tweet_image")
            image_name = None
            if image:
                # get extention and validate
                file_name, file_extension = os.path.splitext(image.filename)
                if file_extension.lower() == ".jpg": file_extension = ".jpeg"
                if file_extension.lower() not in (".png", ".jpg", ".jpeg"):
                    # redirectPath = f"/tweets/new?error=image-not-allowed&text={new_tweet_text}"
                    return

                # image name
                image_name = f"{str(uuid.uuid4())}{file_extension}"

                # save image
                image.save(f"{get_file_path()}/static/images/tweets/{image_name}")

                # is the image valid
                imghdr_extension = imghdr.what(f"{get_file_path()}/static/images/tweets/{image_name}")
                if file_extension != f".{imghdr_extension}":
                    # delete the invalid image 
                    os.remove(f"{get_file_path()}/static/images/tweets/{image_name}")
                    # redirectPath = f"/tweets/new?error=image-not-allowed&text={new_tweet_text}"
                    return

            # connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")
            
            # append new tweet with values
            new_tweet = {
                "tweet_id": str(uuid.uuid4()),
                "tweet_text": new_tweet_text,
                "tweet_created_at": str(time.time()),
                "tweet_updated_at": None,
                "tweet_image": image_name if image_name else None,
                "tweet_user_id": user_id,
            }

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

            return redirect("/home")

        except Exception as ex:
            print(ex)
            response.status = 500
            return redirect("/home")

        finally:
            if db != None:
                db.close()
            return redirect(redirectPath)