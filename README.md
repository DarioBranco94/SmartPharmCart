# SmartPharmCart

Applicazione di esempio che combina una GUI Python con PyQt6 e un front-end Three.js servito da Node.js.

## Installazione delle dipendenze Python

Per installare i pacchetti necessari eseguire:

```bash
pip install -r requirements.txt
```

Configurare i parametri di connessione creando un file `.env` nella
cartella del progetto. Il file di esempio contiene le variabili per il
database, i broker MQTT e il percorso del file SQLite.

## Esecuzione

Avviare l'interfaccia grafica con:

```bash
python main.py
```

Per il front-end 3D è necessario avere Node.js, quindi:

```bash
npm install
npm start
```


=======
SmartPharmCart è un prototipo di carrello farmaci con interfaccia grafica in Python e visualizzazione 3D in un'applicazione web servita da Node.js. Il progetto mostra un modello 3D del carrello e consente di gestire l'elenco dei pazienti e dei farmaci da somministrare tramite un database SQLite.

## Prerequisiti

- **Python 3** (consigliato 3.10 o superiore)
- **Node.js** 20+
- **Docker** (facoltativo, per avviare il server web tramite `docker-compose`)

Per la parte Python è necessario installare i pacchetti `PyQt6` e `PyQt6-WebEngine`:

```bash
pip install PyQt6 PyQt6-WebEngine
```

## Inizializzazione del database

All'avvio è richiesto un file SQLite chiamato `carrello.db`. Per crearlo dal file di schema è sufficiente eseguire:

```bash
python create_db.py
```

Verrà generato il database con le tabelle necessarie.

## Avvio dell'applicazione

1. Installare le dipendenze Node.js:

   ```bash
   npm install
   ```

2. Creare il bundle JavaScript e copiare i file nella cartella `public`:

   ```bash
   npm run build
   ```

3. Avviare il server web (che espone i file statici su `http://localhost:3000`):

   ```bash
   npm start
   ```

   In alternativa è possibile utilizzare Docker:

   ```bash
   docker compose up
   ```
   Il comando leggerà automaticamente le variabili definite nel file `.env`.

4. Con il server web in esecuzione, avviare l'interfaccia Qt:

   ```bash
   python main.py
   ```

L'applicazione mostrerà la GUI con incorporata la pagina web del carrello 3D. Da qui si possono aggiungere pazienti, caricare i farmaci e gestire la somministrazione.


