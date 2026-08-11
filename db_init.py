import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "sobotify_data")
DB_USER = os.getenv("DB_USER", "")
DB_PASS = os.getenv("DB_PASS", "")  # oder leer

ROOT_USER = "root"
ROOT_PASS = input("Gib dein MariaDB-Root-Passwort ein (wird nicht gespeichert): ")

print("Verbinde mit MariaDB als root ...")
conn = pymysql.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=ROOT_USER,
    password=ROOT_PASS,
    charset="utf8mb4",
    autocommit=True
)
cur = conn.cursor()

# --- Datenbank und Benutzer anlegen ---
cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4;")
cur.execute(f"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASS}';")
cur.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost';")
cur.execute("FLUSH PRIVILEGES;")

print(f"Datenbank '{DB_NAME}' und Benutzer '{DB_USER}' erfolgreich angelegt.")
cur.close()
conn.close()
