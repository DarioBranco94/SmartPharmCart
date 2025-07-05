import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Percorso file DB
db_path = Path(os.getenv("DB_PATH", "./carrello.db"))

# Leggi lo schema SQL generato
with open("./schema.sql", "r") as f:
    schema_sql = f.read()

# Crea e inizializza il database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.executescript(schema_sql)
conn.commit()
conn.close()

