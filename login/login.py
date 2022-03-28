from bottle import redirect, response, request, post
import re
import jwt
import sqlite3

from settings import *


@post("/login")
def _():
    db = None
    redirectPath = "/"
    try:
        # email
        login_email = request.forms.get("login_email")
        if not login_email:
            redirectPath = "/login?error=user_email"
            return
        
        # password
        if not request.forms.get("login_password"):
            redirectPath = f"/login?error=user_password&user_email={login_email}"
            return
        
        # if email and password match a user's, log in, set session, set cookie and redirect to dashboard
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        user_id = db.execute("""
            SELECT user_id
            FROM users
            WHERE user_email IS :user_email AND user_password IS :user_password
            """, (login_email, request.forms.get("login_password"))).fetchone()

        if not user_id or len(user_id) != 1:
            redirectPath = ("/login?error=error")
            return

        user_id = user_id[0]

        session_id = jwt.encode({"user_id":user_id}, JWT_KEY, algorithm="HS256")
        
        db.execute("""
            UPDATE users
            SET user_current_session = :session_id
            WHERE user_id = :user_id
            """, (session_id, user_id))

        db.commit()

        # set is_active as true maybe?
        response.set_cookie("jwt", session_id, secret="secret")

        # if successful redirect to frontpage
        redirectPath = "/home"
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        redirectPath = "/"

    finally:
        if db != None:
            db.close()
        if redirectPath != None:
            return redirect(redirectPath)
