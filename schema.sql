DROP TABLE IF EXISTS cart_location;
DROP TABLE IF EXISTS mqtt_outbox;
DROP TABLE IF EXISTS movement;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS batch;
DROP TABLE IF EXISTS drug_master;
DROP TABLE IF EXISTS compartment;
DROP TABLE IF EXISTS drawer;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS ward;
DROP TABLE IF EXISTS staff;

CREATE TABLE ward (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ward_id INTEGER,
    name TEXT NOT NULL,
    FOREIGN KEY (ward_id) REFERENCES ward(id)
);

CREATE TABLE drawer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES cart(id)
);

CREATE TABLE compartment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drawer_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    FOREIGN KEY (drawer_id) REFERENCES drawer(id)
);

CREATE TABLE drug_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE batch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL,
    code TEXT,
    expiry DATE,
    FOREIGN KEY (drug_id) REFERENCES drug_master(id)
);

CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    compartment_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    UNIQUE(batch_id, compartment_id),
    FOREIGN KEY (batch_id) REFERENCES batch(id),
    FOREIGN KEY (compartment_id) REFERENCES compartment(id)
);

CREATE TABLE movement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER NOT NULL,
    change INTEGER NOT NULL,
    reason TEXT,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    staff_id INTEGER,
    FOREIGN KEY (inventory_id) REFERENCES inventory(id),
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

CREATE TABLE staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT UNIQUE,
    password TEXT,
    badge TEXT UNIQUE
);

CREATE TABLE mqtt_outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    payload TEXT NOT NULL,
    sent INTEGER DEFAULT 0,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    x REAL,
    y REAL,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES cart(id)
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

-- Aggiorna la tabella inventory ad ogni inserimento in movement
CREATE TRIGGER movement_inventory_update
AFTER INSERT ON movement
BEGIN
    UPDATE inventory
    SET quantity = quantity + NEW.change
    WHERE id = NEW.inventory_id;

    -- Se la quantita' scende sotto zero annulla la transazione
    SELECT CASE
        WHEN (SELECT quantity FROM inventory WHERE id = NEW.inventory_id) < 0
        THEN RAISE(ROLLBACK, 'Negative inventory quantity')
    END;
END;
