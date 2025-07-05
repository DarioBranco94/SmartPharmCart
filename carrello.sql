DROP TABLE IF EXISTS Giri;
DROP TABLE IF EXISTS Pazienti;
DROP TABLE IF EXISTS Farmaci;
DROP TABLE IF EXISTS GiroPazienti;
DROP TABLE IF EXISTS Prescrizioni;

CREATE TABLE Giri (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    completato BOOLEAN DEFAULT 0
);

CREATE TABLE Pazienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE Farmaci (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE GiroPazienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    giro_id INTEGER NOT NULL,
    paziente_id INTEGER NOT NULL,
    ordine INTEGER DEFAULT 0,
    FOREIGN KEY (giro_id) REFERENCES Giri(id),
    FOREIGN KEY (paziente_id) REFERENCES Pazienti(id)
);

CREATE TABLE Prescrizioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    giro_id INTEGER NOT NULL,
    paziente_id INTEGER NOT NULL,
    farmaco_id INTEGER NOT NULL,
    caricato BOOLEAN DEFAULT 0,
    caricato_timestamp DATETIME,
    somministrato BOOLEAN DEFAULT 0,
    timestamp DATETIME,
    cassetto INTEGER,
    scomparto INTEGER,
    FOREIGN KEY (giro_id) REFERENCES Giri(id),
    FOREIGN KEY (paziente_id) REFERENCES Pazienti(id),
    FOREIGN KEY (farmaco_id) REFERENCES Farmaci(id)
);
