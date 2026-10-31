-- SafarSathi schema reference. Existing tables/data are not dropped.
CREATE DATABASE IF NOT EXISTS safarsathi_db;
USE safarsathi_db;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('customer','admin') NOT NULL DEFAULT 'customer',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS packages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  destination VARCHAR(150) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL DEFAULT 0,
  duration_days INT NOT NULL DEFAULT 1,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  package_id INT NOT NULL,
  travel_date DATE NOT NULL,
  travel_time TIME NULL,
  travellers INT NOT NULL DEFAULT 1,
  hotel_preference VARCHAR(50) NOT NULL DEFAULT 'Standard',
  status VARCHAR(30) NOT NULL DEFAULT 'Pending',
  payment_status VARCHAR(30) NOT NULL DEFAULT 'Not Paid',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_bookings_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_bookings_package FOREIGN KEY (package_id) REFERENCES packages(id)
);

-- Run this only if your existing bookings table does not yet have travel_time:
-- ALTER TABLE bookings ADD COLUMN travel_time TIME NULL AFTER travel_date;

-- Add sample packages only if your packages table is empty (run manually after checking):
-- INSERT INTO packages (title,destination,description,price,duration_days,active) VALUES
-- ('Royal Jaipur Tour','Jaipur','Explore forts, palaces and local markets.',5999,3,TRUE),
-- ('Goa Beach Holiday','Goa','Enjoy beaches and a relaxing holiday.',8999,4,TRUE),
-- ('Manali Mountain Escape','Manali','Discover mountain views and scenic valleys.',10999,5,TRUE);
