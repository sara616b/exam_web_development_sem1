INSERT INTO users (user_id, user_display_name, user_username, user_email, user_password, user_created_at, user_current_session) 
VALUES (1, "Sarah", "sarah", "sarah@mail.com", 123, 12345, NULL);


DELETE FROM users 
WHERE user_id = "d7535bcf-8fde-4e73-b534-335104d28165";

UPDATE users
SET user_id = "b1589d36-40d6-49f6-bacb-d35a9e7dd474"
WHERE user_id = 1;


UPDATE users
SET user_display_name = "Sarah Is Here"
WHERE user_id = "b1589d36-40d6-49f6-bacb-d35a9e7dd474";


UPDATE likes
SET fk_user_id = "b1589d36-40d6-49f6-bacb-d35a9e7dd474"
WHERE fk_user_id = 1;