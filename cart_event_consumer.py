import json
import os
import time
import paho.mqtt.client as mqtt
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.environ.get('DB_PATH', 'carrello.db')

MQTT_HOST = os.environ.get('MQTT_HOST', 'mosquitto')
MQTT_PORT = int(os.environ.get('MQTT_PORT', '1883'))

TOPICS = [
    ('movement', 0),
    ('drawer/state', 0),
]

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

conn = get_conn()

def validate_payload(topic, data):
    if topic == 'movement':
        required = {
            'drug_id', 'batch_code', 'drawer_id', 'compartment_number',
            'change', 'movement_type', 'staff_id'
        }
        return required.issubset(data)
    if topic == 'drawer/state':
        required = {'drawer_id', 'state'}
        return required.issubset(data)
    return False

def on_connect(client, userdata, flags, rc, properties=None):
    for t, q in TOPICS:
        client.subscribe(t, q)


def on_message(client, userdata, msg):
    global conn
    payload = msg.payload.decode('utf-8')
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print('Invalid JSON:', payload)
        return

    if not validate_payload(msg.topic, data):
        print('Invalid payload for', msg.topic, data)
        return

    cur = conn.cursor()
    if msg.topic == 'movement':
        cur.execute(
            'INSERT INTO movement (drug_id, batch_code, drawer_id, compartment_number, change, movement_type, staff_id) VALUES (?,?,?,?,?,?,?)',
            (
                data['drug_id'],
                data['batch_code'],
                data['drawer_id'],
                data['compartment_number'],
                data['change'],
                data['movement_type'],
                data['staff_id'],
            ),
        )
    elif msg.topic == 'drawer/state':
        cur.execute(
            'INSERT INTO drawer_state (drawer_id, state, ts) VALUES (?, ?, CURRENT_TIMESTAMP) '
            'ON CONFLICT(drawer_id) DO UPDATE SET state=excluded.state, ts=CURRENT_TIMESTAMP',
            (data['drawer_id'], data['state'])
        )
    cur.execute(
        'INSERT INTO mqtt_outbox (topic, payload) VALUES (?, ?)',
        (msg.topic, json.dumps(data))
    )
    conn.commit()
    cur.close()

def wait_for_sqlite(path, retries=10, delay=2):
    for i in range(retries):
        if os.path.exists(path):
            try:
                sqlite3.connect(path).close()
                print("✅ DB pronto, connessione riuscita.")
                return
            except sqlite3.Error as e:
                print(f"⏳ Tentativo {i+1}/{retries}: DB non pronto ({e})")
        else:
            print(f"⏳ Tentativo {i+1}/{retries}: DB non trovato")
        time.sleep(delay)
    raise Exception("❌ Errore: impossibile connettersi al DB dopo vari tentativi.")

def main():
    wait_for_sqlite(DB_PATH)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
