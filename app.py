from bottle import default_app, get, static_file, redirect, run, view
import sqlite3
from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

# STYLESHEET #########################
@get("/static/style.css")
def style():
    return static_file("/static/style.css", root=".")

# SCRIPTS ############################
@get("/static/js/script.js")
def script():
    return static_file("/static/js/script.js", root=".")
@get("/static/js/spa.js")
def spa():
    return static_file("/static/js/spa.js", root=".")
@get("/static/js/validator.js")
def validate():
    return static_file("/static/js/validator.js", root=".")

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
from tweets import post_tweet, edit_tweet, delete_tweet, tweet_modal, like_tweet, dislike_tweet
from user_profile import get_profile, follow_user, unfollow_user, get_all_user
from administrator import administrator_view, admin_delete_tweet

# SERVER #############################
try:
  # Production
  import production
  application = default_app()
except:
  # Development
  run(host='127.0.0.1', port=3333, server="paste", reloader=True, debug=True)