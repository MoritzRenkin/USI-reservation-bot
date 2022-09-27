#USI-registration-helper

Der USI-reservation-bot kann das Reservieren von Kursen am <a href="https://www.usi.at/">Universitätssportinstituts Wien (USI)</a> automatisieren. Der Bot kann lediglich Reservierungen vornehmen, es werden keine Käufe durch das Programm abgeschlossen.

DISCLAIMER: Die Nutzung dieses Programms verstößt möglicherweise gegen die Nutzungsbedigungen des Universitätssportinstituts. Der enthaltene Code dient rein zu Bildungszwecken und jede Nutzung erfolgt auf eigene Gefahr.

##Setup (nur vor der ersten Verwendung)

Der Bot ist als Python Skript entwickelt und benötigt Python 3.9 oder neuer zur Ausführung. Die neueste Python Version kann <a href="https://www.python.org/downloads/">hier</a> heruntergeladen werden.
Die notwendigen Dependencies können mittels Commandline (Windows) bzw. Shell (Mac OSX/Linux) wie folgt installiert werden: 
```
pip install -r <Pfad-zum-Projekt>/requirements.txt
```

##Verwendung

Vor dem Ausführen des Bots muss die ``conf.ini`` Datei mit euren Anmeldedaten und den zu reservierenden Kursen befüllt werden. Derzeit wird nur das Login über die Universität Wien unterstützt.

Der Bot wird in der Commandline bzw. Shell gestartet:
```
python3 <Pfad-zum-Projekt>/usi_reservation_bot.py
```

Der Bot verwendet <a href="https://www.selenium.dev/">Selenium</a> Webdriver ferngesteuerten Benutzung des gewählten Browsers. Bei erstmaliger Verwendung des Programms wird der jeweilige Driver heruntergeladen und in ``.wdm`` abgelegt. Möglicherweise kann es hierbei zu Problemen mit der Firewall kommen.
