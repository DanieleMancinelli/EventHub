import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3306))
)

try:
    with conn.cursor() as cursor:
        # Aggiungiamo la colonna username
        cursor.execute("ALTER TABLE recensioni ADD COLUMN username VARCHAR(100) AFTER utente_id")
    conn.commit()
    print("✅ Database riparato: Colonna 'username' aggiunta con successo!")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("ℹ️ La colonna esiste già, tutto a posto.")
    else:
        print(f"❌ Errore: {e}")
finally:
    conn.close()
