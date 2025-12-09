-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS sequencing_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE sequencing_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Note: Default users will be created by the Flask application
-- Admin: admin@example.com / admin123
-- User: user@example.com / user123


