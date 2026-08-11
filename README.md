Dieses Paket enthält alle im Rahmen der Bachelorarbeit
„Entwicklung und Umsetzung eines Sys-tems zur Speicherung und Analyse von Daten in sozialen Robotik-Anwendungen" des Sobotify-Frameworks
erstellt en Skripte, SQL-Definitionen und Dashboard-Dateien.

**Inhalt der ZIP-Datei

Python-Module

db_init.py – Initialisierung der MariaDB-Datenbank

mqtt_to_mariadb.py – Import historischer CSV-Logdaten

live_to_mariadb.py – Live-Datenimport über den Logger

Dashboard

sobotify_quiz.json – vollständige Grafana-Dashboarddefinition

SQL

sobotify_data_structure.sql – Export der Datenbankstruktur (ohne Daten)

Konfiguration

.env.example – Beispiel für die Umgebungsvariablen (ohne Passwort)

Sonstiges

LICENSE – MIT-Lizenz für alle im Projekt enthaltenen Dateien

README – diese Datei

**Voraussetzungen

Python 3.10+

MariaDB 11+

Grafana 10+

MQTT-Broker (z. B. Eclipse Mosquitto)

**Kurzanleitung

Datenbank einrichten:

python db_init.py


Historische Logdaten importieren:

python mqtt_to_mariadb.py


Live-Datenimport starten:

python live_to_mariadb.py


Grafana öffnen und das Dashboard sobotify_quiz.json importieren.

**Lizenz

Alle Dateien stehen unter der MIT-Lizenz (siehe LICENSE)
