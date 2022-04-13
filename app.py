from bottle import default_app, get, static_file, redirect, run, view, error
import sqlite3
from settings import get_file_path, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

# STYLESHEET #########################
@get("/static/style/style.css")
def style():
    return static_file("/static/style/style.css", root=".")

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
from index import index_view
from signup import signup_view, signup
from login import login_view, login, logout
from home import home_view
from tweets import post_tweet, edit_tweet, delete_tweet, tweet_modal, like_tweet, dislike_tweet, retweet_tweet, delete_retweet
from users import user_view, follow_user, unfollow_user, all_users_view
from admin import admin_view, admin_delete_tweet



##############################
@error(404)
def _(error):
  return f"Sorry, an error occured: {error}"
##############################
@error(500)
def _(error):
  return f"Sorry, an error occured: {error}"
##############################
@error(400)
def _(error):
  return f"Sorry, an error occured: {error}"

# SERVER #############################
try:
  # Production
  import production
  application = default_app()
except:
  # Development
  run(host='127.0.0.1', port=3333, server="paste", reloader=True, debug=True)
