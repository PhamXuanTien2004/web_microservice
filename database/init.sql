-- ============================================
-- IoT Sensor Monitoring - Database Schema
-- Created: 2025-02-12
-- ============================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables (for clean restart)
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS sensor_statistics;
DROP TABLE IF EXISTS notification_logs;
DROP TABLE IF EXISTS alert_rules;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS sensor_data;
DROP TABLE IF EXISTS sensor_thresholds;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS sensor_types;
DROP TABLE IF EXISTS user_preferences;
DROP TABLE IF EXISTS refresh_tokens;
DROP TABLE IF EXISTS users;

-- ============================================
-- TABLE: users
-- ============================================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('user', 'admin') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: refresh_tokens
-- ============================================
CREATE TABLE refresh_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token (token(255)),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: user_preferences
-- ============================================
CREATE TABLE user_preferences (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    email_alerts BOOLEAN DEFAULT TRUE,
    sms_alerts BOOLEAN DEFAULT FALSE,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'vi',
    timezone VARCHAR(50) DEFAULT 'Asia/Ho_Chi_Minh',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: sensor_types
-- ============================================
CREATE TABLE sensor_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    default_unit VARCHAR(20),
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: sensors
-- ============================================
CREATE TABLE sensors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type_id INT NOT NULL,
    mqtt_topic VARCHAR(255) UNIQUE NOT NULL,
    location VARCHAR(255),
    description TEXT,
    status ENUM('active', 'inactive', 'error') DEFAULT 'active',
    last_seen TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES sensor_types(id),
    INDEX idx_user_id (user_id),
    INDEX idx_mqtt_topic (mqtt_topic),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: sensor_thresholds
-- ============================================
CREATE TABLE sensor_thresholds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sensor_id INT UNIQUE NOT NULL,
    min_value DECIMAL(10, 2),
    max_value DECIMAL(10, 2),
    warning_min DECIMAL(10, 2),
    warning_max DECIMAL(10, 2),
    critical_min DECIMAL(10, 2),
    critical_max DECIMAL(10, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: sensor_data
-- ============================================
CREATE TABLE sensor_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sensor_id INT NOT NULL,
    value DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20),
    quality ENUM('good', 'warning', 'critical', 'error') DEFAULT 'good',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE,
    INDEX idx_sensor_timestamp (sensor_id, timestamp DESC),
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_quality (quality)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: alerts
-- ============================================
CREATE TABLE alerts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sensor_id INT NOT NULL,
    user_id INT NOT NULL,
    alert_type ENUM('warning', 'critical', 'offline', 'recovered') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    message TEXT NOT NULL,
    sensor_value DECIMAL(10, 2),
    threshold_value DECIMAL(10, 2),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP NULL,
    acknowledged_by INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (acknowledged_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_acknowledged (acknowledged),
    INDEX idx_severity (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: alert_rules
-- ============================================
CREATE TABLE alert_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sensor_id INT NOT NULL,
    rule_name VARCHAR(100) NOT NULL,
    condition_type ENUM('threshold', 'offline', 'custom') NOT NULL,
    cooldown_minutes INT DEFAULT 15,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE,
    INDEX idx_sensor_enabled (sensor_id, enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: notification_logs
-- ============================================
CREATE TABLE notification_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    alert_id BIGINT NOT NULL,
    channel ENUM('email', 'sms', 'push') NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
    error_message TEXT NULL,
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_sent_at (sent_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: sensor_statistics
-- ============================================
CREATE TABLE sensor_statistics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sensor_id INT NOT NULL,
    period ENUM('hourly', 'daily', 'weekly', 'monthly') NOT NULL,
    period_start TIMESTAMP NOT NULL,
    min_value DECIMAL(10, 2),
    max_value DECIMAL(10, 2),
    avg_value DECIMAL(10, 2),
    std_dev DECIMAL(10, 2),
    data_points INT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE,
    UNIQUE KEY unique_period (sensor_id, period, period_start),
    INDEX idx_period_start (period_start DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLE: audit_logs
-- ============================================
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_created (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- VERIFICATION
-- ============================================
SELECT '✅ Database schema created successfully!' AS status;
SELECT COUNT(*) AS total_tables FROM information_schema.tables 
WHERE table_schema = 'iot_monitoring';