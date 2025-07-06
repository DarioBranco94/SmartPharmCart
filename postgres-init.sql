
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


CREATE TABLE IF NOT EXISTS cart (
    id SERIAL PRIMARY KEY,
    ward_id INTEGER REFERENCES ward(id),
    name TEXT NOT NULL,
    label TEXT,
    model TEXT,
    serial_no TEXT
);

CREATE TABLE IF NOT EXISTS drawer_state (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS drawer (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES cart(id),
    number INTEGER NOT NULL,
    label TEXT,
    state_id INTEGER REFERENCES drawer_state(id)
);

CREATE TABLE IF NOT EXISTS compartment (
    id SERIAL PRIMARY KEY,
    drawer_id INTEGER NOT NULL REFERENCES drawer(id),
    number INTEGER NOT NULL,
    label TEXT
);

CREATE TABLE IF NOT EXISTS drug_master (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    form TEXT,
    strength TEXT,
    manufacturer TEXT,
    last_updated TIMESTAMP
);

CREATE TABLE IF NOT EXISTS batch (
    id SERIAL PRIMARY KEY,
    drug_id INTEGER NOT NULL REFERENCES drug_master(id),
    code TEXT,
    expiry DATE,
    batch_number TEXT,
    mfg_date DATE,
    exp_date DATE
);

CREATE TABLE IF NOT EXISTS inventory (
    compartment_id INTEGER NOT NULL REFERENCES compartment(id),
    drug_code INTEGER NOT NULL REFERENCES drug_master(id),
    batch_id INTEGER NOT NULL REFERENCES batch(id),
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (compartment_id, drug_code, batch_id)
);

CREATE TABLE IF NOT EXISTS staff (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT UNIQUE,
    password TEXT,
    badge TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS movement (
    id SERIAL PRIMARY KEY,
    movement_type TEXT NOT NULL,
    compartment_id INTEGER,
    drug_code INTEGER,
    batch_id INTEGER,
    qty INTEGER NOT NULL,
    operator_id INTEGER REFERENCES staff(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compartment_id, drug_code, batch_id)
        REFERENCES inventory (compartment_id, drug_code, batch_id)
);

CREATE TABLE mqtt_outbox (
    id SERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    payload TEXT NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggiorna la tabella inventory ad ogni inserimento in movement
CREATE OR REPLACE FUNCTION update_inventory_after_movement()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE inventory SET quantity = quantity + NEW.change
    WHERE id = NEW.inventory_id;
    IF (SELECT quantity FROM inventory WHERE id = NEW.inventory_id) < 0 THEN
        RAISE EXCEPTION 'Negative inventory quantity';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER movement_inventory_update
AFTER INSERT ON movement
FOR EACH ROW
EXECUTE FUNCTION update_inventory_after_movement();


CREATE TABLE IF NOT EXISTS cart_location (

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