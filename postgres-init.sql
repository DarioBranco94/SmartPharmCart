CREATE TABLE IF NOT EXISTS movement (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER,
    change INTEGER NOT NULL,
    reason TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    staff_id INTEGER
);

CREATE SCHEMA IF NOT EXISTS drawer;
CREATE TABLE IF NOT EXISTS drawer.state (
    drawer_id INTEGER PRIMARY KEY,
    state TEXT NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mqtt_outbox (
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
