

INSERT INTO users (
        user_id,
        user_display_name,
        user_username,
        user_email,
        user_password,
        user_created_at,
        user_current_session,
        user_profile_image,
        user_profile_header,
        user_is_verified
        ) 
VALUES (
        "f94fcdc6-a222-41bb-a48d-d42cf3f48596",
        "Mickey Mouse",
        "disneysfavorite",
        "5f7e0672-0a45-4627-90b5-51f54c7709f1@mail.com",
        "123",
        "1650267381",
        "NULL"
      
        ,"NULL",
        "NULL",
        False
        );


-- DELETE FROM users 
-- WHERE user_id = "1f0e0c12-2c44-4dfc-aec5-42c5246fc986";

-- UPDATE users
-- SET user_id = "b1589d36-40d6-49f6-bacb-d35a9e7dd474"
-- WHERE user_id = 1;


-- UPDATE users
-- SET user_display_name = "Sarah Is Here"
-- WHERE user_id = "b1589d36-40d6-49f6-bacb-d35a9e7dd474";


-- UPDATE likes
-- SET fk_user_id = "b1589d36-40d6-49f6-bacb-d35a9e7dd474"
-- WHERE fk_user_id = 1;