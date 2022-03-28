from bottle import delete, redirect, post, request, response
import sqlite3
import os

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@delete("/tweets/delete/<tweet_id>")
def _(tweet_id):
    db = None
    try:
        if not check_if_logged_in():
            return redirect("/login")

        # connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        # find image and delete it from the folder if it exists
        tweet_image = db.execute("""
            SELECT tweet_image
            FROM tweets
            WHERE tweet_id = :tweet_id
            """, (tweet_id,)).fetchone()[0]
        if tweet_image:
            if os.path.exists(f"{get_file_path()}/static/images/tweets/{tweet_image}"):
                os.remove(f"{get_file_path()}/static/images/tweets/{tweet_image}")

        # delete tweet from database
        db.execute("DELETE FROM tweets WHERE tweet_id = :tweet_id", (tweet_id,))
        db.commit()
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/")
    finally:
        if db != None:
            db.close()
        return redirect("/home")
