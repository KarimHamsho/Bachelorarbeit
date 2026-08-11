# Sobotify – Speicherung und Analyse von Interaktionsdaten

Dieses Repository enthält die im Rahmen der Bachelorarbeit

**„Entwicklung und Umsetzung eines Systems zur Speicherung und Analyse von Daten in sozialen Robotik-Anwendungen“**

entwickelten Erweiterungen für das **Sobotify-Framework**.

Ziel der Erweiterung ist die strukturierte Speicherung von MQTT-basierten Interaktionsdaten in einer MariaDB-Datenbank sowie deren anschließende Analyse und Visualisierung mit Grafana.

Die entwickelte Lösung unterstützt zwei Datenwege:

- **Offline-Import:** Import bereits vorhandener CSV-Logdateien
- **Live-Datenverarbeitung:** direkte Weitergabe neuer MQTT-Nachrichten vom Sobotify-Logger an MariaDB

---

## Inhalt des Repositorys

### Python-Module

- `db_init.py`  
  Initialisierung der MariaDB-Datenbank und Einrichtung des Datenbankbenutzers.

- `mqtt_to_mariadb.py`  
  Import historischer `_log_messages.csv`-Dateien aus dem Sobotify-Logverzeichnis in MariaDB.

- `live_to_mariadb.py`  
  Verarbeitung und Speicherung neuer Log-Nachrichten während des laufenden Sobotify-Betriebs.

### Erweiterungen bestehender Sobotify-Module

Die Dateien `logger.py` und `sobotify.py` gehören zum bestehenden Sobotify-Framework und wurden nicht vollständig im Rahmen dieser Bachelorarbeit entwickelt.

Aus diesem Grund werden im Repository nur die für die Bachelorarbeit vorgenommenen Erweiterungen dokumentiert.

- `logger_BA_extension.md`  
  Dokumentiert die Erweiterung des vorhandenen Sobotify-Loggers um die direkte Weitergabe eingehender MQTT-Nachrichten an `live_to_mariadb.py`.

- `sobotify_BA_extension.md`  
  Dokumentiert die Erweiterung zum automatischen Öffnen des Grafana-Dashboards beim Start des Logging-Servers.

### Grafana-Dashboard

- `sobotify_quiz.json`  
  Vollständige Definition des im Rahmen der Bachelorarbeit entwickelten Grafana-Dashboards.

### SQL

- `sobotify_data_structure.sql`  
  Export der verwendeten MariaDB-Datenbankstruktur ohne gespeicherte Mess- oder Interaktionsdaten.

### Konfiguration

- `.env.example`  
  Beispielkonfiguration für die benötigten Umgebungsvariablen.

  Die tatsächliche `.env`-Datei mit Zugangsdaten und Passwort sollte **nicht in das Git-Repository aufgenommen werden**.

### Sonstiges

- `LICENSE`  
  Lizenzinformationen für die im Rahmen dieses Repositorys bereitgestellten Dateien.

- `README.md`  
  Beschreibung des Projekts, der Installation und der Verwendung.

---

## Einbindung in das Sobotify-Projekt

Die Analyse-Module werden innerhalb des bestehenden Sobotify-Projekts im Verzeichnis

```text
sobotify/tools/analysing/
```

abgelegt.

Eine mögliche Projektstruktur sieht beispielsweise so aus:

```text
sobotify-main/
│
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
│
├── dashboard/
│   └── sobotify_quiz.json
│
├── sql/
│   └── sobotify_data_structure.sql
│
├── docs/
│   ├── logger_BA_extension.md
│   └── sobotify_BA_extension.md
│
└── sobotify/
    │
    ├── sobotify.py
    │
    └── tools/
        │
        ├── logger.py
        │
        └── analysing/
            ├── __init__.py
            ├── db_init.py
            ├── mqtt_to_mariadb.py
            └── live_to_mariadb.py
```

Die Position von `live_to_mariadb.py` ist insbesondere für den folgenden Import im erweiterten Logger relevant:

```python
from sobotify.tools.analysing import live_to_mariadb
```

Die vorhandenen Dateien `logger.py` und `sobotify.py` des Sobotify-Frameworks werden dabei lediglich um die in den entsprechenden Markdown-Dateien dokumentierten BA-Erweiterungen ergänzt.

---

## Voraussetzungen

Für die Verwendung der Erweiterung werden benötigt:

- bestehende Sobotify-Installation
- Python 3.10 oder neuer
- MariaDB
- Grafana
- MQTT-Broker, z. B. Eclipse Mosquitto
- Python-Paket `PyMySQL`
- Python-Paket `python-dotenv`

Die benötigten Python-Pakete können beispielsweise mit folgendem Befehl installiert werden:

```bash
python -m pip install pymysql python-dotenv
```

Die weiteren Abhängigkeiten des Sobotify-Frameworks müssen entsprechend der Sobotify-Installation vorhanden sein.

---

## Konfiguration

Die Datei `.env.example` dient als Vorlage für die lokale Datenbankkonfiguration.

Beispiel:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sobotify_data
DB_USER=sobouser
DB_PASS=DEIN_PASSWORT
```

Für den lokalen Betrieb wird daraus eine Datei mit dem Namen

```text
.env
```

erstellt und das gewünschte Passwort eingetragen.

Die Datei `.env` enthält Zugangsdaten und sollte deshalb nicht in Git aufgenommen werden.

Eine entsprechende `.gitignore` sollte mindestens folgenden Eintrag enthalten:

```gitignore
.env
```

---

## Kurzanleitung

### 1. MariaDB starten

Vor der Verwendung muss der MariaDB-Server gestartet sein.

---

### 2. Datenbank einrichten

Bei der ersten Einrichtung wird `db_init.py` ausgeführt:

```bash
python db_init.py
```

Das Skript richtet die für die Analyse verwendete MariaDB-Datenbank und den Datenbankbenutzer ein.

Dieser Schritt ist normalerweise nur bei der ersten Einrichtung erforderlich.

---

### 3. Historische Logdaten importieren

Bereits vorhandene Sobotify-Logdateien können mit

```bash
python mqtt_to_mariadb.py
```

importiert werden.

Das Skript durchsucht das Sobotify-Logverzeichnis

```text
~/.sobotify/log/
```

nach vorhandenen `_log_messages.csv`-Dateien und überträgt deren Inhalte in MariaDB.

Dieser Import ist für die Analyse bereits abgeschlossener Quiz- und Interaktionsdurchläufe vorgesehen.

---

### 4. Live-Datenverarbeitung

Im normalen Sobotify-Live-Betrieb muss `live_to_mariadb.py` **nicht zusätzlich separat gestartet werden**, wenn die Erweiterung in `logger.py` eingebunden wurde.

Der Logger übergibt jede neue Nachricht direkt an:

```python
live_to_mariadb.import_rows(...)
```

Der Datenfluss lautet damit:

```text
MQTT
  ↓
Sobotify Logger
  ├──→ CSV-Logdatei
  │
  └──→ live_to_mariadb.py
           ↓
        MariaDB
           ↓
        Grafana
```

Die vorhandene CSV-Protokollierung bleibt dadurch weiterhin erhalten und wird lediglich um den direkten Datenbankimport ergänzt.

`live_to_mariadb.py` kann für Entwicklungs- oder Testzwecke auch eigenständig verwendet werden. Im normalen Live-Betrieb sollte jedoch vermieden werden, gleichzeitig den direkten Logger-Import und einen zusätzlichen Import derselben Logdaten auszuführen, da ansonsten doppelte Datenbankeinträge entstehen können.

---

## Grafana einrichten

Nach der Einrichtung der Datenbank wird MariaDB in Grafana als Datenquelle konfiguriert.

Beispiel:

```text
Type:     MySQL
Host:     127.0.0.1:3306
Database: sobotify_data
User:     sobouser
```

Das zugehörige Passwort entspricht der lokalen `.env`-Konfiguration.

Anschließend kann das Dashboard

```text
dashboard/sobotify_quiz.json
```

über die Import-Funktion von Grafana geladen werden.

---

## Echtzeit-Dashboard

Im Rahmen der Bachelorarbeit wurde `sobotify.py` um einen kleinen Aufruf erweitert, durch den das Grafana-Dashboard nach dem Start des Logging-Servers automatisch im Browser geöffnet wird.

Das Dashboard verwendet standardmäßig:

- ein Zeitfenster der letzten 10 Minuten
- automatische Aktualisierung alle 5 Sekunden
- das vorausgewählte Live-Panel zur Darstellung der Quizinteraktionen

Die genaue Erweiterung ist in

```text
docs/sobotify_BA_extension.md
```

dokumentiert.

---

## Speicherung der Daten

Die MQTT-Nachrichten werden entsprechend ihres Topics unterschiedlichen Tabellen zugeordnet.

Zu den verwendeten Tabellen gehören unter anderem:

```text
robot_speak
human_speak
robot_reaction
settings_robot
settings_human
logging_meta
quiz_interactions
```

Die Tabelle `quiz_interactions` enthält rekonstruierte Frage-Antwort-Paare und die daraus berechnete Antwortlatenz.

Die Rohdaten bleiben zusätzlich über die ursprünglichen CSV-Logdateien von Sobotify erhalten.

---

## Sicherheit

Passwörter oder andere Zugangsdaten sollten niemals direkt in das Repository geschrieben werden.

Insbesondere sollte folgende Datei nicht veröffentlicht werden:

```text
.env
```

Stattdessen wird ausschließlich die Vorlage

```text
.env.example
```

bereitgestellt.

Falls Zugangsdaten versehentlich bereits in einen öffentlichen Git-Commit aufgenommen wurden, sollte das betreffende Passwort geändert werden.

---

## Hinweise zum ursprünglichen Sobotify-Code

Sobotify ist ein bestehendes Framework.

Die im Rahmen dieser Bachelorarbeit vorgenommenen Änderungen an bestehenden Framework-Dateien beschränken sich auf kleine Erweiterungen für:

1. die direkte Speicherung der Logger-Nachrichten in MariaDB,
2. das automatische Öffnen des Grafana-Dashboards.

Die vollständigen Framework-Dateien `logger.py` und `sobotify.py` werden deshalb in diesem Repository nicht als eigenständig entwickelte Bestandteile der Bachelorarbeit dargestellt.

Die vorgenommenen Änderungen sind separat dokumentiert, sodass klar zwischen dem ursprünglichen Sobotify-Code und den im Rahmen der Bachelorarbeit entwickelten Erweiterungen unterschieden werden kann.

---

## Lizenz

Die in diesem Repository im Rahmen der Bachelorarbeit bereitgestellten eigenen Dateien stehen unter der MIT-Lizenz, siehe:

```text
LICENSE
```

Für Bestandteile des ursprünglichen Sobotify-Frameworks gelten die jeweiligen Lizenzbedingungen des Sobotify-Projekts.
