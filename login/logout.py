from bottle import delete, put, get, post, response, request, redirect
import sqlite3

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@put("/logout")
def _():
    try:
        # get cookie
        session_id = request.get_cookie("jwt", secret="secret")
        # remove cookie by making it expire 
        response.set_cookie("jwt", "", secret="secret", expires=0)

        # connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        # delete session from database
        db.execute("""
            UPDATE users
            SET user_current_session = :none
            WHERE user_current_session = :session_id
            """, (None, str(session_id),))
        db.commit()

        return
    
    except Exception as ex:
        print(ex)
        response.status = 500
    
    finally:
        if db != None:
            db.close()
