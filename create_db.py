import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Percorso file DB
db_path = Path(os.getenv("DB_PATH", "./carrello.db"))
db_path.parent.mkdir(parents=True, exist_ok=True)

# Remove existing database to start fresh
if db_path.exists():
    db_path.unlink()

# Leggi lo schema SQL generato
with open("./schema.sql", "r") as f:
    schema_sql = f.read()

# Crea e inizializza il database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.executescript(schema_sql)
conn.commit()
conn.close()

