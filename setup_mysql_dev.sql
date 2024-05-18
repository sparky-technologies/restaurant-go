-- sql script


CREATE DATABASE IF NOT EXISTS restaurant_db;
       CREATE USER IF NOT EXISTS 'restaurant_user'@'localhost' IDENTIFIED BY 'Restaurant_pwd123@';
              GRANT ALL PRIVILEGES ON restaurant_db.* TO 'restaurant_user'@'localhost';
                                      GRANT SELECT ON performance_schema.* TO 'restaurant_user'@'localhost';
FLUSH PRIVILEGES;