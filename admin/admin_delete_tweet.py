from bottle import delete, redirect, response
from common import delete_tweet

@delete("/admin/delete/<tweet_id>")
def _(tweet_id):
    try:
        ##### if tweet_id doesn't exist
        if not tweet_id:
            response.status = 204
            return

        ##### delete tweet
        counter = delete_tweet(tweet_id)

        ##### if no tweets deleted, error 
        # TODO add redirection path
        if counter == 0:
            print("No tweets deleted")
            response.status = 500
            return

        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return redirect("/admin")
