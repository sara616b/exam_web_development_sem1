from bottle import put, response, request, redirect
import sqlite3
from common import get_file_path, confirm_user_is_logged_in

@put("/logout")
def _():
    ##### if user isn't logged in redirect to login
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    db = None
    try:
        ##### get session from cookie
        session_id = request.get_cookie("jwt", secret="secret")

        ##### remove cookie by making it expire
        response.set_cookie("jwt", "", secret="secret", expires=0)

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ##### set session to None in the user's row in the database
        db.execute("""
            UPDATE users
            SET user_current_session = :none
            WHERE user_current_session = :session_id
            """, (None, str(session_id),))
        db.commit()

        return
    
    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return {"error": str(ex)}

    finally:
        if db != None:
            db.close()
