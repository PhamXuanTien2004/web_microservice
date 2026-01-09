-- 1. Database
CREATE DATABASE IF NOT EXISTS auth_service_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 2. User
CREATE USER IF NOT EXISTS 'auth_user'@'localhost'
IDENTIFIED WITH mysql_native_password BY 'root@root';

-- 3. Quyền
GRANT ALL PRIVILEGES ON auth_service_db.* 
TO 'auth_user'@'localhost';

FLUSH PRIVILEGES;

SHOW DATABASES;

SELECT * FROM auth_service_db;
