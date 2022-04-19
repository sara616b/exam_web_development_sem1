from bottle import redirect, response, delete
from common import delete_retweet, confirm_user_is_logged_in, is_uuid

@delete("/retweets/delete/<retweet_id>")
def _(retweet_id):
    ##### the user needs to be logged in to access this page
    if not confirm_user_is_logged_in():
        return redirect("/login?alert-info=You're not logged in.", code=303)

    redirect_path = None
    try:
        ##### check whether the id is a uuid4
        if is_uuid(retweet_id) == False:
            response.status = 400
            redirect_path = "/home?alert-info=Trying to delete the retweet failed. Please try again."
            return

        ##### delete rewteet and get the count of how many posts where deleted
        counter = delete_retweet(retweet_id)
        
        ##### if 1 post wheren't deleted, redirect with error message
        if counter != 1:
            redirect_path = "/home?alert-info=Couldn't delete post. Please try again."
            return

        return

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return redirect("/home")

    finally:
        if redirect_path != None:
            return redirect(redirect_path)
