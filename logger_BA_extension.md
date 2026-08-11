# Erweiterungen in `logger.py`

Die Datei `logger.py` ist Bestandteil des bestehenden Sobotify-Frameworks und wurde nicht vollständig im Rahmen dieser Bachelorarbeit entwickelt.

Für die Bachelorarbeit wurde der vorhandene Logger lediglich um eine direkte Anbindung an MariaDB erweitert.  
Die ursprüngliche CSV-Protokollierung bleibt dabei erhalten.

Die folgenden Codeabschnitte zeigen ausschließlich die vorgenommenen Erweiterungen und ihre Position innerhalb der ursprünglichen `logger.py`.

---

## 1. Import des Live-Datenbankmoduls

### Position

Im Importbereich am Anfang von `logger.py`.

### Zweck

Das Modul `live_to_mariadb.py` übernimmt die Verarbeitung und Speicherung der vom Logger empfangenen MQTT-Nachrichten in MariaDB.

```python
from sobotify.tools.analysing import live_to_mariadb

---

## 2. Aufbau der MariaDB-Verbindung

### Position

In der Methode:
```python
LoggerServer.__init__()
Der Block wird nach der Initialisierung der CSV-Logdatei und vor
```python
self.mqtt_client.publish("logging_server/status/init-done")
eingefügt

### Zweck

Beim Start des Logging-Servers wird einmalig eine Verbindung zur MariaDB-Datenbank aufgebaut.
Falls die Verbindung nicht hergestellt werden kann, bleibt der ursprüngliche CSV-Logger weiterhin funktionsfähig.
```python
# BA-Erweiterung: DB-Verbindung für Direkt-Import
try:
    self.db_conn = live_to_mariadb.connect_db()
    live_to_mariadb.ensure_interactions_table(self.db_conn)
    print("[logger] Connected to MariaDB for live import.")
except Exception as e:
    print("[logger] WARNING: could not connect to MariaDB:", e)
    self.db_conn = None
## 3. Direkter Import eingehender MQTT-Nachrichten
### Position
In der Methode:
```python
LoggerServer.process_message()

innerhalb des bestehenden else-Blocks für nicht ignorierte MQTT-Nachrichten.

### Zweck

Die empfangene MQTT-Nachricht wird zunächst wie bisher in die CSV-Logdatei geschrieben.

Zusätzlich wird dieselbe Nachricht unmittelbar an live_to_mariadb.py übergeben und dort in MariaDB gespeichert. Dadurch stehen die Daten bereits während eines laufenden Experiments für die Analyse zur Verfügung.
```python
# BA-Erweiterung

# Bytes → String
try:
    msg_text = message.decode("utf-8")
except Exception:
    msg_text = str(message)

# Wie bisher in CSV schreiben
ts = self.store_message(msg_text, topic)

# Zusätzlich direkt in MariaDB schreiben
if self.db_conn is not None:
    try:
        row = {
            "timestamp": ts,
            "topic": topic,
            "message": msg_text,
        }
        live_to_mariadb.import_rows(self.db_conn, [row])
    except Exception as e:
        print("[logger] DB import error:", e)

## Ergebnis

Durch diese Erweiterung besitzt der Logger zwei parallele Datenwege:

Speicherung der MQTT-Nachrichten in der bestehenden CSV-Logdatei.
Direkte Weitergabe der Nachrichten an live_to_mariadb.py zur Speicherung in MariaDB.

Der ursprüngliche Aufbau und die weiteren Funktionen von logger.py wurden nicht im Rahmen dieser Bachelorarbeit entwickelt.
