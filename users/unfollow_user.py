from bottle import redirect, request, response, delete
import jwt
import sqlite3

from common import get_file_path, confirm_user_is_logged_in, is_uuid, JWT_KEY

@delete("/users/follow/<user_id_to_follow>")
def _(user_id_to_follow):
    ##### the user needs to be logged in to unfollow another user
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    db = None
    redirect_path = None
    try:
        ##### check whether the id is a uuid4
        if is_uuid(user_id_to_follow) == False:
            redirect_path = "/home?alert-info=Trying to unfollow the user failed. Please try again."
            return

        ##### decode jwt cookie to get user id
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if not user_id or is_uuid(user_id) == False:
            redirect_path = "/home?alert-info=Trying to unfollow the user failed. Please try again."
            return

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        if not db: 
            redirect_path = "/home?alert-info=Trying to unfollow the user failed. Please try again."
            return

        ##### delete follow row from database
        counter = db.execute("""
            DELETE FROM followers
            WHERE fk_user_id_follower = :tweet_id
            AND fk_user_id_to_follow = :user_id
            """, (str(user_id), str(user_id_to_follow))).rowcount

        ##### if no row or more than one row was affected, return error
        if counter != 1:
            redirect_path = "/home?alert-info=Trying to unfollow the user failed. Please try again."
            return

        db.commit()
        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        redirect_path = "/home?alert-info=Trying to unfollow the user failed. Please try again."
        return

    finally:
        if db != None:
            db.close()
        if redirect_path != None:
            redirect(redirect_path)
