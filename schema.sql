DROP TABLE IF EXISTS cart_location;
DROP TABLE IF EXISTS drawer_state;
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ward_id INTEGER,
    name TEXT NOT NULL,
    label TEXT,
    model TEXT,
    serial_no TEXT,
    FOREIGN KEY (ward_id) REFERENCES ward(id)
);

CREATE TABLE drawer_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE drawer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    label TEXT,
    state_id INTEGER,
    FOREIGN KEY (cart_id) REFERENCES cart(id),
    FOREIGN KEY (state_id) REFERENCES drawer_state(id)
);

CREATE TABLE compartment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drawer_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    label TEXT,
    FOREIGN KEY (drawer_id) REFERENCES drawer(id)
);

CREATE TABLE drug_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    form TEXT,
    strength TEXT,
    manufacturer TEXT,
    last_updated DATETIME
);

CREATE TABLE batch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL,
    code TEXT,
    expiry DATE,
    batch_number TEXT,
    mfg_date DATE,
    exp_date DATE,
    FOREIGN KEY (drug_id) REFERENCES drug_master(id)
);

CREATE TABLE inventory (
    compartment_id INTEGER NOT NULL,
    drug_code INTEGER NOT NULL,
    batch_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (compartment_id, drug_code, batch_id),
    FOREIGN KEY (compartment_id) REFERENCES compartment(id),
    FOREIGN KEY (drug_code) REFERENCES drug_master(id),
    FOREIGN KEY (batch_id) REFERENCES batch(id)
);

CREATE TABLE movement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movement_type TEXT NOT NULL,
    compartment_id INTEGER,
    drug_code INTEGER,
    batch_id INTEGER,
    qty INTEGER NOT NULL,
    operator_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compartment_id, drug_code, batch_id)
        REFERENCES inventory(compartment_id, drug_code, batch_id),
    FOREIGN KEY (operator_id) REFERENCES staff(id)
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

CREATE TABLE drawer_state (
    drawer_id INTEGER PRIMARY KEY,
    state TEXT NOT NULL,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (drawer_id) REFERENCES drawer(id)
);

-- Default data
INSERT INTO cart (id, name, label, model, serial_no) VALUES
    (1, 'Cart 1', 'Cart 1', 'Model A', 'SN001');
INSERT INTO ward (id, name) VALUES (1, 'Default Ward');
UPDATE cart SET ward_id = 1 WHERE id = 1;
INSERT INTO staff (name, username, password, badge) VALUES ('Admin', 'admin', 'admin', '0001');

INSERT INTO drawer_state (id, name) VALUES
    (1, 'closed'),
    (2, 'open'),
    (3, 'locked');

-- Create drawers and compartments for cart 1
INSERT INTO drawer (cart_id, number, label) VALUES
    (1, 1, 'Drawer 1'),
    (1, 2, 'Drawer 2'),
    (1, 3, 'Drawer 3'),
    (1, 4, 'Drawer 4'),
    (1, 5, 'Drawer 5');

INSERT INTO compartment (drawer_id, number, label) VALUES
    (1,1,'C1-1'),(1,2,'C1-2'),(1,3,'C1-3'),(1,4,'C1-4'),(1,5,'C1-5'),(1,6,'C1-6'),
    (2,1,'C2-1'),(2,2,'C2-2'),(2,3,'C2-3'),(2,4,'C2-4'),(2,5,'C2-5'),(2,6,'C2-6'),
    (3,1,'C3-1'),(3,2,'C3-2'),(3,3,'C3-3'),(3,4,'C3-4'),(3,5,'C3-5'),(3,6,'C3-6'),
    (4,1,'C4-1'),(4,2,'C4-2'),(4,3,'C4-3'),(4,4,'C4-4'),(4,5,'C4-5'),(4,6,'C4-6'),
    (5,1,'C5-1'),(5,2,'C5-2'),(5,3,'C5-3'),(5,4,'C5-4'),(5,5,'C5-5'),(5,6,'C5-6');
