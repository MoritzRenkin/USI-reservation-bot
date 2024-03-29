# USI-reservation-bot [DEPRECATED] ⛔

Nicht mehr anwendbar nach Umstellung des USI Anmeldesystems!

Der USI-reservation-bot kann das Reservieren von Sportkursen am <a href="https://www.usi.at/" target="_blank">Universitätssportinstitut Wien (USI)</a> automatisieren. Der Bot kann lediglich Reservierungen vornehmen, es werden keine Käufe durch das Programm abgeschlossen.

Hinweis: Das Projekt wurde ausschließlich zu Bildungszwecken entwickelt. Jegliche Art von Ausführung erfolgt auf eigene Verantwortung.

## Setup (nur vor der ersten Verwendung)

Der Bot ist als Python Skript entwickelt und benötigt Python 3.9 oder neuer zur Ausführung. Die neueste Python Version kann <a href="https://www.python.org/downloads/" target="_blank">hier</a> heruntergeladen werden.

Die notwendigen Dependencies können über cmd (Windows) bzw. Terminal (macOS/Linux) installiert werden. Im Ordner des Projekts: 

Windows:
```
py -3 -m pip install -r requirements.txt
```

macOS/Linux:
```
python3 -m pip install -r requirements.txt
```

## Verwendung

Vor dem Ausführen muss der Bot in der Datei ``config.ini`` konfiguriert werden. Vor allem folgende Felder sollten überprüft und ggf. angepasst werden:
* ``login_institution`` Derzeit wird das Login über folgende Institute unterstützt[^institutes][^2factor]: 
  * Technische Universität Wien 
  * Universität Wien
  * Wirschaftsuniversität Wien
  * OpenIdP (alle Anderen)
* ``kurse_semesterbetrieb`` bzw. ``kurse_jahresbetrieb``
* ``browser`` Die neueste Version des Browsers muss installiert sein.
*  ``start`` Der Start der Anmeldungen wird normalerweise auf <a href="https://www.usi.at/de/termine/termine/">usi.at</a> unter Termine angegeben.

Der Bot wird in cmd bzw. Terminal gestartet.

Windows:
```
py -3 usi_reservation_bot.py
```

macOS/Linux:
```
python3 usi_reservation_bot.py
```

Nachdem der Bot alle Reservierungen abgeschlossen hat, muss der Kaufvorgang in dem vom Bot gesteuerten Browser abgeschlossen werden. USI-Reservierungen verfallen ansonsten nach 30 Minuten. Je nach Konfiguration in ``config.ini`` wird ein Alarmton abgespielt, sobald die manuelle Durchführung des Kaufvorgangs erforderlich ist. Der Alarm kann angepasst werden, indem das File ``sounds/alarm.wav``[^mixkit] ersetzt wird. 

Das Programm bzw. der zugehörige Browser dürfen nicht frühzeitig geschlossen werden, da ansonsten die Reservierungen verloren gehen.

Der Bot verwendet <a href="https://www.selenium.dev/">Selenium</a> Webdriver zur Fernsteuerung des gewählten Browsers. Bei erstmaliger Verwendung des Programms wird der jeweilige Driver heruntergeladen und in ``.wdm`` abgelegt. Möglicherweise kann es hierbei zu Warnmeldungen der Firewall kommen.

[^mixkit]: Der inkludierte Alarmton stammt von <a href="https://mixkit.co/free-sound-effects/alarm/" >mixkit.co</a>
[^institutes]: Für andere Login-Institute oder neue Features gerne einen <a href="https://github.com/MoritzRenkin/USI-reservation-bot/issues">Issue erzeugen</a>, oder Projekt forken und selbst hinzufügen (siehe TODO-Element in `` usi_reservation_bot.py ``). Pull requests sind willkommen. 
[^2factor]: 2-Faktor Authentifizierung wird nicht unterstützt. 
