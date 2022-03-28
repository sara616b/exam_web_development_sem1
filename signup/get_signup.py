from bottle import default_app, get, static_file, redirect, run, view
import sqlite3
from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

##############################
@get("/signup")
@view("signup.html")
def _():
    try:
      return 

    except Exception as ex:
      print(ex)
      return {"error":ex}
    