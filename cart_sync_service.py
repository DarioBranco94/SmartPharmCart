import json
import os
import time
import paho.mqtt.client as mqtt
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.environ.get('DB_PATH', 'carrello.db')

CENTRAL_HOST = os.environ.get('CENTRAL_MQTT_HOST', 'central-broker')
CENTRAL_PORT = int(os.environ.get('CENTRAL_MQTT_PORT', '1883'))

INTERVAL = int(os.environ.get('SYNC_INTERVAL', '15'))

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

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.isolation_level = None
    client = mqtt.Client()
    client.connect(CENTRAL_HOST, CENTRAL_PORT, 60)
    client.loop_start()

    try:
        while True:
            cur = conn.cursor()
            cur.execute('SELECT id, topic, payload FROM mqtt_outbox WHERE sent = 0 ORDER BY id')
            rows = cur.fetchall()
            for _id, topic, payload in rows:
                client.publish(topic, payload)
                cur.execute('UPDATE mqtt_outbox SET sent = 1 WHERE id = ?', (_id,))
            conn.commit()
            cur.close()
            time.sleep(INTERVAL)
    finally:
        client.loop_stop()
        client.disconnect()
        conn.close()


if __name__ == '__main__':
    main()
