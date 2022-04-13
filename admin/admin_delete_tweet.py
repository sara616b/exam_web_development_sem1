from bottle import delete, redirect, response

from settings import delete_tweet

@delete("/admin/delete/<tweet_id>")
def _(tweet_id):
    try:
        counter = delete_tweet(tweet_id)
        if counter == 0:
            print("No tweets deleted")
            response.status = 500
            return
        return

    except Exception as ex:
        print(ex)
        response.status = 500
        return redirect("/admin")
