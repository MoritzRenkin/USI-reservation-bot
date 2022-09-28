# USI-registration-helper

Der USI-reservation-bot kann das Reservieren von Kursen am <a href="https://www.usi.at/">Universitätssportinstituts Wien (USI)</a> automatisieren. Der Bot kann lediglich Reservierungen vornehmen, es werden keine Käufe durch das Programm abgeschlossen.

DISCLAIMER: Die Nutzung dieses Programms verstößt möglicherweise gegen die Nutzungsbedigungen des Universitätssportinstituts. Der enthaltene Code dient rein zu Bildungszwecken und jegliche Art von Ausführung erfolgt auf eigenes Risiko.

## Setup (nur vor der ersten Verwendung)

Der Bot ist als Python Skript entwickelt und benötigt Python 3.9 oder neuer zur Ausführung. Die neueste Python Version kann <a href="https://www.python.org/downloads/">hier</a> heruntergeladen werden.

Die notwendigen Dependencies können über die Commandline (Windows) bzw. Shell (macOS/Linux) wie folgt installiert werden: 

Windows:
```
py -3 -m pip install -r "<Pfad-zum-Projekt>\requirements.txt"
```

macOS/Linux:
```
python3 -m pip install -r "<Pfad-zum-Projekt>/requirements.txt"
```

## Verwendung

Vor dem Ausführen des Bots muss die ``conf.ini`` Datei mit euren Anmeldedaten und den zu reservierenden Kursen befüllt werden. Derzeit wird nur das Login über die Universität Wien unterstützt.

Es ist empfehlenswert, den Bot in der Commandline bzw. Shell zu starten.

Windows:
```
py -3 "<Pfad-zum-Projekt>\usi_reservation_bot.py"
```

macOS/Linux:
```
python3 "<Pfad-zum-Projekt>/usi_reservation_bot"
```

Der Bot verwendet <a href="https://www.selenium.dev/">Selenium</a> Webdriver zur Fernsteuerung des gewählten Browsers. Bei erstmaliger Verwendung des Programms wird der jeweilige Driver heruntergeladen und in ``.wdm`` abgelegt. Möglicherweise kann es hierbei zu Problemen mit der Firewall kommen.
