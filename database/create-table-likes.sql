DROP TABLE IF EXISTS likes;

CREATE TABLE likes(
    fk_user_id                 TEXT NOT NULL,
    fk_tweet_id                TEXT NOT NULL,
    PRIMARY KEY(fk_user_id, fk_tweet_id)
) WITHOUT ROWID;