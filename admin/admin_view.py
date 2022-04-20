from bottle import get, response, request, view
from common import get_all_tweets

@get("/admin")
@view("admin.html")
def _():
    try:
        ##### get all tweets and users data
        tweets = get_all_tweets(None)

        ##### alert info
        alert_info = request.params.get("alert-info") or None

        ##### return view
        return dict(
            tweets=tweets,          # all tweets
            url="/admin",           # url
            title="Admin Board",    # title
            alert_info=alert_info   # alert message
            )

    except Exception as ex:
        print("Exception: " + str(ex))
        response.status = 500
        return
