from bottle import redirect, request, response, post, delete
import uuid
import os
import jwt
import time
import sqlite3
import imghdr

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@delete("/users/follow/<user_id_to_follow>")
def _(user_id_to_follow):
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
            user_id = None
                # decode jwt cookie to get user id for new tweet
            user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
            
            # connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")

            # delete follow from database
            db.execute("""
                DELETE FROM followers
                WHERE fk_user_id_follower = :tweet_id
                AND fk_user_id_to_follow = :user_id
                """, (str(user_id), str(user_id_to_follow)))
            db.commit()

            return

        except Exception as ex:
            print(ex)
            response.status = 500
            return redirect("/home")

        finally:
            if db != None:
                db.close()
            # return redirect(redirectPath)