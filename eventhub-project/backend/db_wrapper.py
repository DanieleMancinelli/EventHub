import pymysql
import os
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
        # Tabella Eventi
        query_events = '''
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
        '''
        # Tabella Iscrizioni (Biglietti)
        query_registrations = '''
        CREATE TABLE IF NOT EXISTS iscrizioni (
            id INT AUTO_INCREMENT PRIMARY KEY,
            evento_id INT,
            utente_id VARCHAR(100),
            codice_biglietto VARCHAR(255) UNIQUE,
            FOREIGN KEY (evento_id) REFERENCES eventi(id) ON DELETE CASCADE
        )
        '''
        # Tabella Recensioni
        query_reviews = '''
        CREATE TABLE IF NOT EXISTS recensioni (
            id INT AUTO_INCREMENT PRIMARY KEY,
            evento_id INT,
            utente_id VARCHAR(100),
            rating INT CHECK (rating BETWEEN 1 AND 5),
            commento TEXT,
            segnalata BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (evento_id) REFERENCES eventi(id) ON DELETE CASCADE
        )
        '''
        self.execute_query(query_events)
        self.execute_query(query_registrations)
        self.execute_query(query_reviews)

    # Metodo base per testare la connessione
    def get_tutti_gli_eventi(self):
        return self.fetch_query("SELECT id, titolo, data_evento, luogo, categoria, prezzo, posti_disponibili FROM eventi")

