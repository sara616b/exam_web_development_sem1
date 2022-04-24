from bottle import get, response, request, view
from common import get_all_tweets

@get("/admin")
@view("admin.html")
def _():
    try:
        ##### return view
        return dict(
            tweets=get_all_tweets(None),                        # all tweets
            url="/admin",                                       # url
            title="Admin Board",                                # title
            alert_info=request.params.get("alert-info") or None # alert message
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return
