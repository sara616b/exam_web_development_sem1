from bottle import get, redirect, request, view, template, response
import sqlite3
import jwt

from settings import get_file_path, get_all_posts, only_update_body, get_all_tweets, get_all_users, confirm_user_is_logged_in, time_since_from_epoch, date_text_from_epoch, REGEX_EMAIL, JWT_KEY

@get("/tweets/<tweet_id>")
@view("home.html")
def _(tweet_id):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login", code=303)
    
    db = None
    redirectPath = None
    try:
        ##### get errors from query string
        error = request.params.get("error")
        possible_errors = [
            {
                "error": "empty",
                "message": "Tweet must contain text",
            },
            {
                "error": "short",
                "message": "Tweet must be 2 or more characters long",
            },
            {
                "error": "long",
                "message": "Tweet can only be 250 characters long",
            },
            {
                "error": "image-not-allowed",
                "message": "Image must be a .png or .jpeg (.jpg)"
            }
        ]

        ##### get tweet text from params to set as value in input 
            ##### get tweet text from params to set as value in input 
        ##### get tweet text from params to set as value in input 
        tweet_text = request.params.get("text")

        ###### connect to database
        db = sqlite3.connect(f"{get_file_path()}/database/database.db")

        ##### get user id
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]

        ##### get all users data and all tweets data
        users = get_all_users(user_id)
        tweets = get_all_tweets(user_id)
        posts = get_all_posts(user_id)

        if tweet_id == "new":
            return dict(
                user_id=user_id,
                users=users,
                tweets=tweets,
                posts=posts,
                tweet_id=tweet_id,
                url="/tweets/" + tweet_id,
                title="New tweet",
                modal='tweet',
                tweet=None,
                only_update_body=only_update_body(),
                error=error,
                tweet_text=tweet_text,
                possible_errors=possible_errors,
                )
        
        elif tweet_id != 'new':
            ##### check that the tweet belongs to the user logged in
            tweet_and_user_id_match = len(db.execute(f"""
                SELECT *
                FROM tweets
                WHERE tweet_id == :tweet_id AND tweet_user_id == :user_id
                """, (tweet_id, user_id)).fetchall())
            if tweet_and_user_id_match != 1:
                # redirectPath = "/home?error=notyourtweet"
                redirectPath = "/home"
                return
            tweet_to_edit = {}
            
            # get tweet info from database
            tweet = db.execute("""
                SELECT tweet_text, tweet_image
                FROM tweets
                WHERE tweet_id = :tweet_id
                """,(tweet_id,)).fetchone()

            ##### redirect if tweet doesn't exist
            if not tweet:
                redirectPath = "/home"
                return

            # if tweet is found, set info that's needed to display the editing inputs
            tweet_to_edit = {
                "tweet_id": tweet_id,
                "tweet_text": tweet[0],
                "tweet_image": tweet[1]
            }

            return dict(
                user_id=user_id,
                users=users,
                tweets=tweets,
                tweet_id=tweet_id,
                posts=posts,
                tweet=tweet_to_edit,
                url="/tweets/" + tweet_id,
                title="Edit tweet",
                modal='tweet',
                only_update_body=only_update_body(),
                error=error,
                tweet_text=tweet_text,
                possible_errors=possible_errors,
                )
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/home")

    finally:
        if db != None:
            db.close()
        if redirectPath: redirect(redirectPath)