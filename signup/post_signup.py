from bottle import redirect, request, response, post
import re
import uuid
import time
import sqlite3

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@post("/signup")
def _():
    db = None
    redirectPath = "/"
    try:
        # get the info from the form and validate
        errors = []
        form_inputs = {}

        # display name
        signup_display_name = request.forms.get("signup_display_name")
        if not signup_display_name:
            errors.append("display-name-missing")
        elif len(signup_display_name) < 1 or len(signup_display_name) > 100:
            errors.append("display-name-length")
        if signup_display_name:
            form_inputs["display-name"] = signup_display_name
     
        # username
        signup_username = request.forms.get("signup_username")
        if not signup_username:
            errors.append("username-missing")
        else:
            form_inputs["username"] = signup_username
   
        # email
        signup_email = request.forms.get("signup_email")
        if not signup_email:
            errors.append("email-missing")
        elif not re.match(REGEX_EMAIL, signup_email):
            errors.append("email-invalid")
        if not signup_email == '':
            form_inputs["email"] = signup_email

        # password
        signup_password = request.forms.get("signup_password")
        if not signup_password:
            errors.append("password-missing")
        elif len(signup_password) < 3:
            errors.append("password-short")
        elif signup_password != request.forms.get("signup_password_repeat"):
            errors.append("passwords-different")

        db = sqlite3.connect(f"{get_file_path()}/database/database.db")
        users_in_database = db.execute("""
            SELECT user_username, user_email
            FROM users
            WHERE user_username = :new_user_username OR user_email = :user_email
        """, (signup_username, signup_email)).fetchall()
        print(users_in_database)

        # check if username or email is already in use
        for user in users_in_database:
            if user[0] == signup_username and signup_username:
                errors.append("user-exists-username")
            if user[1] == signup_email and signup_email:
                errors.append("user-exists-email")

        # potential error messages
        if not errors == []:
            error_string = f'{"=error&".join(errors)}=error'
            form_input_string = ''
            for value in form_inputs:
                form_input_string += f"&{value}={form_inputs[value]}"
            redirectPath = f"/signup?{error_string}{form_input_string}"
            return

        # new user details
        new_user = {
            "user_id": str(uuid.uuid4()),
            "user_display_name": signup_display_name,
            "user_username": signup_username,
            "user_email": signup_email,
            "user_password": signup_password,
            "user_created_at": time.time(),
            "user_current_session": None,
        }
        
        # insert to database
        db.execute("""
            INSERT INTO users
            VALUES(:user_id, :user_display_name, :user_username, :user_email, :user_password, :user_created_at, :user_current_session
            """, new_user)
        db.commit()
        redirectPath = "/login"
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
