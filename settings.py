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
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

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
    if time_since_hours < 24:
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


# from bottle import response
# import sqlite3
# import re

# _errors = {
#   "en_server_error":"server error",
#   "dk_server_error":"server fejl",
#   "sv_server_error":"serverfel",
#   "en_json_error":"invalid json",
#   "dk_json_error":"ugyldigt json",  
# }

# ##############################
# def _send(status = 400, error_message = "unknown error"):
#   response.status = status
#   return {"info":error_message}

# ##############################
# def _is_item_name(text=None, language="en"):
#   min, max = 2, 20
#   errors = {
#     "en":f"item_name {min} to {max} characters. No spaces", 
#     "dk":f"item_name {min} til {max} tegn. Uden mellemrum",
#     "sv":f"item_name {min} till {max} tegn. Inga mellanrum ",
#   }
#   if not text: return None, errors[language]
#   text = re.sub("[\n\t]*", "", text)
#   text = re.sub(" +", " ", text)
#   text = text.strip()
#   if len(text) < min or len(text) > max : return None, errors[language]
#   # if " " in text : return None, errors[language]
#   text = text.capitalize()
#   return text, None

# ##############################
# def _is_item_description(text=None, language="en"):
#   min, max = 10, 500
#   errors = {
#     "en":f"item_description {min} to {max} characters", 
#     "dk":f"item_description {min} til {max} tegn",
#     "sv":f"item_description {min} till {max} tegn",
#   }
#   if not text: return None, errors[language]
#   # text = re.sub("[\n\t]*", "", text)
#   # text = re.sub(" +", " ", text)
#   text = text.strip()
#   if len(text) < min or len(text) > max : return None, errors[language]
#   return text, None

# ##############################
# def _is_item_price(text=None, language="en"):
#   errors = {
#     "en":f"item_price must be a number with two decimals divided by a comma, and cannot start with zero", 
#     "dk":f"item_price skal være et tal med to decimaler divideret med et komma, og må ikke starte med nul",
#     "sv":f"item_price måste vara ett tal med två decimaler delat med ett kommatecken och får inte börja med noll"
#   }
#   if not text : return None, errors[language]
#   if not ',' in text:
#     text = f"{text},00"
#   if not re.match("^[1-9][0-9]*[,][0-9]{2}$", text) : return None, errors[language]
#   return text, None

# ##############################
# def _is_uuid4(text=None, language="en"):
#   errors = {
#     "en":f"item_id must be uuid4", 
#     "dk":f"item_id skal være uuid4",
#     "sv":f"item_id måste vara uuid4"
#   }
#   if not text: return None, errors[language]
#   regex_uuid4 = "^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
#   if not re.match(regex_uuid4, text) : return None, errors[language]
#   return text, None

# ##############################
# def create_json_from_sqlite_result(cursor, row):
#   d = {}
#   for idx, col in enumerate(cursor.description):
#     d[col[0]] = row[idx]
#   return d

# ##############################
# def _db_connect(db_name):
#   db = sqlite3.connect(db_name)
#   db.row_factory = create_json_from_sqlite_result
#   return db
