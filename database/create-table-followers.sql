DROP TABLE IF EXISTS followers;

CREATE TABLE followers(
    fk_user_id_follower                 TEXT NOT NULL,
    fk_user_id_to_follow                TEXT NOT NULL,
    PRIMARY KEY(fk_user_id_follower, fk_user_id_to_follow)
) WITHOUT ROWID;