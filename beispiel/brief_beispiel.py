# -*- coding: utf-8 -*-
"""Beispiel-Bewerbungsschreiben.

Erfundene Person, erfundene Firma. Als Vorlage für eigene Briefe kopieren:

    cp beispiel/brief_beispiel.py beispiel/brief_meinefirma.py

Im Kopf jedes echten Briefes gehört ein kurzer Quellen-Kommentar: welche
Aussage worauf beruht und was bewusst weggelassen wurde. Das zwingt zur
Ehrlichkeit und macht die Bewerbung später nachvollziehbar. Siehe
docs/regeln.md.
"""

BRIEF = {
    # Hintergrundgrafik: bogen, bogen_linie, welle, diagonal oder keine
    "grafik": "bogen_linie",

    "absender": [
        "Andrea Muster",
        "Musterstrasse 1",
        "8000 Musterstadt",
        "Tel. 079 000 00 00",
        "andrea.muster@example.ch",
    ],

    "empfaenger": [
        "Beispiel AG",
        "Personaldienst",
        "Frau Sandra Beispiel",
        "Postfach 100",
        "8000 Musterstadt",
    ],

    "datum": "Musterstadt, 1. März 2026",
    "betreff": "Bewerbung als Sachbearbeiterin Kundendienst 80 %",

    # Optional: Referenz- oder Vakanznummer, erscheint grau rechts im Betreff
    # "stellennummer": "1234",

    "anrede": "Sehr geehrte Frau Beispiel",

    # Vier Absätze plus ein kurzer Schlussabsatz.
    # A1 konkrete Tätigkeit mit persönlicher Note, verankert in einer Station
    # A2 dieselbe Arbeit konkret ausgeführt, mit einem harten Beleg
    # A3 Ausbildung und Werkzeuge
    # A4 Bezug auf die Ausschreibung, Pensum, Eintritt
    # A5 Gesprächswunsch, ein Satz
    "absaetze": [
        "Erste Anlaufstelle zu sein, wenn jemand ein Anliegen hat und nicht weiss, wer "
        "zuständig ist, war bei der Muster Service AG vier Jahre lang meine Arbeit. Am "
        "Telefon und per E-Mail habe ich Auskunft gegeben und das, was ich nicht selbst "
        "abschliessen konnte, an die zuständige Fachstelle übergeben.",

        "Dahinter stand die laufende Administration. Ich habe Aufträge erfasst, Mutationen "
        "ausgeführt, Anfragen zu Rechnungen und Kündigungen bearbeitet und die Stammdaten "
        "gepflegt. Für die Rückmeldungen der Kundschaft wurde ich 2024 als beste Beraterin "
        "meines Teams ausgezeichnet.",

        "Meine kaufmännische Grundbildung habe ich an der Handelsschule abgeschlossen. Mit "
        "Word, Excel und Outlook arbeite ich täglich, und mehrfach habe ich dazu "
        "beigetragen, interne Abläufe zu vereinfachen.",

        "Ihre Ausschreibung nennt den Kundendienst als Drehscheibe zwischen Verkauf und "
        "Logistik. Dass dazu die eigenständige Betreuung eines Kundensegments gehört, ist "
        "für mich der Reiz an dieser Stelle. Das Pensum von 80 % passt mir, und ich kann "
        "per 1. Juni 2026 anfangen.",

        "Ich freue mich auf Ihre Rückmeldung und die Gelegenheit, mich Ihnen persönlich "
        "vorzustellen.",
    ],

    "gruss": "Freundliche Grüsse",
    "signatur": "Andrea Muster",
}
