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

CENTRAL_HOST = os.environ.get('CENTRAL_MQTT_HOST', 'central-broker')
CENTRAL_PORT = int(os.environ.get('CENTRAL_MQTT_PORT', '1883'))

INTERVAL = int(os.environ.get('SYNC_INTERVAL', '15'))


def main():
    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = True
    client = mqtt.Client()
    client.connect(CENTRAL_HOST, CENTRAL_PORT, 60)
    client.loop_start()

    try:
        while True:
            with conn.cursor() as cur:
                cur.execute('SELECT id, topic, payload FROM mqtt_outbox WHERE sent = 0 ORDER BY id')
                rows = cur.fetchall()
                for _id, topic, payload in rows:
                    client.publish(topic, payload)
                    cur.execute('UPDATE mqtt_outbox SET sent = 1 WHERE id = %s', (_id,))
            time.sleep(INTERVAL)
    finally:
        client.loop_stop()
        client.disconnect()
        conn.close()


if __name__ == '__main__':
    main()
