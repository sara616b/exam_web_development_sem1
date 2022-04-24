from bottle import get, redirect, request, view, response
import sqlite3
import jwt
from common import get_file_path, get_all_posts, is_uuid, only_update_body, get_all_tweets, get_all_users, confirm_user_is_logged_in, JWT_KEY

@get("/tweets/<tweet_id>")
@view("tweet_modal.html")
def _(tweet_id):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    db = None
    redirect_path = None
    try:
        ##### get errors from query string
        error = request.params.get("error")
        possible_errors = {
            "text": [
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
        }

        ##### get tweet text from params to set as value in input 
        tweet_text = request.params.get("text")

        ##### get user id
        user_id = jwt.decode(request.get_cookie("jwt", secret="secret"), JWT_KEY, algorithms=["HS256"])["user_id"]
        if not user_id or is_uuid(user_id) == False:
            redirect_path = "/home?alert-info=Trying to open tweet modal failed. Please try again."
            return

        ##### get all users data and all tweets data
        users = get_all_users(user_id)
        tweets = get_all_tweets(user_id)
        posts = get_all_posts(user_id)

        if tweet_id == "new":
            return dict(
                user_id=user_id,                    # user_id of logged in user
                users=users,                        # all users to display 'who to follow' aside
                tweets=tweets,                      # all tweets
                posts=posts,                        # all posts
                tweet_id=tweet_id,                  # id will be 'new' and thereby not the real id
                url="/tweets/" + tweet_id,          # url
                title="New tweet",                  # title
                tweet=None,                         # since it's a new tweet, no values are predefined
                only_update_body=only_update_body(),# update header and footer?
                error=error,                        # any form validation error
                tweet_text=tweet_text,              # tweet text
                possible_errors=possible_errors,    # possible form validation errors
                type='new'
                )
        
        elif tweet_id != 'new': # if the tweet id isn't 'new' the user is editing an existing tweet
            ##### check whether the id is a uuid4
            if is_uuid(tweet_id) == False:
                redirect_path = "/home?alert-info=Tweet not found."
                return

            ###### connect to database
            db = sqlite3.connect(f"{get_file_path()}/database/database.db")

            ##### check that the tweet belongs to the user logged in
            tweet_and_user_id_match = len(db.execute(f"""
                SELECT *
                FROM tweets
                WHERE tweet_id == :tweet_id AND tweet_user_id == :user_id
                """, (tweet_id, user_id)).fetchall())
            if tweet_and_user_id_match != 1:
                redirect_path = "/home?alert-info=Tweet doesn't exist or isn't yours"
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
                redirect_path = "/home?alert-info=Tweet not found."
                return

            # if tweet is found, set info that's needed to display the editing inputs
            tweet_to_edit = {
                "tweet_id": tweet_id,
                "tweet_text": tweet[0].replace("<br />", ""),
                "tweet_image": tweet[1]
            }

            return dict(
                user_id=user_id,                    # user_id of logged in user
                users=users,                        # all users to display 'who to follow' aside
                tweets=tweets,                      # all tweets
                tweet_id=tweet_id,                  # tweet_id
                posts=posts,                        # all posts
                tweet=tweet_to_edit,                # the tweet the user is editing
                url="/tweets/" + tweet_id,          # url
                title="Edit tweet",                 # title
                only_update_body=only_update_body(),# update header and footer?
                error=error,                        # any form validation error
                tweet_text=tweet_text,              # tweet text
                possible_errors=possible_errors,    # possible form validation errors
                type='edit'
                )
        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return redirect("/home")

    finally:
        if db != None:
            db.close()
        if redirect_path != None:
            redirect(redirect_path)