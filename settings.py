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
        db = sqlite3.connect("database/database.db")

        # TODO - Instead have the session unique for each user
        jwt_cookie = request.get_cookie("jwt", secret="secret")
        session_matches_user = str(db.execute("""
                SELECT user_current_session, user_id
                FROM users
                WHERE user_current_session = :user_current_session
                """, (str(jwt_cookie),)).fetchone())
        if session_matches_user[0]:
            session_matches_user = True

        if jwt_cookie and session_matches_user:
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

def time_since_from_epoch(epoch):
    time_since_seconds = int(time.time()) - int(epoch.split('.')[0])
    if time_since_seconds < 60:
        return f"{str(time_since_seconds).split('.')[0]}s"
    
    time_since_minutes = time_since_seconds / 60
    if time_since_minutes < 60:
        return f"{str(time_since_minutes).split('.')[0]}m"
    
    time_since_hours = time_since_minutes / 60
    if time_since_hours < 60:
        return f"{str(time_since_hours).split('.')[0]}h"

    time_since_days = time_since_hours / 24
    if time_since_days < 7:
        return f"{str(time_since_days).split('.')[0]}d"
    
    time_since = f"{str(datetime.datetime.fromtimestamp(time_since_seconds.strftime('%B %d'))).split('.')[0]}"
    return time_since

def date_text_from_epoch(epoch):
    return datetime.datetime.fromtimestamp(int(epoch.split('.')[0])).strftime('%d/%m/%Y %H:%M')

def get_file_path():
    try:
      import production
      return "/home/buzzer/site"
    except:
      return "."
    