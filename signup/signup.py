from bottle import redirect, request, response, post
import re
import uuid
import time
import sqlite3
import jwt

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@post("/signup")
def _():
    try:
        check_if_logged_in()
    except:
        # if check_if_logged_in raises an exception
        # the user isn't logged in
        db = None
        redirectPath = "/"
        try:
            errors = []
            form_inputs = {}

            ##### display name
            display_name = request.forms.get("signup_display_name")
            if not display_name:
                errors.append("display-name-missing")
            elif len(display_name) < 1 or len(display_name) > 100:
                errors.append("display-name-length")
            if display_name:
                form_inputs["display-name"] = display_name
        
            ##### username
            username = request.forms.get("signup_username")
            username.replace(" ", "")
            if not username:
                errors.append("username-missing")
            elif len(display_name) < 1 or len(display_name) > 100:
                errors.append("username-length")
            if username:
                form_inputs["username"] = username
    
            ##### email
            email = request.forms.get("signup_email")
            if not email:
                errors.append("email-missing")
            elif not re.match(REGEX_EMAIL, email):
                errors.append("email-invalid")
            if email:
                form_inputs["email"] = email

            ##### password
            if not request.forms.get("signup_password"):
                errors.append("password-missing")
            elif len(request.forms.get("signup_password")) < 3:
                errors.append("password-short")
            elif request.forms.get("signup_password") != request.forms.get("signup_password_repeat"):
                errors.append("passwords-different")

            ##### connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")

            ##### select users that matches input
            users_in_database = db.execute("""
                SELECT user_username, user_email
                FROM users
                WHERE user_username = :new_user_username OR user_email = :user_email
            """, (username, email)).fetchall()

            ##### if any users were found, check whether username or email is already in use
            if users_in_database:
                for user in users_in_database:
                    if username and user[0] == username:
                        errors.append("user-exists-username")
                    if email and user[1] == email:
                        errors.append("user-exists-email")

            ##### potential error messages
            if errors != []:
                ##### build query string with errors
                error_string = f'{"=error&".join(errors)}=error'

                ##### add form inputs to query string
                form_input_string = ''
                for value in form_inputs:
                    form_input_string += f"&{value}={form_inputs[value]}"
                redirectPath = f"/signup?{error_string}{form_input_string}"

                ##### return if errors were found
                return

            ##### new user details dictionary
            new_user = {
                "user_id": str(uuid.uuid4()),
                "user_display_name": display_name,
                "user_username": username,
                "user_email": email,
                "user_password": request.forms.get("signup_password"),
                "user_created_at": time.time(),
                "user_current_session": None,
            }
            
            ##### insert user into database
            db.execute("""
                INSERT INTO users
                VALUES(
                    :user_id,
                    :user_display_name,
                    :user_username,
                    :user_email,
                    :user_password,
                    :user_created_at,
                    :user_current_session)
                """, new_user)
            db.commit()

            ##### log in the user
            ##### encode session and set it in database and cookie
            session_id = jwt.encode({"user_id":new_user["user_id"]}, JWT_KEY, algorithm="HS256")
            db.execute("""
                UPDATE users
                SET user_current_session = :session_id
                WHERE user_id = :user_id
                """, (session_id, new_user["user_id"]))
            db.commit()
            response.set_cookie("jwt", session_id, secret="secret")

            ##### send signup email
            sender_email = "sarahwebdev2022@gmail.com"
            receiver_email = new_user["user_email"]
            password = "kcyacprpwsnpalak"

            message = MIMEMultipart("alternative")
            message["Subject"] = "Thank you for signing up to Buzzer!"
            message["From"] = sender_email
            message["To"] = receiver_email

            ##### text and HTML message
            text = MIMEText(f"Hi {new_user['user_username']}! Thanks for signing up to Buzzer.", "plain")
            html = MIMEText(f"""\
                <html>
                    <body>
                    <p>
                        Hi {new_user['user_username']},<br>
                        Thank you for signing up to Buzzer.<br>
                    </p>
                    </body>
                </html>
                """, "html")

            message.attach(text)
            message.attach(html)

            ##### create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                try:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                    return
                except Exception as ex:
                    print(ex)
                    return
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

    else:
        ##### if the user is logged in redirect to home feed
        return redirect("/home")
