from bottle import get, response, view

from settings import get_all_tweets

@get("/admin")
@view("admin.html")
def _():
    try:
        ##### get all tweets and users data
        tweets = get_all_tweets(None)

        ##### return view
        return dict(
            tweets=tweets,          # all tweets
            url="/admin",           # url
            title="Administrator",  # title
            )

    except Exception as ex:
        print(ex)
        response.status = 500
        return
