DROP TABLE IF EXISTS retweets;

CREATE TABLE retweets(
    retweet_id                 TEXT NOT NULL,
    fk_user_id                 TEXT NOT NULL,
    fk_tweet_id                TEXT NOT NULL,
    retweeted_at               TEXT NOT NULL,
    PRIMARY KEY(retweet_id)
) WITHOUT ROWID;