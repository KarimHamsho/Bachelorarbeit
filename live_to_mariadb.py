# sobotify/tools/analysing/live_to_mariadb.py

import os
import csv
import time
from datetime import datetime

import pymysql   # das ist in deiner sobotify-Umgebung vorhanden

# dotenv nur optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # kein dotenv installiert -> einfach Umgebungsvariablen / Defaults nehmen
    pass

# ---------- DB Konfig ----------
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "sobotify_data")
DB_USER = os.getenv("DB_USER", "sobouser")
DB_PASS = os.getenv("DB_PASS", "")  # leer = ohne Passwort

# ---------- Log-Verzeichnis ----------
LOG_BASE_DIR = os.path.join(os.path.expanduser("~"), ".sobotify", "log")

# Topic-Zuordnung – deine Struktur
TOPIC_MAP = {
    "robot_speak": (
        "robot/command/say",
        "robot/status/speech_done",
        "robot_control/command/speak-and-gesture",
        "log/quiz/question",
    ),
    "human_speak": (
        "speech-recognition/partial-text",
        "speech-recognition/text",
        "speech-recognition/statement",
        "log/quiz/answer/correct",
        "log/quiz/answer/wrong",
        "quiz/answer/correct",
        "quiz/answer/wrong",
    ),
    "robot_reaction": (
        "facial_processing/dominant_emotion",
        "facial_processing/name",
        "robot/command/move",
        "robot/command/search_head",
    ),
    "settings_robot": (
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
    ),
    "settings_human": (
        "facial_processing/status/init-done",
        "facial_processing/start",
        "facial_processing/stop",
        "speech-recognition/status/init-done",
        "speech-recognition/control/record/start",
    ),
    "logging_meta": (
        "logging_server/status/init-done",
        "logging_server/status/log_dir",
        "log/app_info",
        "log/quiz/run/110",
        "log/quiz/search_answers/69",
    ),
}

ANSWER_TOPICS = (
    "log/quiz/answer/correct",
    "log/quiz/answer/wrong",
    "quiz/answer/correct",
    "quiz/answer/wrong",
)

last_question = None  # Merker für Live-Frage


def connect_db():
    print(f"[live_to_mariadb] connect to MariaDB {DB_HOST}:{DB_PORT} db={DB_NAME} user={DB_USER}")
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS or None,
        database=DB_NAME,
        charset="utf8mb4",
        autocommit=True,
    )


def ensure_interactions_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_interactions (
        question_time DATETIME(6),
        question_text TEXT,
        answer_time   DATETIME(6),
        answer_text   TEXT,
        latency_ms    INT
    ) CHARACTER SET utf8mb4;
                """)
    cur.close()



def classify_topic(topic: str) -> str:
    for table, topics in TOPIC_MAP.items():
        if topic in topics:
            return table
    # unbekannte Topics landen wenigstens irgendwo
    return "logging_meta"


def parse_ts(ts_str: str) -> str:
    try:
        return datetime.fromisoformat(ts_str).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def get_latest_logfile() -> str:
    if not os.path.isdir(LOG_BASE_DIR):
        raise FileNotFoundError(f"log dir not found: {LOG_BASE_DIR}")
    subdirs = [
        os.path.join(LOG_BASE_DIR, d)
        for d in os.listdir(LOG_BASE_DIR)
        if os.path.isdir(os.path.join(LOG_BASE_DIR, d))
    ]
    if not subdirs:
        raise FileNotFoundError("no log subdir found")
    latest = sorted(subdirs)[-1]
    csv_path = os.path.join(latest, "_log_messages.csv")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"_log_messages.csv not found in {latest}")
    return csv_path


def import_rows(conn, rows):
    global last_question

    cur = conn.cursor()
    for row in rows:
        ts_iso = row["timestamp"]
        topic = row["topic"]
        msg = row["message"]

        ts_db = parse_ts(ts_iso)
        table = classify_topic(topic)

        # 1) Basistabellen füllen
        cur.execute(
            f"INSERT INTO {table} (ts, topic, message) VALUES (%s, %s, %s)",
            (ts_db, topic, msg),
        )

        # 2) Frage merken
        if topic == "log/quiz/question":
            # neue Frage -> Zeit & Text merken, Status zurücksetzen
            last_question = {"ts": ts_iso, "text": msg}

        # 4) Finale Antwort (Spracherkennung) -> Interaktion speichern
        elif topic == "speech-recognition/statement" and last_question is not None:
            try:
                q_dt = datetime.fromisoformat(last_question["ts"]).replace(tzinfo=None)
                a_dt = datetime.fromisoformat(ts_iso).replace(tzinfo=None)
            except ValueError:
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

    cur.close()


def live_loop():
    conn = connect_db()
    ensure_interactions_table(conn)
    csv_path = get_latest_logfile()
    print(f"[live_to_mariadb] watching: {csv_path}")

    # Initiale Daten
    last_size = os.path.getsize(csv_path)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if rows:
            import_rows(conn, rows)
            print(f"[live_to_mariadb] imported initial {len(rows)} rows")

    # Auf neue Zeilen warten
    while True:
        time.sleep(2)
        try:
            new_size = os.path.getsize(csv_path)
        except FileNotFoundError:
            print("[live_to_mariadb] logfile disappeared, stopping.")
            break

        if new_size > last_size:
            # neuen Teil lesen
            with open(csv_path, "r", encoding="utf-8") as f:
                f.seek(last_size)
                new_part = f.read()

            # Header holen
            with open(csv_path, "r", encoding="utf-8") as fhead:
                header = fhead.readline().strip().split(",")

            new_lines = [l for l in new_part.splitlines() if l.strip()]
            reader = csv.DictReader(new_lines, fieldnames=header)
            rows = list(reader)
            clean_rows = [r for r in rows if r.get("timestamp") and r.get("topic")]
            if clean_rows:
                import_rows(conn, clean_rows)
                print(f"[live_to_mariadb] imported {len(clean_rows)} new rows")
            last_size = new_size


if __name__ == "__main__":
    try:
        live_loop()
    except Exception as e:
        print("[live_to_mariadb] ERROR:", e)
