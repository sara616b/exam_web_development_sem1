from bottle import redirect, response, request, post
import re
import jwt
import sqlite3

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY


@post("/login")
def _():
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in

        db = None
        redirectPath = None
        try:
            ##### email
            email = request.forms.get("login_email")
            if not email:
                response.status = 204
                redirectPath = "/login?error=email-missing"
                return
            if not re.match(REGEX_EMAIL, email):
                response.status = 400
                redirectPath = "/login?error=email-invalid"
                return

            ##### password
            if not request.forms.get("login_password"):
                response.status = 204
                redirectPath = f"/login?error=password-missing&email={email}"
                return
            if len(request.forms.get("login_password")) < 3:
                response.status = 400
                redirectPath = f"/login?error=password-short&email={email}"
                return

            # if email and password match a user's,
            # log in,
            # set session,
            # set cookie,
            # and redirect to dashboard

            ##### connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")

            ##### user_id for who's logged in
            user_id = db.execute("""
                SELECT user_id
                FROM users
                WHERE user_email IS :user_email AND user_password IS :user_password
                """, (email, request.forms.get("login_password"))).fetchone()
            if not user_id or len(user_id) != 1:
                redirectPath = (f"/login?error=no-match&email={email}")
                return
            user_id = user_id[0]

            ##### encode session and set it in database and cookie
            session_id = jwt.encode({"user_id":user_id}, JWT_KEY, algorithm="HS256")
            db.execute("""
                UPDATE users
                SET user_current_session = :session_id
                WHERE user_id = :user_id
                """, (session_id, user_id))
            db.commit()
            response.set_cookie("jwt", session_id, secret="secret")
            
            return

        except Exception as ex:
            print(ex)
            response.status = 500
            return

        finally:
            if db != None:
                db.close()
            ##### redirect with query string (errors and email)
            return redirect(redirectPath)

    else:
        ##### if the user is logged in redirect to home feed
        return redirect("/home")
        