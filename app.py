from bottle import default_app, get, static_file, redirect, run, view
import sqlite3
from settings import *

# STYLESHEET #########################
@get("/static/style.css")
def style():
    return static_file("/static/style.css", root=".")
# SCRIPT #############################
@get("/static/script.js")
def script():
    return static_file("/static/script.js", root=".")
# IMAGES #############################
@get("/static/images/icon.svg")
def icon():
    return static_file("/static/images/icon.svg", root=".")
@get("/static/images/profile/default.svg")
def icon():
    return static_file("/static/images/profile/default.svg", root=".")
# @get("/static/image/icon.svg")
# def icon():
#     return static_file("/static/image/icon.svg", root=".")

# IMPORT MODULES #####################
from home import get_home

##############################
@get("/")
@view("index.html")
def _():
    try:
      db = sqlite3.connect(f"{get_file_path()}/database/database.db")
      # get tweet info from database
      user = db.execute("""
        SELECT *
        FROM users
        WHERE user_id = :user_id
        """,(1,)).fetchone()

      if user:
        user = {
          "user_id": user[0],
          "user_display_name": user[1],
          "user_username": user[2],
          "user_email": user[3],
        }
      return dict(user=user)

    except Exception as ex:
      print(ex)
      return {"error":ex}
    

##############################
@get("/signup")
@view("signup.html")
def _():
    try:
      return 

    except Exception as ex:
      print(ex)
      return {"error":ex}
    

##############################
@get("/login")
@view("login.html")
def _():
    try:
      return 

    except Exception as ex:
      print(ex)
      return {"error":ex}
    

# SERVER #############################
try:
  # Production
  import production
  application = default_app()
except:
  # Development
    run(host='127.0.0.1', port=3333, server="paste", reloader=True, debug=True)