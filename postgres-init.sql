DROP TABLE IF EXISTS cart_location;
DROP TABLE IF EXISTS mqtt_outbox;
DROP TABLE IF EXISTS movement;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS batch;
DROP TABLE IF EXISTS drug_master;
DROP TABLE IF EXISTS compartment;
DROP TABLE IF EXISTS drawer_state;
DROP TABLE IF EXISTS drawer;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS ward;
DROP TABLE IF EXISTS staff;

CREATE TABLE ward (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
    ward_id INTEGER REFERENCES ward(id),
    name TEXT NOT NULL
);

CREATE TABLE drawer (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES cart(id),
    number INTEGER NOT NULL
);

CREATE TABLE compartment (
    id SERIAL PRIMARY KEY,
    drawer_id INTEGER NOT NULL REFERENCES drawer(id),
    number INTEGER NOT NULL
);

CREATE TABLE drug_master (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE batch (
    id SERIAL PRIMARY KEY,
    drug_id INTEGER NOT NULL REFERENCES drug_master(id),
    code TEXT,
    expiry DATE
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES batch(id),
    compartment_id INTEGER NOT NULL REFERENCES compartment(id),
    quantity INTEGER NOT NULL DEFAULT 0,
    UNIQUE(batch_id, compartment_id)
);

CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT UNIQUE,
    password TEXT,
    badge TEXT UNIQUE
);

CREATE TABLE movement (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER NOT NULL REFERENCES inventory(id),
    change INTEGER NOT NULL,
    reason TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    staff_id INTEGER REFERENCES staff(id)
);

CREATE TABLE drawer_state (
    drawer_id INTEGER PRIMARY KEY,
    state TEXT NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mqtt_outbox (
    id SERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    payload TEXT NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_location (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES cart(id),
    x REAL,
    y REAL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default data
INSERT INTO cart (id, name) VALUES (1, 'Cart 1');
INSERT INTO ward (id, name) VALUES (1, 'Default Ward');
UPDATE cart SET ward_id = 1 WHERE id = 1;
INSERT INTO staff (name, username, password, badge) VALUES ('Admin', 'admin', 'admin', '0001');

-- Create drawers and compartments for cart 1
INSERT INTO drawer (cart_id, number) VALUES
    (1, 1),(1, 2),(1, 3),(1, 4),(1, 5);

INSERT INTO compartment (drawer_id, number) VALUES
    (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),
    (2,1),(2,2),(2,3),(2,4),(2,5),(2,6),
    (3,1),(3,2),(3,3),(3,4),(3,5),(3,6),
    (4,1),(4,2),(4,3),(4,4),(4,5),(4,6),
    (5,1),(5,2),(5,3),(5,4),(5,5),(5,6);
