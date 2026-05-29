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
        self.execute_query('CREATE TABLE IF NOT EXISTS eventi (id INT AUTO_INCREMENT PRIMARY KEY, titolo VARCHAR(255) NOT NULL, descrizione TEXT, data_evento DATETIME NOT NULL, luogo VARCHAR(255) NOT NULL, categoria VARCHAR(100), prezzo DECIMAL(10, 2) DEFAULT 0.0, posti_totali INT NOT NULL, posti_disponibili INT NOT NULL, immagine_copertina LONGBLOB, organizzatore_id VARCHAR(100) NOT NULL)')
        self.execute_query('CREATE TABLE IF NOT EXISTS iscrizioni (id INT AUTO_INCREMENT PRIMARY KEY, evento_id INT, utente_id VARCHAR(100), codice_biglietto VARCHAR(255), FOREIGN KEY (evento_id) REFERENCES eventi(id) ON DELETE CASCADE)')
        # AGGIUNTA COLONNA USERNAME
        self.execute_query('CREATE TABLE IF NOT EXISTS recensioni (id INT AUTO_INCREMENT PRIMARY KEY, evento_id INT, utente_id VARCHAR(100), username VARCHAR(100), rating INT, commento TEXT, segnalata BOOLEAN DEFAULT FALSE, FOREIGN KEY (evento_id) REFERENCES eventi(id) ON DELETE CASCADE)')

    def get_eventi_filtrati(self, cat=None, dat=None, luo=None, prz=None):
        query = "SELECT id, titolo, descrizione, data_evento, luogo, categoria, prezzo, posti_disponibili FROM eventi WHERE 1=1"
        params = []
        if cat: query += " AND categoria = %s"; params.append(cat)
        if dat: query += " AND DATE(data_evento) = %s"; params.append(dat)
        if luo: query += " AND luogo LIKE %s"; params.append(f"%{luo}%")
        if prz: query += " AND prezzo <= %s"; params.append(prz)
        return self.fetch_query(query, params)

    def get_evento_by_id(self, id): return self.fetch_query("SELECT * FROM eventi WHERE id = %s", (id,))
    
    def aggiungi_evento(self, t, d, dt, l, c, pr, po, img, org):
        query = "INSERT INTO eventi (titolo, descrizione, data_evento, luogo, categoria, prezzo, posti_totali, posti_disponibili, immagine_copertina, organizzatore_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        return self.execute_query(query, (t, d, dt, l, c, pr, po, po, img, org))

    def get_eventi_per_organizzatore(self, org_id): return self.fetch_query("SELECT * FROM eventi WHERE organizzatore_id = %s", (org_id,))

    def iscrivi_utente(self, ev_id, u_id):
        ev = self.get_evento_by_id(ev_id)
        if not ev or ev[0]['posti_disponibili'] <= 0 or ev[0]['data_evento'] < datetime.now(): return False
        cod = f"TICKET-{ev_id}-{u_id[:5]}"
        self.execute_query("INSERT INTO iscrizioni (evento_id, utente_id, codice_biglietto) VALUES (%s, %s, %s)", (ev_id, u_id, cod))
        self.execute_query("UPDATE eventi SET posti_disponibili = posti_disponibili - 1 WHERE id = %s", (ev_id,))
        return cod

    def get_biglietti_utente(self, u_id): return self.fetch_query("SELECT e.titolo, e.data_evento, e.luogo, i.codice_biglietto FROM iscrizioni i JOIN eventi e ON i.evento_id = e.id WHERE i.utente_id = %s", (u_id,))

    def get_recensioni_evento(self, ev_id): return self.fetch_query("SELECT * FROM recensioni WHERE evento_id = %s AND segnalata = FALSE", (ev_id,))

    def aggiungi_recensione(self, ev_id, u_id, user, r, c):
        query = "INSERT INTO recensioni (evento_id, utente_id, username, rating, commento) VALUES (%s, %s, %s, %s, %s)"
        self.execute_query(query, (ev_id, u_id, user, r, c))

    def segnala_recensione(self, r_id): self.execute_query("UPDATE recensioni SET segnalata = TRUE WHERE id = %s", (r_id,))
