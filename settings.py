from bottle import request, response
import jwt
from jwt.exceptions import InvalidSignatureError
import sqlite3
import uuid
import time
import datetime

JWT_KEY = f"{str(uuid.uuid4())}-{str(uuid.uuid4())}-{str(uuid.uuid4())}"
REGEX_EMAIL = '^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'

def check_if_logged_in():
    try:
        is_logged_in = False
        # if the jwt cookie is in SESSIONS and is valid
        # set is_logged_in to value from user_information (True)
        # else print error
        db = sqlite3.connect("database/database.sqlite")


        # TODO - Instead have the session unique for each user
        jwt_cookie = request.get_cookie("jwt", secret="secret")
        jwt_is_in_sessions = str(db.execute("""
                SELECT session_id
                FROM sessions
                WHERE session_id IS :session_id
                """, (str(jwt_cookie),)).fetchone())
        if jwt_is_in_sessions[0]:
            jwt_is_in_sessions = True

        if jwt_cookie and jwt_is_in_sessions:
            try:
                session_id = jwt.decode(
                        jwt_cookie,
                        JWT_KEY, algorithms=["HS256"]
                    ) or None
                if session_id is not None:
                    is_logged_in = True

            except InvalidSignatureError as error:
                print(f"Invalid signature error: {error}")

        return is_logged_in

    except Exception as ex:
        print(ex)
        response.status = 500
        return {"info": f"Error when checking login: {ex}"}

    finally:
        db.close()

def date_text_from_epoch(epoch):
    return datetime.datetime.fromtimestamp(int(epoch.split('.')[0])).strftime('%d/%m/%Y %H:%M')

def get_file_path():
    try:
      import production
      return "/home/buzzer/site"
    except:
      return "."
    