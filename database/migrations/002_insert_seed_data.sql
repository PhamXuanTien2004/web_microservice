USE iot_monitoring;

-- Thêm loại cảm biến cơ bản
INSERT INTO sensor_types (name, unit) VALUES 
('Temperature', '°C'), 
('Humidity', '%'), 
('Air Quality', 'AQI');

-- Thêm tài khoản Admin và User mẫu (Password đều là: password123 đã hash)
-- Lưu ý: Trong thực tế, Auth-Service sẽ xử lý việc hash này.
INSERT INTO users (username, password_hash, email, role) VALUES 
('admin', '$2b$12$Kpb/D.J.y86/M..vK/mBbuYvI.P/h1R..', 'admin@example.com', 'admin'),
('user01', '$2b$12$Kpb/D.J.y86/M..vK/mBbuYvI.P/h1R..', 'user01@example.com', 'user');

-- Gán cảm biến mẫu cho user01 (Id = 2)
INSERT INTO sensors (user_id, type_id, name, mqtt_topic, min_threshold, max_threshold) VALUES 
(2, 1, 'Phòng ngủ - Nhiệt độ', 'sensors/user01/temp_bed', 18.0, 30.0),
(2, 2, 'Phòng khách - Độ ẩm', 'sensors/user01/humi_living', 40.0, 70.0);