from bottle import redirect, response, request, put
import re
import jwt
import sqlite3
from common import get_file_path, confirm_user_is_logged_in, REGEX_EMAIL, JWT_KEY

@put("/login")
def _():
    ##### if user is logged in redirect to home
    if confirm_user_is_logged_in():
        return redirect("/home", code=303)

    db = None
    redirect_path = None
    try:
        ##### email
        email = request.forms.get("login_email")
        if not email:
            redirect_path = "/login?error=email-missing"
            return
        if not re.match(REGEX_EMAIL, email):
            redirect_path = "/login?error=email-invalid"
            return

        ##### password
        if not request.forms.get("login_password"):
            redirect_path = f"/login?error=password-missing&email={email}"
            return
        if len(request.forms.get("login_password")) < 3:
            redirect_path = f"/login?error=password-short&email={email}"
            return

        ##### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ##### check if email and password match a user's in the database
        user_id = db.execute("""
            SELECT user_id
            FROM users
            WHERE user_email IS :user_email AND user_password IS :user_password
            """, (email, request.forms.get("login_password"))).fetchone()

        ##### if no users and password matched input, redirect
        if not user_id:
            redirect_path = (f"/login?error=no-match&email={email}")
            return
        else:
            user_id = user_id[0]

        ##### encode session
        session_id = jwt.encode({"user_id":user_id}, JWT_KEY, algorithm="HS256")

        ##### set session in database
        db.execute("""
            UPDATE users
            SET user_current_session = :session_id
            WHERE user_id = :user_id
            """, (session_id, user_id))
        db.commit()

        ##### set session in cookie
        response.set_cookie("jwt", session_id, secret="secret")
        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        redirect_path = "/login?alert-info=Sorry, an error occured. Please try again."
        return

    finally:
        if db != None:
            db.close()

        ##### redirect with query string (errors and email)
        if redirect_path != None:
            return redirect(redirect_path)
