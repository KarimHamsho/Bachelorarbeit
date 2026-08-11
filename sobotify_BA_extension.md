## Erweiterung in `sobotify.py`

### Position

Die Erweiterung befindet sich in der Methode:

```python
sobotify.start_logging_server()
```

Der Block wird nach dem erfolgreichen Start und der Initialisierung des Logging-Servers eingefügt.

### Zweck

Nach dem Start des Logging-Servers wird das Grafana-Dashboard automatisch im Standardbrowser geöffnet.

Dadurch steht die Echtzeit-Analyse unmittelbar beim Start der Anwendung zur Verfügung. Das Dashboard wird mit einem Zeitfenster der letzten zehn Minuten, einer Aktualisierung alle fünf Sekunden und dem vorausgewählten Live-Panel geöffnet.

```python
# BA_MHD_Yosef
import webbrowser

webbrowser.open(
    "http://localhost:3000/d/adg27zv/sobotify_quiz?orgId=1&from=now-10m&to=now&timezone=browser&refresh=5s&viewPanel=panel-2"
)
```

### Ergebnis

Beim Start des Logging-Servers wird Grafana automatisch geöffnet, sodass neu eintreffende und in MariaDB gespeicherte Interaktionsdaten direkt im Dashboard beobachtet werden können.
