from bottle import get, redirect, request, view, response
import sqlite3

from settings import get_file_path, check_if_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@get("/tweets")
@get("/tweets/<tweet_id>")
@view("tweet_modal.html")
def _(tweet_id):
    db = None
    try:
        if tweet_id == "new":
            return dict(tweet_id = tweet_id)

        if not check_if_logged_in():
            return redirect("/login") 
        
        tweet_to_edit = {}
        error = request.params.get("error")
        
        # connect to database
        db = sqlite3.connect("database/database.db")

        # get tweet info from database
        tweet = db.execute("""
            SELECT tweet_text, tweet_image
            FROM tweets
            WHERE tweet_id = :tweet_id
        """,(tweet_id,)).fetchone()

        # if tweet is found, set info that's needed to display the editing inputs
        if tweet:
            tweet_to_edit = {
                "tweet_id": tweet_id,
                "tweet_text": tweet[0],
                "tweet_image": tweet[1]
            }
        
        # redirect if tweet doesn't exist
        if not tweet:
            return redirect("/home")

        return dict(tweet_id=tweet_id, tweet=tweet_to_edit)
        # return dict(is_logged_in=check_if_logged_in(), tweet=tweet_to_edit, error=error)

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/")
    finally:
        if db != None:
            db.close()