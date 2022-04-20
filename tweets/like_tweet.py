from bottle import redirect, request, response, post
import jwt
import sqlite3
from common import get_file_path, confirm_user_is_logged_in, is_uuid, JWT_KEY

@post("/tweets/like/<tweet_id>")
def _(tweet_id):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    db = None
    redirect_path = None
    try:
        ##### check whether the id is a uuid4
        if is_uuid(tweet_id) == False:
            redirect_path = "/home?alert-info=Trying to like the tweet failed. Please try again."
            return

        ##### decode jwt cookie to get user id
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

        # connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        # insert new tweet to database
        counter = db.execute("""
            INSERT INTO likes
            VALUES(
                :user_id,
                :tweet_id)
            """, (str(user_id), str(tweet_id))).rowcount
        
        ##### check that 1 and only 1 like was inserted
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