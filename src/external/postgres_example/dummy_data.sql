CREATE TABLE product (
    productID SERIAL PRIMARY KEY,
    price FLOAT,
    on_sale BOOLEAN,
    product_name VARCHAR(100) NOT NULL
);

INSERT INTO product (price, on_sale, product_name)
VALUES
(19.99, TRUE, 'Coffee Maker'),
(89.99, FALSE, 'Stand Mixer'),
(12.50, TRUE, 'Travel Mug'),
(49.99, FALSE, 'Wireless Earbuds'),
(129.99, TRUE, 'Robot Vacuum'),
(8.99, FALSE, 'Cutting Board'),
(34.99, TRUE, 'Yoga Mat'),
(59.99, FALSE, 'Air Fryer'),
(22.50, TRUE, 'Desk Lamp'),
(149.99, FALSE, 'Smart Thermostat'),
(17.99, TRUE, 'Bamboo Shower Caddy'),
(299.00, FALSE, 'Electric Scooter'),
(14.99, TRUE, 'Insulated Water Bottle'),
(79.99, FALSE, 'Portable Bluetooth Speaker'),
(199.99, TRUE, 'Cordless Drill Set'),
(29.99, FALSE, 'Indoor Plant Pot'),
(159.00, TRUE, 'Office Chair');