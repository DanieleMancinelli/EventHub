import pymysql
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class DatabaseWrapper:
    def __init__(self):
        self.db_config = {
            'host': os.getenv("DB_HOST"),
            'user': os.getenv("DB_USER"),
            'password': os.getenv("DB_PASSWORD"),
            'database': os.getenv("DB_NAME"),
            'port': int(os.getenv("DB_PORT", 3306)),
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.create_tables()

    def connect(self):
        return pymysql.connect(**self.db_config)

    def execute_query(self, query, params=()):
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    def fetch_query(self, query, params=()):
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            conn.close()

    def create_tables(self):
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS eventi (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titolo VARCHAR(255) NOT NULL,
                descrizione TEXT,
                data_evento DATETIME NOT NULL,
                luogo VARCHAR(255) NOT NULL,
                categoria VARCHAR(100),
                prezzo DECIMAL(10, 2) DEFAULT 0.0,
                posti_totali INT NOT NULL,
                posti_disponibili INT NOT NULL,
                immagine_copertina LONGBLOB,
                organizzatore_id VARCHAR(100) NOT NULL
            )
        ''')
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS iscrizioni (
                id INT AUTO_INCREMENT PRIMARY KEY,
                evento_id INT,
                utente_id VARCHAR(100),
                codice_biglietto VARCHAR(255),
                FOREIGN KEY (evento_id) REFERENCES eventi(id) ON DELETE CASCADE
            )
        ''')
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS recensioni (
                id INT AUTO_INCREMENT PRIMARY KEY,
                evento_id INT,
                utente_id VARCHAR(100),
                rating INT,
                commento TEXT,
                segnalata BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (evento_id) REFERENCES eventi(id) ON DELETE CASCADE
            )
        ''')

    # --- EVENTI ---
    def get_evento_by_id(self, evento_id):
        return self.fetch_query("SELECT * FROM eventi WHERE id = %s", (evento_id,))

    def get_eventi_filtrati(self, categoria=None, data=None, luogo=None, prezzo_max=None):
        query = "SELECT id, titolo, descrizione, data_evento, luogo, categoria, prezzo, posti_disponibili FROM eventi WHERE 1=1"
        params = []
        if categoria: query += " AND categoria = %s"; params.append(categoria)
        if data: query += " AND DATE(data_evento) = %s"; params.append(data)
        if luogo: query += " AND luogo LIKE %s"; params.append(f"%{luogo}%")
        if prezzo_max: query += " AND prezzo <= %s"; params.append(prezzo_max)
        return self.fetch_query(query, params)

    def aggiungi_evento(self, titolo, desc, data, luogo, cat, prezzo, posti, img, org_id):
        query = "INSERT INTO eventi (titolo, descrizione, data_evento, luogo, categoria, prezzo, posti_totali, posti_disponibili, immagine_copertina, organizzatore_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        return self.execute_query(query, (titolo, desc, data, luogo, cat, prezzo, posti, posti, img, org_id))

    # --- ISCRIZIONI ---
    def iscrivi_utente(self, evento_id, utente_id):
        evento = self.get_evento_by_id(evento_id)
        if not evento or evento[0]['posti_disponibili'] <= 0: return False
        codice = f"TICKET-{evento_id}-{utente_id[:5]}"
        self.execute_query("INSERT INTO iscrizioni (evento_id, utente_id, codice_biglietto) VALUES (%s, %s, %s)", (evento_id, utente_id, codice))
        self.execute_query("UPDATE eventi SET posti_disponibili = posti_disponibili - 1 WHERE id = %s", (evento_id,))
        return codice

    def get_biglietti_utente(self, utente_id):
        query = "SELECT e.titolo, e.data_evento, e.luogo, i.codice_biglietto FROM iscrizioni i JOIN eventi e ON i.evento_id = e.id WHERE i.utente_id = %s"
        return self.fetch_query(query, (utente_id,))

    def get_iscritti_evento(self, evento_id):
        return self.fetch_query("SELECT utente_id, codice_biglietto FROM iscrizioni WHERE evento_id = %s", (evento_id,))

    # --- RECENSIONI & MODERAZIONE ---
    def aggiungi_recensione(self, evento_id, utente_id, rating, commento):
        query = "INSERT INTO recensioni (evento_id, utente_id, rating, commento) VALUES (%s, %s, %s, %s)"
        self.execute_query(query, (evento_id, utente_id, rating, commento))

    def segnala_recensione(self, recensione_id):
        self.execute_query("UPDATE recensioni SET segnalata = TRUE WHERE id = %s", (recensione_id,))

    def get_recensioni_segnalate(self):
        return self.fetch_query("SELECT r.*, e.titolo FROM recensioni r JOIN eventi e ON r.evento_id = e.id WHERE r.segnalata = TRUE")

    def elimina_recensione(self, recensione_id):
        self.execute_query("DELETE FROM recensioni WHERE id = %s", (recensione_id,))

    def approva_recensione(self, recensione_id):
        self.execute_query("UPDATE recensioni SET segnalata = FALSE WHERE id = %s", (recensione_id,))
