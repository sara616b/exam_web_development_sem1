DROP TABLE IF EXISTS tweets;

CREATE TABLE tweets(
    tweet_id            TEXT UNIQUE NOT NULL,
    tweet_text          TEXT,
    tweet_created_at    TEXT NOT NULL,
    tweet_updated_at    TEXT,
    tweet_image         TEXT,
    tweet_user_id       TEXT NOT NULL,
    PRIMARY KEY(tweet_id)
) WITHOUT ROWID;