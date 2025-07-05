import sqlite3
from pathlib import Path

# Percorso file DB
db_path = Path("./carrello.db")

# Leggi lo schema SQL generato
with open("./carrello.sql", "r") as f:
    schema_sql = f.read()

# Crea e inizializza il database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.executescript(schema_sql)
conn.commit()
conn.close()

