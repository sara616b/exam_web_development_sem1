from bottle import delete, redirect, response
from common import delete_tweet, confirm_user_is_logged_in, is_uuid

@delete("/tweets/delete/<tweet_id>")
def _(tweet_id):
    
    ##### the user needs to be logged in to delete tweet
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)
  
    redirect_path = None
    try:
        ##### check whether the id is a uuid4
        if is_uuid(tweet_id) == False:
            redirect_path = "/home?alert-info=Trying to delete the tweet failed. Please try again."
            return

        ##### delete tweet and get the count of how many posts where deleted
        counter = delete_tweet(tweet_id)
        
        ##### if 1 post wheren't deleted, redirect with error message
        if counter != 1:
            redirect_path = "/home?alert-info=Couldn't delete post. Please try again."
            return

        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return redirect("/login")

    finally:
        if redirect_path != None:
            return redirect(redirect_path)
