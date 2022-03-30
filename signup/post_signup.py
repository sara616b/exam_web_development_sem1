from bottle import redirect, request, response, post
import re
import uuid
import time
import sqlite3

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

        # check if username or email is already in use
        if users_in_database:
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

        ##### send signup email
        # sender_email = "sarahwebdev2022@gmail.com"
        # receiver_email = new_user["user_email"]
        # password = "webdev2022"
        sender_email = "sarahwebdev2022@gmail.com"
        receiver_email = new_user["user_email"]
        # password = "webdev2022"
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

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            try:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
                return "yes, email sent"
            except Exception as ex:
                print(ex)
                return "uppps... could not send the email"

        # sender_email = "sarahwebdev2022@gmail.com"
        # receiver_email = "sarahwebdev2022@gmail.com"
        # password = gmail_password

        # message = MIMEMultipart("alternative")
        # message["Subject"] = "My Email From Python"
        # message["From"] = sender_email
        # message["To"] = receiver_email

        # # Create the plain-text and HTML version of your message
        # text = """\
        # Hi,
        # Thank you.
        # """

        # html = """\
        # <html>
        #     <body>
        #     <p>
        #         Hi,<br>
        #         <b style="color: blue">How are you?</b><br>
        #     </p>
        #     </body>
        # </html>
        # """

        # # Turn these into plain/html MIMEText objects
        # part1 = MIMEText(text, "plain")
        # part2 = MIMEText(html, "html")

        # # Add HTML/plain-text parts to MIMEMultipart message
        # # The email client will try to render the last part first
        # message.attach(part1)
        # message.attach(part2)

        # # Create secure connection with server and send email
        # context = ssl.create_default_context()
        # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        #     try:
            #     server.login(sender_email, password)
            #     server.sendmail(sender_email, receiver_email, message.as_string())
            #     return "yes, email sent"
        #     except Exception as ex:
            #     print("ex")
            #     return "uppps... could not send the email"


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
