import json
import os
import time
import paho.mqtt.client as mqtt
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    'host': os.environ.get('DB_HOST', 'db'),
    'port': os.environ.get('DB_PORT', 5432),
    'dbname': os.environ.get('DB_NAME', 'cart'),
    'user': os.environ.get('DB_USER', 'cart'),
    'password': os.environ.get('DB_PASSWORD', 'cart'),
}

MQTT_HOST = os.environ.get('MQTT_HOST', 'mosquitto')
MQTT_PORT = int(os.environ.get('MQTT_PORT', '1883'))

TOPICS = [
    ('movement', 0),
    ('drawer/state', 0),
]

def get_conn():
    return psycopg2.connect(**DB_PARAMS)

conn = get_conn()
conn.autocommit = True

def validate_payload(topic, data):
    if topic == 'movement':
        required = {'inventory_id', 'change', 'reason', 'staff_id'}
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
            'INSERT INTO movement (inventory_id, change, reason, staff_id) VALUES (%s,%s,%s,%s)',
            (data['inventory_id'], data['change'], data['reason'], data['staff_id'])
        )
    elif msg.topic == 'drawer/state':
        cur.execute(
            'INSERT INTO drawer_state (drawer_id, state, ts) VALUES (%s,%s, NOW()) '
            'ON CONFLICT (drawer_id) DO UPDATE SET state = EXCLUDED.state, ts = NOW()',
            (data['drawer_id'], data['state'])
        )
    cur.execute(
        'INSERT INTO mqtt_outbox (topic, payload) VALUES (%s,%s)',
        (msg.topic, json.dumps(data))
    )
    cur.close()


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
