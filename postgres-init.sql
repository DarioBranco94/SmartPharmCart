CREATE TABLE IF NOT EXISTS ward (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

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

CREATE TABLE IF NOT EXISTS mqtt_outbox (
    id SERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    payload TEXT NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart_location (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES cart(id),
    x REAL,
    y REAL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
