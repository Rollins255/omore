-- Database for tracking gas cylinder inventory for multiple suppliers

-- Create the database
DROP DATABASE IF EXISTS gas_inventory_db;
CREATE DATABASE gas_inventory_db;
USE gas_inventory_db;

-- Suppliers table
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT unique_supplier UNIQUE (supplier_name, phone)
);

-- Cylinder types table
CREATE TABLE cylinder_types (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    capacity_kg DECIMAL(5,2) NOT NULL,
    description VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_capacity UNIQUE (capacity_kg)
);

-- Inventory table (tracks current stock)
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    type_id INT NOT NULL,
    empty_count INT DEFAULT 0,
    full_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES cylinder_types(type_id) ON DELETE CASCADE,
    CONSTRAINT unique_inventory UNIQUE (supplier_id, type_id)
);

-- Restocking table (records when new cylinders arrive)
CREATE TABLE restocking (
    restock_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    type_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    restock_date DATE NOT NULL,
    received_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES cylinder_types(type_id) ON DELETE CASCADE
);

-- Sales table (records when cylinders are sold)
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    inventory_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    sale_date DATE NOT NULL,
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    sold_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id) ON DELETE CASCADE
);

-- Insert sample cylinder types
INSERT INTO cylinder_types (capacity_kg, description) VALUES
(6.00, 'Standard 6kg cooking gas cylinder'),
(13.00, 'Large 13kg cooking gas cylinder');

-- Insert sample suppliers
INSERT INTO suppliers (supplier_name, contact_person, phone, email, address) VALUES
('GasPro Ltd', 'John Smith', '+254712345678', 'john@gaspro.com', '123 Mombasa Road, Nairobi'),
('CleanEnergy Gas', 'Mary Johnson', '+254723456789', 'mary@cleanenergy.com', '456 Thika Road, Nairobi'),
('EcoGas Solutions', 'David Kimani', '+254734567890', 'david@ecogas.co.ke', '789 Ngong Road, Nairobi');

-- Insert initial inventory
INSERT INTO inventory (supplier_id, type_id, empty_count, full_count) VALUES
(1, 1, 20, 50),  -- GasPro 6kg
(1, 2, 15, 30),  -- GasPro 13kg
(2, 1, 10, 40),  -- CleanEnergy 6kg
(2, 2, 5, 25),   -- CleanEnergy 13kg
(3, 1, 8, 35),    -- EcoGas 6kg
(3, 2, 12, 28);   -- EcoGas 13kg

-- Insert sample restocking records
INSERT INTO restocking (supplier_id, type_id, quantity, unit_price, restock_date, received_by) VALUES
(1, 1, 100, 800.00, '2023-01-15', 'James Mwangi'),
(1, 2, 50, 1500.00, '2023-01-15', 'James Mwangi'),
(2, 1, 80, 820.00, '2023-01-20', 'Sarah Omondi'),
(3, 2, 40, 1550.00, '2023-01-25', 'Peter Kamau');

-- Insert sample sales records
INSERT INTO sales (inventory_id, quantity, unit_price, sale_date, customer_name, customer_phone) VALUES
(1, 2, 1200.00, '2023-02-01', 'Alice Wanjiku', '+254700111222'),
(1, 1, 1200.00, '2023-02-02', 'Robert Kipchoge', '+254700222333'),
(3, 3, 1250.00, '2023-02-03', 'Susan Akinyi', '+254700333444'),
(4, 1, 2400.00, '2023-02-04', 'Michael Odhiambo', '+254700444555');

GRANT ALL PRIVILEGES ON gas_inventory_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;