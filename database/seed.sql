-- ============================================
-- IoT Sensor Monitoring - Seed Data
-- Created: 2025-02-12
-- ============================================

USE iot_monitoring;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- INSERT SENSOR TYPES
-- ============================================

INSERT INTO sensor_types (name, description, default_unit, icon) VALUES
('Temperature', 'Cảm biến nhiệt độ', '°C', 'thermometer'),
('Humidity', 'Cảm biến độ ẩm', '%', 'droplet'),
('Pressure', 'Cảm biến áp suất khí quyển', 'hPa', 'gauge');

SELECT '✅ Sensor types inserted' AS status;

-- ============================================
-- INSERT USERS
-- ============================================

-- Password cho tất cả users: "Password123!"
-- Hash được generate bằng bcrypt (cost factor 12)
-- Bạn có thể generate hash mới tại: https://bcrypt-generator.com

INSERT INTO users (username, email, password_hash, phone, role, is_active) VALUES
-- Admin user
('admin', 'admin@iotmonitoring.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5qdgJ7T5zZ5S6', '+84901234567', 'admin', TRUE),

-- Regular users
('john_doe', 'john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5qdgJ7T5zZ5S6', '+84907654321', 'user', TRUE),
('jane_smith', 'jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5qdgJ7T5zZ5S6', '+84909876543', 'user', TRUE),
('test_user', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5qdgJ7T5zZ5S6', '+84912345678', 'user', TRUE);

SELECT '✅ Users inserted' AS status;

-- ============================================
-- INSERT USER PREFERENCES
-- ============================================

INSERT INTO user_preferences (user_id, email_alerts, sms_alerts, theme, language) VALUES
(1, TRUE, TRUE, 'dark', 'vi'),   -- Admin
(2, TRUE, FALSE, 'light', 'vi'),  -- john_doe
(3, TRUE, TRUE, 'light', 'en'),   -- jane_smith
(4, FALSE, FALSE, 'dark', 'vi');  -- test_user

SELECT '✅ User preferences inserted' AS status;

-- ============================================
-- INSERT SENSORS
-- ============================================

-- Sensors cho john_doe (user_id = 2)
INSERT INTO sensors (user_id, name, type_id, mqtt_topic, location, description, status) VALUES
(2, 'Nhiệt độ phòng khách', 1, 'sensors/2/1/data', 'Phòng khách, tầng 1', 'Cảm biến DHT22', 'active'),
(2, 'Độ ẩm phòng ngủ', 2, 'sensors/2/2/data', 'Phòng ngủ, tầng 2', 'Cảm biến DHT22', 'active'),
(2, 'Nhiệt độ bếp', 1, 'sensors/2/3/data', 'Bếp, tầng 1', 'Cảm biến DS18B20', 'active'),
(2, 'Áp suất không khí', 3, 'sensors/2/4/data', 'Ban công, tầng 2', 'Cảm biến BMP280', 'active'),
(2, 'Nhiệt độ garage', 1, 'sensors/2/5/data', 'Garage', 'Cảm biến DHT11', 'inactive');

-- Sensors cho jane_smith (user_id = 3)
INSERT INTO sensors (user_id, name, type_id, mqtt_topic, location, description, status) VALUES
(3, 'Nhiệt độ văn phòng', 1, 'sensors/3/1/data', 'Văn phòng tầng 3', 'Cảm biến DHT22', 'active'),
(3, 'Độ ẩm kho hàng', 2, 'sensors/3/2/data', 'Kho hàng tầng 1', 'Cảm biến SHT31', 'active'),
(3, 'Nhiệt độ server room', 1, 'sensors/3/3/data', 'Phòng server tầng 2', 'Cảm biến precision', 'active');

-- Sensor cho test_user (user_id = 4)
INSERT INTO sensors (user_id, name, type_id, mqtt_topic, location, description, status) VALUES
(4, 'Test Sensor 1', 1, 'sensors/4/1/data', 'Test Location', 'For testing purposes', 'active');

SELECT '✅ Sensors inserted' AS status;

-- ============================================
-- INSERT SENSOR THRESHOLDS
-- ============================================

-- Temperature sensors: Normal 15-35°C
INSERT INTO sensor_thresholds (sensor_id, min_value, max_value, warning_min, warning_max, critical_min, critical_max) VALUES
(1, 15.0, 35.0, 18.0, 30.0, 10.0, 40.0),  -- Phòng khách
(3, 15.0, 35.0, 18.0, 32.0, 10.0, 45.0),  -- Bếp
(5, 5.0, 40.0, 10.0, 35.0, 0.0, 50.0),    -- Garage
(6, 18.0, 28.0, 20.0, 26.0, 15.0, 32.0),  -- Văn phòng
(8, 15.0, 25.0, 18.0, 23.0, 12.0, 28.0);  -- Server room

-- Humidity sensors: Normal 30-70%
INSERT INTO sensor_thresholds (sensor_id, min_value, max_value, warning_min, warning_max, critical_min, critical_max) VALUES
(2, 30.0, 70.0, 35.0, 65.0, 20.0, 80.0),  -- Phòng ngủ
(7, 40.0, 60.0, 45.0, 55.0, 30.0, 70.0);  -- Kho hàng

-- Pressure sensors: Normal 980-1030 hPa
INSERT INTO sensor_thresholds (sensor_id, min_value, max_value, warning_min, warning_max, critical_min, critical_max) VALUES
(4, 980.0, 1030.0, 990.0, 1020.0, 970.0, 1040.0);  -- Áp suất

SELECT '✅ Sensor thresholds inserted' AS status;

-- ============================================
-- INSERT SAMPLE SENSOR DATA
-- ============================================

-- Temperature sensor data (last 24 hours)
INSERT INTO sensor_data (sensor_id, value, unit, quality, timestamp) VALUES
-- Sensor 1: Nhiệt độ phòng khách
(1, 24.5, '°C', 'good', DATE_SUB(NOW(), INTERVAL 3 HOUR)),
(1, 24.8, '°C', 'good', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(1, 25.2, '°C', 'good', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(1, 25.0, '°C', 'good', DATE_SUB(NOW(), INTERVAL 30 MINUTE)),
(1, 24.7, '°C', 'good', NOW()),

-- Sensor 2: Độ ẩm phòng ngủ
(2, 55.0, '%', 'good', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(2, 56.5, '%', 'good', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(2, 58.0, '%', 'good', DATE_SUB(NOW(), INTERVAL 30 MINUTE)),
(2, 57.5, '%', 'good', NOW()),

-- Sensor 4: Áp suất
(4, 1013.2, 'hPa', 'good', DATE_SUB(NOW(), INTERVAL 3 HOUR)),
(4, 1012.8, 'hPa', 'good', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(4, 1013.5, 'hPa', 'good', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(4, 1013.0, 'hPa', 'good', NOW());

SELECT '✅ Sample sensor data inserted' AS status;

-- ============================================
-- INSERT SAMPLE ALERTS
-- ============================================

INSERT INTO alerts (sensor_id, user_id, alert_type, severity, message, sensor_value, threshold_value, acknowledged, created_at) VALUES
(1, 2, 'warning', 'medium', 'Nhiệt độ phòng khách vượt ngưỡng cảnh báo', 31.5, 30.0, FALSE, DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(3, 2, 'critical', 'high', 'Nhiệt độ bếp vượt ngưỡng nguy hiểm!', 42.0, 40.0, TRUE, DATE_SUB(NOW(), INTERVAL 5 HOUR));

SELECT '✅ Sample alerts inserted' AS status;

-- ============================================
-- INSERT ALERT RULES
-- ============================================

INSERT INTO alert_rules (sensor_id, rule_name, condition_type, cooldown_minutes, enabled) VALUES
(1, 'Temperature threshold check', 'threshold', 15, TRUE),
(2, 'Humidity threshold check', 'threshold', 15, TRUE),
(3, 'Kitchen temperature alert', 'threshold', 10, TRUE),
(8, 'Server room temperature critical', 'threshold', 5, TRUE);

SELECT '✅ Alert rules inserted' AS status;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- FINAL VERIFICATION
-- ============================================

SELECT '========================================' AS '';
SELECT '✅ SEED DATA COMPLETED!' AS status;
SELECT '========================================' AS '';

SELECT 
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM sensor_types) AS total_sensor_types,
    (SELECT COUNT(*) FROM sensors) AS total_sensors,
    (SELECT COUNT(*) FROM sensor_thresholds) AS total_thresholds,
    (SELECT COUNT(*) FROM sensor_data) AS total_data_points,
    (SELECT COUNT(*) FROM alerts) AS total_alerts,
    (SELECT COUNT(*) FROM alert_rules) AS total_alert_rules;

SELECT '========================================' AS '';
SELECT '📝 TEST CREDENTIALS' AS info;
SELECT '========================================' AS '';

SELECT 
    username, 
    email, 
    'Password123!' AS password, 
    role,
    CASE WHEN is_active THEN '✅ Active' ELSE '❌ Inactive' END AS status
FROM users
ORDER BY role DESC, id;

SELECT '========================================' AS '';