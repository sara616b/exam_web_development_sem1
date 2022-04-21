from bottle import delete, redirect, response
from common import delete_tweet

@delete("/admin/delete/<tweet_id>")
def _(tweet_id):
    redirect_path = None
    try:
        ##### if tweet_id doesn't exist
        if not tweet_id:
            redirect_path = "/admin?alert-info=Tweet not found. Please try again"
            return

        ##### delete tweet
        counter = delete_tweet(tweet_id)

        ##### if no tweet has been deleted, error 
        if counter != 1:
            redirect_path = "/admin?alert-info=No tweets deleted. Please try again"
            return

        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return
    
    finally:
        if redirect_path != None:
            return redirect(redirect_path)
