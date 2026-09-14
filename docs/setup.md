# Setup

## Bewerbungsschreiben (Python)

```bash
pip install reportlab pillow
python3 generator/brief_rl.py beispiel/brief_beispiel.py ausgabe/Bewerbung.pdf
```

Mehr braucht es nicht. `brief_rl.py` zeichnet die Seite direkt: Absender,
Empfänger auf 95 mm eingerückt, Betreff in Braun mit feiner Sandlinie,
Fliesstext in Carlito 11 pt, Sandbogen unten rechts, Unterschrift über dem
gedruckten Namen.

**Schrift.** Carlito ist massgleich mit Calibri und liegt unter Linux meist
schon unter `/usr/share/fonts/truetype/crosextra/`. Andernfalls aus dem
LibreOffice-Paket installieren oder im Skript oben den Pfad anpassen:

```python
pdfmetrics.registerFont(TTFont("Carlito", "/pfad/zu/Carlito-Regular.ttf"))
```

**Unterschrift.** `generator/unterschrift.png` ist ein Platzhalter. Ersetze ihn
durch einen Scan der eigenen Unterschrift, freigestellt, mit transparentem
Hintergrund, etwa 360 × 125 px. Die Breite rechnet das Skript aus dem
Seitenverhältnis selbst aus.

---

## Lebenslauf (Node.js)

```bash
npm install
cd generator/cv
node word_cv.js ../../beispiel/cv_beispiel.json ../../ausgabe/CV.docx
```

Einzige Abhängigkeit ist [`docx`](https://docx.js.org/).

**Schriften.** Der Lebenslauf setzt Montserrat in fünf Schnitten voraus:
Regular, Light, Medium, SemiBold, Bold. Kostenlos bei Google Fonts. Unter
Linux nach `~/.fonts/` legen und `fc-cache -f` laufen lassen, unter Windows
und macOS normal installieren.

**Foto.** `generator/cv/foto_portrait.png` ist ein Platzhalter. Ersetze ihn
durch ein eigenes Bild im Seitenverhältnis 4:5, etwa 400 × 500 px.

**Schriften einbetten**, damit die Datei auf fremden Rechnern gleich aussieht:

```bash
python3 generator/schriften_einbetten.py ausgabe/CV.docx
```

Das Skript erwartet die TTF-Dateien an den oben im Skript eingetragenen
Pfaden — dort gegebenenfalls anpassen.

**PDF daraus:**

```bash
libreoffice --headless --convert-to pdf ausgabe/CV.docx
```

---

## Sichtprüfung

Nie ungeprüft verschicken. Beide Dokumente als Bild rendern und anschauen:

```bash
pdfinfo ausgabe/CV.pdf | grep Pages        # Seitenzahl wie erwartet?
pdftoppm -png -r 100 ausgabe/CV.pdf kontrolle
```

Dafür braucht es `poppler-utils`. Danach die Kontrollbilder wieder löschen.

---

## Stolpersteine

**PowerShell blockiert npm.** Unter Windows meldet PowerShell, dass
`npm.ps1` nicht ausgeführt werden darf. Stattdessen `npm.cmd install`
aufrufen — dieselbe Software, andere Hülle, keine Änderung an den
Sicherheitseinstellungen nötig.

**Compress-Archive scheitert an gesperrten Dateien.** Wenn der Virenscanner
`node_modules` gerade durchsieht, bricht das PowerShell-Cmdlet ab. Das
eingebaute `tar` kommt damit klar:

```powershell
tar -a -c -f paket.zip node_modules
```

**Die Word-Datei sieht auf einem anderen Rechner falsch aus.** Fast immer eine
fehlende Schrift, nicht eine falsche Word-Version. Schriften einbetten oder
eine Schrift wählen, die überall vorhanden ist.

**Umgebung ohne Paketinstallation.** Wo sich weder npm noch pip erreichen
lassen, hilft es, `node_modules` einmal anderswo zu erzeugen und als Archiv
mitzuführen. `brief_rl.py` wurde bewusst so gebaut, dass es mit ReportLab
auskommt und keine Systembibliotheken wie bei WeasyPrint benötigt.
