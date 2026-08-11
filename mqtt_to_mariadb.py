# sobotify/tools/analysing/mqtt_to_mariadb.py

import os
import csv
import glob
from datetime import datetime

# 1) .env laden (optional, falls installiert)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # läuft auch ohne python-dotenv, dann müssen Variablen im System gesetzt sein
    pass

import pymysql  # pip install pymysql

# ---------- Konfiguration aus .env ----------
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "sobotify_data")
DB_USER = os.getenv("DB_USER", "sobouser")
DB_PASS = os.getenv("DB_PASS", "")  # darf leer sein

# Pfad, den dein logger.py benutzt:
LOG_BASE_DIR = os.path.join(os.path.expanduser("~"), ".sobotify", "log")
def get_all_logfiles():
    """
    Sucht unter ~/.sobotify/log nach ALLEN Verzeichnissen
    und gibt eine sortierte Liste der _log_messages.csv-Pfade zurück.
    """
    if not os.path.isdir(LOG_BASE_DIR):
        raise FileNotFoundError(f"Log-Basisordner nicht gefunden: {LOG_BASE_DIR}")

    csv_files = []
    for d in glob.glob(os.path.join(LOG_BASE_DIR, "*")):
        if not os.path.isdir(d):
            continue
        csv_path = os.path.join(d, "_log_messages.csv")
        if os.path.isfile(csv_path):
            csv_files.append(csv_path)

    if not csv_files:
        raise FileNotFoundError(f"Keine _log_messages.csv in {LOG_BASE_DIR} gefunden")

    # sortiert nach Pfad → durch die Zeitstempel-Namen ist das auch zeitlich sortiert
    csv_files.sort()
    return csv_files


# ---------- Topic-Mapping nach deiner Vorgabe ----------
ROBOT_SPEAK_TOPICS = (
    "robot/command/say",
    "robot/status/speech_done",
    "robot_control/command/speak-and-gesture",
    "log/quiz/question",
)

HUMAN_SPEAK_TOPICS = (
    "speech-recognition/partial-text",
    "speech-recognition/text",
    "speech-recognition/statement",
    "log/quiz/answer/correct",
    "log/quiz/answer/wrong",
)

ROBOT_REACTION_TOPICS = (
    "facial_processing/dominant_emotion",
    "facial_processing/name",
    "robot/command/move",
    "robot/command/search_head",
)

SETTINGS_ROBOT_TOPICS = (
    "robot/status/init-done",
    "robot/status/file_extension",
    "robot/status/samplerate",
    "robot/command/get_file_extension",
    "robot/command/set_language",
    "robot/command/set_speed",
    "robot/command/streaming/start",
    "robot/command/streaming/stop",
    "robot/command/motion_terminate",
    "robot_control/status/init-done",
    "robot_control/status/done",
    "robot_control/command/set-speed",
    "robot_control/command/set-min-speed",
    "robot_control/command/set-max-speed",
)

SETTINGS_HUMAN_TOPICS = (
    "facial_processing/status/init-done",
    "facial_processing/start",
    "facial_processing/stop",
    "speech-recognition/status/init-done",
    "speech-recognition/control/record/start",
)

LOGGING_META_TOPICS = (
    "logging_server/status/init-done",
    "logging_server/status/log_dir",
    "log/app_info",
    "log/quiz/run/110",
    "log/quiz/search_answers/69",
)

# Antwort-Themen (wir nehmen ein paar Varianten mit rein, falls du später was änderst)
ANSWER_TOPICS = (
    "log/quiz/answer/correct",
    "log/quiz/answer/wrong",
    "quiz/answer/correct",
    "quiz/answer/wrong",
)

def to_dt(ts_iso: str) -> datetime:
    """Logger schreibt ISO 'YYYY-MM-DDTHH:MM:SS.ffffff'."""
    return datetime.fromisoformat(ts_iso).replace(tzinfo=None)

# Merker für letzte Frage & Korrektheit (für Frage–Antwort-Paare)
last_question = None



def get_latest_logfile():
    """
    Sucht unter ~/.sobotify/log nach dem neuesten Verzeichnis
    und gibt den Pfad zu _log_messages.csv zurück.
    """
    if not os.path.isdir(LOG_BASE_DIR):
        raise FileNotFoundError(f"Log-Basisordner nicht gefunden: {LOG_BASE_DIR}")

    subdirs = [d for d in glob.glob(os.path.join(LOG_BASE_DIR, "*")) if os.path.isdir(d)]
    if not subdirs:
        raise FileNotFoundError(f"Keine Log-Ordner in {LOG_BASE_DIR} gefunden")

    latest_dir = sorted(subdirs)[-1]
    csv_path = os.path.join(latest_dir, "_log_messages.csv")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"_log_messages.csv nicht gefunden in {latest_dir}")
    return csv_path


def connect_db(db_name=None):
    """stellt Verbindung her; kann ohne Passwort arbeiten"""
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS or None,
        database=db_name,
        charset="utf8mb4",
        autocommit=True,
    )
    return conn


def init_database():
    """DB + Tabellen anlegen, wenn noch nicht da."""
    # erst ohne DB verbinden
    conn = connect_db(None)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4;")
    cur.close()
    conn.close()

    # jetzt mit DB verbinden und Tabellen anlegen
    conn = connect_db(DB_NAME)
    cur = conn.cursor()

    # gemeinsame Struktur
    table_sql = """
    CREATE TABLE IF NOT EXISTS {table_name} (
        ts DATETIME(6),
        topic VARCHAR(255),
        message TEXT
    ) CHARACTER SET utf8mb4;
    """

    for t in (
        "robot_speak",
        "human_speak",
        "robot_reaction",
        "settings_robot",
        "settings_human",
        "logging_meta",
    ):
        cur.execute(table_sql.format(table_name=t))

    # Interaktionstabelle anlegen
    ensure_interactions_table(conn)

    conn.close()


def ensure_interactions_table(conn):
    """Tabelle für Frage–Antwort-Paare mit Latenz anlegen (falls nicht vorhanden)."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_interactions (
        question_time DATETIME(6),
        question_text TEXT,
        answer_time   DATETIME(6),
        answer_text   TEXT,
        latency_ms    INT
    ) CHARACTER SET utf8mb4;

        """
    )

    cur.close()



def classify_topic(topic: str) -> str:
    """gibt den Tabellennamen für ein Topic zurück"""
    if topic in ROBOT_SPEAK_TOPICS:
        return "robot_speak"
    if topic in HUMAN_SPEAK_TOPICS:
        return "human_speak"
    if topic in ROBOT_REACTION_TOPICS:
        return "robot_reaction"
    if topic in SETTINGS_ROBOT_TOPICS:
        return "settings_robot"
    if topic in SETTINGS_HUMAN_TOPICS:
        return "settings_human"
    if topic in LOGGING_META_TOPICS:
        return "logging_meta"
    # alles andere landet auch in logging_meta („und Reste“)
    return "logging_meta"


def parse_ts(ts_str: str):
    """
    logger.py schreibt ISO-Format, z. B. 2025-10-29T09:31:22.123456
    Das wandeln wir in String, den MariaDB mit DATETIME(6) versteht.
    """
    dt = datetime.fromisoformat(ts_str).replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def import_csv_to_db(csv_path: str):
    """Komplette Log-Datei in Tabellen + quiz_interactions importieren."""
    global last_question, last_answer_ok

    conn = connect_db(DB_NAME)
    ensure_interactions_table(conn)
    cur = conn.cursor()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts_iso = row.get("timestamp", "")
            topic = row.get("topic", "")
            msg = row.get("message", "")

            if not topic or not ts_iso:
                continue

            # Basis-Tabellen füllen
            ts_db = parse_ts(ts_iso)
            table = classify_topic(topic)
            cur.execute(
                f"INSERT INTO {table} (ts, topic, message) VALUES (%s, %s, %s)",
                (ts_db, topic, msg),
            )

            # Frage merken
            if topic == "log/quiz/question":
                last_question = {"ts": ts_iso, "text": msg}


            # Finale Antwort (statement) → Interaktion
            elif topic == "speech-recognition/statement" and last_question is not None:
                try:
                    q_dt = to_dt(last_question["ts"])
                    a_dt = to_dt(ts_iso)
                except ValueError:
                    last_question = None
                    continue

                latency_ms = int((a_dt - q_dt).total_seconds() * 1000)

                cur.execute(
                    """
                    INSERT INTO quiz_interactions
                        (question_time, question_text,
                         answer_time,   answer_text,
                         latency_ms)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        q_dt.strftime("%Y-%m-%d %H:%M:%S.%f"),
                        last_question["text"],
                        a_dt.strftime("%Y-%m-%d %H:%M:%S.%f"),
                        msg,
                        latency_ms,
                    ),
                )

                # Frage „verbrauchen“, Status zurücksetzen
                last_question = None

    conn.close()
    print(f"Fertig: {csv_path} in MariaDB importiert.")


def main():
    init_database()
    csv_files = get_all_logfiles()
    for csv_path in csv_files:
        print(f"Importiere {csv_path} ...")
        import_csv_to_db(csv_path)



if __name__ == "__main__":
    main()
