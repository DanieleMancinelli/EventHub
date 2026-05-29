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
        self.execute_query(query_events)
        # (Altre tabelle verranno create qui man mano che servono)

    def aggiungi_evento(self, titolo, desc, data, luogo, cat, prezzo, posti, img, org_id):
        query = '''
        INSERT INTO eventi (titolo, descrizione, data_evento, luogo, categoria, prezzo, posti_totali, posti_disponibili, immagine_copertina, organizzatore_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        return self.execute_query(query, (titolo, desc, data, luogo, cat, prezzo, posti, posti, img, org_id))

    def get_eventi_filtrati(self, categoria=None, data=None, luogo=None, prezzo_max=None):
        query = "SELECT id, titolo, descrizione, data_evento, luogo, categoria, prezzo, posti_disponibili FROM eventi WHERE 1=1"
        params = []
        if categoria:
            query += " AND categoria = %s"
            params.append(categoria)
        if data:
            query += " AND DATE(data_evento) = %s"
            params.append(data)
        if luogo:
            query += " AND luogo LIKE %s"
            params.append(f"%{luogo}%")
        if prezzo_max:
            query += " AND prezzo <= %s"
            params.append(prezzo_max)
        
        return self.fetch_query(query, params)

    def get_evento_by_id(self, evento_id):
        return self.fetch_query("SELECT * FROM eventi WHERE id = %s", (evento_id,))
