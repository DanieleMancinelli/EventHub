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

    def connect(self): return pymysql.connect(**self.db_config)
    def execute_query(self, query, params=()):
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        finally: conn.close()
    def fetch_query(self, query, params=()):
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        finally: conn.close()

    def create_tables(self):
        self.execute_query('CREATE TABLE IF NOT EXISTS eventi (id INT AUTO_INCREMENT PRIMARY KEY, titolo VARCHAR(255) NOT NULL, descrizione TEXT, data_evento DATETIME NOT NULL, luogo VARCHAR(255) NOT NULL, categoria VARCHAR(100), prezzo DECIMAL(10, 2) DEFAULT 0.0, posti_totali INT NOT NULL, posti_disponibili INT NOT NULL, immagine_copertina LONGBLOB, organizzatore_id VARCHAR(100) NOT NULL)')
        self.execute_query('CREATE TABLE IF NOT EXISTS iscrizioni (id INT AUTO_INCREMENT PRIMARY KEY, evento_id INT, utente_id VARCHAR(100), codice_biglietto VARCHAR(255), FOREIGN KEY (evento_id) REFERENCES eventi(id) ON DELETE CASCADE)')
        self.execute_query('CREATE TABLE IF NOT EXISTS recensioni (id INT AUTO_INCREMENT PRIMARY KEY, evento_id INT, utente_id VARCHAR(100), username VARCHAR(100), rating INT, commento TEXT, segnalata BOOLEAN DEFAULT FALSE, FOREIGN KEY (evento_id) REFERENCES eventi(id) ON DELETE CASCADE)')
        self.execute_query('CREATE TABLE IF NOT EXISTS utenti (utente_id VARCHAR(100) PRIMARY KEY, username VARCHAR(100), is_banned BOOLEAN DEFAULT FALSE, is_organizzatore BOOLEAN DEFAULT FALSE)')

    def sync_user(self, u_id, username): self.execute_query("INSERT IGNORE INTO utenti (utente_id, username) VALUES (%s, %s)", (u_id, username))
    def is_user_banned(self, u_id):
        res = self.fetch_query("SELECT is_banned FROM utenti WHERE utente_id = %s", (u_id,))
        return res[0]['is_banned'] if res else False
    def get_all_users(self): return self.fetch_query("SELECT * FROM utenti")
    def toggle_ban(self, u_id): self.execute_query("UPDATE utenti SET is_banned = NOT is_banned WHERE utente_id = %s", (u_id,))
    def toggle_organizzatore(self, u_id): self.execute_query("UPDATE utenti SET is_organizzatore = NOT is_organizzatore WHERE utente_id = %s", (u_id,))

    def get_eventi_filtrati(self, cat=None, dat=None, luo=None, prz=None):
        query = "SELECT id, titolo, descrizione, data_evento, luogo, categoria, prezzo, posti_totali, posti_disponibili, organizzatore_id FROM eventi WHERE 1=1"
        params = []
        if cat: query += " AND categoria = %s"; params.append(cat)
        if dat: query += " AND DATE(data_evento) = %s"; params.append(dat)
        if luo: query += " AND luogo LIKE %s"; params.append(f"%{luo}%")
        if prz: query += " AND prezzo <= %s"; params.append(prz)
        return self.fetch_query(query, params)

    def update_evento(self, ev_id, t, d, dt, l, c, pr, po, img, org_id):
        if img:
            query = "UPDATE eventi SET titolo=%s, descrizione=%s, data_evento=%s, luogo=%s, categoria=%s, prezzo=%s, posti_totali=%s, immagine_copertina=%s WHERE id=%s AND organizzatore_id=%s"
            self.execute_query(query, (t, d, dt, l, c, pr, po, img, ev_id, org_id))
        else:
            query = "UPDATE eventi SET titolo=%s, descrizione=%s, data_evento=%s, luogo=%s, categoria=%s, prezzo=%s, posti_totali=%s WHERE id=%s AND organizzatore_id=%s"
            self.execute_query(query, (t, d, dt, l, c, pr, po, ev_id, org_id))

    def get_evento_by_id(self, id): return self.fetch_query("SELECT * FROM eventi WHERE id = %s", (id,))
    def get_eventi_per_organizzatore(self, org): 
        query = "SELECT e.id, e.titolo, e.descrizione, e.data_evento, e.luogo, e.categoria, e.prezzo, e.posti_totali, e.posti_disponibili, (SELECT COUNT(*) FROM iscrizioni WHERE evento_id = e.id) as num_iscritti, (SELECT COUNT(*) FROM iscrizioni WHERE evento_id = e.id) * e.prezzo as incasso_stimato, (SELECT AVG(rating) FROM recensioni WHERE evento_id = e.id) as rating_medio FROM eventi e WHERE organizzatore_id = %s"
        return self.fetch_query(query, (org,))
    def aggiungi_evento(self, t, d, dt, l, c, pr, po, img, org): query = "INSERT INTO eventi (titolo, descrizione, data_evento, luogo, categoria, prezzo, posti_totali, posti_disponibili, immagine_copertina, organizzatore_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"; return self.execute_query(query, (t, d, dt, l, c, pr, po, po, img, org))
    def elimina_evento(self, id, org_id): self.execute_query("DELETE FROM eventi WHERE id = %s AND organizzatore_id = %s", (id, org_id))
    
    def iscrivi_utente(self, ev_id, u_id):
        ev = self.get_evento_by_id(ev_id)
        if not ev or ev[0]['posti_disponibili'] <= 0 or ev[0]['data_evento'] < datetime.now(): return False
        suffix = datetime.now().strftime('%M%S%f')[:6]
        cod = f"TICKET-{ev_id}-{u_id[:4]}-{suffix}"
        self.execute_query("INSERT INTO iscrizioni (evento_id, utente_id, codice_biglietto) VALUES (%s, %s, %s)", (ev_id, u_id, cod))
        self.execute_query("UPDATE eventi SET posti_disponibili = posti_disponibili - 1 WHERE id = %s", (ev_id,))
        return cod

    # FIX: Cancella per codice biglietto specifico
    def disiscrivi_utente(self, codice, u_id):
        res = self.fetch_query("SELECT evento_id FROM iscrizioni WHERE codice_biglietto = %s AND utente_id = %s", (codice, u_id))
        if res:
            ev_id = res[0]['evento_id']
            self.execute_query("DELETE FROM iscrizioni WHERE codice_biglietto = %s AND utente_id = %s", (codice, u_id))
            self.execute_query("UPDATE eventi SET posti_disponibili = posti_disponibili + 1 WHERE id = %s", (ev_id,))

    def get_biglietti_utente(self, u_id): return self.fetch_query("SELECT e.id as evento_id, e.titolo, e.data_evento, e.luogo, i.codice_biglietto FROM iscrizioni i JOIN eventi e ON i.evento_id = e.id WHERE i.utente_id = %s", (u_id,))
    def get_iscritti_evento(self, ev_id): return self.fetch_query("SELECT utente_id, codice_biglietto FROM iscrizioni WHERE evento_id = %s", (ev_id,))
    def get_recensioni_evento(self, ev_id): return self.fetch_query("SELECT * FROM recensioni WHERE evento_id = %s", (ev_id,))
    def aggiungi_recensione(self, ev_id, u_id, user, r, c): self.execute_query("INSERT INTO recensioni (evento_id, utente_id, username, rating, commento) VALUES (%s, %s, %s, %s, %s)", (ev_id, u_id, user, r, c))
    def segnala_recensione(self, r_id): self.execute_query("UPDATE recensioni SET segnalata = TRUE WHERE id = %s", (r_id,))
