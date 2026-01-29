CREATE DATABASE IF NOT EXISTS user_service_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'auth_user'@'localhost'
IDENTIFIED WITH mysql_native_password BY 'root@root';
GRANT ALL PRIVILEGES ON user_service_db.*
TO 'auth_user'@'localhost';

FLUSH PRIVILEGES;
SHOW DATABASES;