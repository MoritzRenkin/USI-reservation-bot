# USI-registration-bot

Der USI-reservation-bot kann das Reservieren von Kursen am <a href="https://www.usi.at/" target="_blank">Universitätssportinstitut Wien (USI)</a> automatisieren. Der Bot kann lediglich Reservierungen vornehmen, es werden keine Käufe durch das Programm abgeschlossen.

Hinweis: Die Nutzung dieses Programms verstößt möglicherweise gegen die Nutzungsbedigungen des Universitätssportinstituts. Der enthaltene Code dient rein zu Bildungszwecken und jegliche Art von Ausführung erfolgt auf eigenes Risiko.

## Setup (nur vor der ersten Verwendung)

Der Bot ist als Python Skript entwickelt und benötigt Python 3.9 oder neuer zur Ausführung. Die neueste Python Version kann <a href="https://www.python.org/downloads/" target="_blank">hier</a> heruntergeladen werden.

Die notwendigen Dependencies können über den Command Prompt (Windows) bzw. Terminal (macOS/Linux) wie folgt installiert werden: 

Windows:
```
py -3 -m pip install -r "<Pfad-zum-Projekt>\requirements.txt"
```

macOS/Linux:
```
python3 -m pip install -r "<Pfad-zum-Projekt>/requirements.txt"
```

## Verwendung

Vor dem Ausführen des Bots muss ``config.ini`` mit euren Anmeldedaten und den zu reservierenden Kursen befüllt werden. Derzeit wird das Login über folgende Institute unterstützt: 
* Technische Universität Wien 
* Universität Wien
* OpenIdP (alle Anderen)

Für andere Institute gerne bei mir melden oder selbst hinzufügen (siehe TODO-Element in `` usi_reservation_bot.py ``)

Es ist empfehlenswert, den Bot im Command Prompt bzw. Terminal zu starten.

Windows:
```
py -3 "<Pfad-zum-Projekt>\usi_reservation_bot.py"
```

macOS/Linux:
```
python3 "<Pfad-zum-Projekt>/usi_reservation_bot.py"
```

Der Bot verwendet <a href="https://www.selenium.dev/">Selenium</a> Webdriver zur Fernsteuerung des gewählten Browsers. Bei erstmaliger Verwendung des Programms wird der jeweilige Driver heruntergeladen und in ``.wdm`` abgelegt. Möglicherweise kann es hierbei zu Problemen mit der Firewall kommen.

Nachdem der Bot alle Reservierungen abgeschlossen hat, muss der Kaufvorgang in dem vom Bot gesteuerten Browser abgeschlossen werden. Je nach Konfiguration in ``config.ini`` wird ein Alarm abgespielt, sobald die manuelle Durchführung des Kaufvorgangs erforderlich ist. Der Alarm kann angepasst werden, indem das File ``sounds/alarm.wav`` ersetzt wird. USI-Reservierungen verfallen überlichweise nach 30 Minuten, wenn der Kaufvorgang nicht abgeschlossen wird.

Das Programm bzw. der zugehörige Browser dürfen nicht frühzeitig geschlossen werden, da ansonsten die Reservierungen verloren gehen.
