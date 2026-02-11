-- Tạo Database nếu chưa có
CREATE DATABASE IF NOT EXISTS iot_monitoring;
USE iot_monitoring;

-- 1. Bảng Users (Dùng cho Auth & User Service)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Bảng Sensor Types (Ví dụ: Nhiệt độ, Độ ẩm)
CREATE TABLE IF NOT EXISTS sensor_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL, -- Ví dụ: Temperature
    unit VARCHAR(10) NOT NULL  -- Ví dụ: °C
);

-- 3. Bảng Sensors (Mỗi User sở hữu nhiều cảm biến)
CREATE TABLE IF NOT EXISTS sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    mqtt_topic VARCHAR(255) UNIQUE NOT NULL,
    min_threshold FLOAT,
    max_threshold FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES sensor_types(id)
);

-- 4. Bảng Sensor Data (Lưu lịch sử số liệu - Dùng cho Analytics)
CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (sensor_id, timestamp),
    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
);

-- 5. Bảng Alerts (Lưu lịch sử cảnh báo)
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    message TEXT NOT NULL,
    status ENUM('active', 'acknowledged', 'resolved') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
);