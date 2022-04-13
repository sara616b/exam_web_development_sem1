from bottle import redirect, request, response, post, delete
import uuid
import os
import jwt
import time
import sqlite3
import imghdr

from settings import get_file_path, delete_retweet, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@delete("/retweets/delete/<retweet_id>")
def _(retweet_id):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)

    try:
        counter = delete_retweet(retweet_id)
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/home")
