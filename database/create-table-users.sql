DROP TABLE IF EXISTS users;

CREATE TABLE users(
    user_id                 TEXT UNIQUE NOT NULL,
    user_display_name       TEXT NOT NULL,
    user_username           TEXT UNIQUE NOT NULL,
    user_email              TEXT UNIQUE NOT NULL,
    user_password           TEXT NOT NULL,
    user_created_at         TEXT NOT NULL,
    user_current_session    TEXT,
    user_profile_image      TEXT,
    user_profile_header     TEXT,
    user_is_verified        TEXT NOT NULL,
    PRIMARY KEY(user_id)
) WITHOUT ROWID;