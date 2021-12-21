# Flatex-Documents-Download-Helper

### Danke an
Vielen Dank an User headEx74, siehe https://github.com/headEx74/Flatex-Documents-Download-Helper,
sein Skript bildet die Grundlage für dieses Repository.

:bangbang: Mein Skript bietet folgende zusätzliche Features:
- Automatischer Login
- Kontoauswahl bei mehreren Cashkonten
- Automatische Zeitraumwahl, kein manuelles Einstellen mehr
- Automatisches Downloaden der letzten X Monate im Skript direkt
- Sammlung aller Downloads in eigenem Ordner
- keine Vorkonfiguration vom Browser möglich
- Browserunabhängig
- Direktstart von Chrome, ohne Kommandozeile


Das Skript erlaubt es mittels per Selenium gesteuerten Chrome-Browser PDF-Dokumente aus dem Dokumentenarchiv von Flatex herunterzuladen. 

### Zugangsdaten speichern
Um dem Skript den Login zu ermöglichen, muss in diesem Ordner (gleicher Ordner wie das `.py` Skript) Ordner eine Konfigurationsdatei `credentials.ini` erstellt werden, mit folgendem Inhalt (um persönliche Daten ergänzen):
```
[CONFIGURATION]
kundennummer = 1111111
passwort = meinPasswort
kontonummer_letzte_drei_zeichen = 123
```
Siehe `beispiel-credentials.ini`, einfach die Informationen ändern und die Datei in `credentials.ini` umbenennen.

### Anleitung Verwendung
Skript starten mit 
```python3 flatex_document_downloader.py <months>```
Wobei der parameter `<months>` folgendermaßen eingestellt wird:
Die Anzahl der herunterzuladenden letzten Monate, der aktuelle Monat inbegriffen. Um also nur diesen Monat herunterzuladen, diesen Parameter auf 1 setzen. Für diesen und den letzten Monat den Parameter auf 2 setzen, und so weiter.

Beispiel (lädt den aktuellen Monat und den letzten herunter): 
```python3 flatex_document_downloader.py 2```

### Anleitung Installation

1. Python herunterladen und installieren: https://www.python.org/downloads/
2. Requirements installieren: `pip install -r requirements.txt`
3. Chrome Browser herunterladen: https://www.google.com/chrome/
4. Für Google Chrome: Zur Browser Version passenden Chrome Driver herunterladen
    - Download: https://chromedriver.chromium.org/downloads
    - Den Chrome Driver (also der Ordner, in dem er sich befindet) in den PATH (in den Windows Umgebungsvariablen) 
     eintragen, damit er von Selenium gefunden wird
    - MAC: `brew install chromedriver`