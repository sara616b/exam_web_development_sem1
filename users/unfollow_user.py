from bottle import redirect, request, response, post, delete
import jwt
import sqlite3

from settings import get_file_path, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@delete("/users/follow/<user_id_to_follow>")
def _(user_id_to_follow):
    ##### the user needs to be logged in to unfollow another user
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    db = None
    try:
        ##### decode jwt cookie to get user id
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if not user_id: 
            response.status = 204
            return

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        if not db: 
            response.status = 204
            return

        ##### delete follow row from database
        rows_deleted = db.execute("""
            DELETE FROM followers
            WHERE fk_user_id_follower = :tweet_id
            AND fk_user_id_to_follow = :user_id
            """, (str(user_id), str(user_id_to_follow))).rowcount
        db.commit()

        if rows_deleted > 0:
            ##### success
            response.status = 200
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/home")

    finally:
        if db: db.close()
