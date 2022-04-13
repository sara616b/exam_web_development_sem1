from bottle import delete, redirect, post, request, response
import sqlite3
import os

from settings import delete_tweet, get_file_path, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@delete("/tweets/delete/<tweet_id>")
def _(tweet_id):
    
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)
        
    try:
        counter = delete_tweet(tweet_id)
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/login")
