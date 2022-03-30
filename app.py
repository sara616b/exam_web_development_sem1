from bottle import default_app, get, static_file, redirect, run, view
import sqlite3
from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

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
def profile_default():
    return static_file("/static/images/profile/default.svg", root=".")
@get("/static/images/tweets/<filename>")
def image(filename):
    return static_file(f"/static/images/tweets/{filename}", root=".")

# IMPORT MODULES #####################
from index import get_index
from signup import get_signup, post_signup
from login import login_view, login, logout
from home import get_home
from tweets import post_tweet, edit_tweet, delete_tweet, form_for_tweet
from user_profile import get_profile

# SERVER #############################
try:
  # Production
  import production
  application = default_app()
except:
  # Development
  run(host='127.0.0.1', port=3333, server="paste", reloader=True, debug=True)