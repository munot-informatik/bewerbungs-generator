# Setup

## Voraussetzungen

Vier Dinge, ohne die nichts läuft: **Python**, **Node.js**, die **Schriften**
und ein Programm, das **.docx** öffnet — Word oder LibreOffice. Der Brief
braucht nur Python, der Lebenslauf nur Node; wer beides erzeugen will, braucht
beides.

### Windows

```powershell
winget install Python.Python.3.13
winget install OpenJS.NodeJS.LTS
winget install TheDocumentFoundation.LibreOffice
```

Die letzte Zeile entfällt, wenn Microsoft Word installiert ist. Danach ein
**neues** Terminalfenster öffnen, sonst sind die Befehle noch nicht im PATH:

```powershell
pip install reportlab pillow
npm.cmd install
```

`npm.cmd` statt `npm`, weil PowerShell das Ausführen von `npm.ps1` blockiert.

**Carlito** wird unter Windows nicht gebraucht: Calibri ist massgleich, liegt
bereits im System und wird automatisch gefunden. **Montserrat** dagegen fehlt
und muss beschafft werden — fünf Schnitte (Light, Regular, Medium, SemiBold,
Bold) bei Google Fonts holen und entweder per Rechtsklick installieren oder
die TTF-Dateien nach `daten/schriften/` legen. Dort sucht
`schriften_einbetten.py` von selbst.

### Debian / Ubuntu

```bash
sudo apt install python3-pip nodejs npm libreoffice-writer \
                 fonts-crosextra-carlito fonts-montserrat
pip install reportlab pillow
npm install
```

### macOS

```bash
brew install python node
brew install --cask libreoffice font-montserrat font-carlito
pip3 install reportlab pillow
npm install
```

### Prüfen, ob alles bereitsteht

```bash
python3 -c "import reportlab, PIL; print('Python bereit')"
node -e "require('docx'); console.log('Node bereit')"
```

Beide Skripte suchen die Schriften an den üblichen Orten für Linux, macOS und
Windows sowie in `daten/schriften/`. Ein eigener Ordner lässt sich über
Umgebungsvariablen vorgeben: `BEWERBUNG_SCHRIFTEN` für das Einbetten,
`BRIEF_SCHRIFT_REGULAR` und `BRIEF_SCHRIFT_BOLD` für den Brief.

---

## Bewerbungsschreiben (Python)

```bash
pip install reportlab pillow
python3 generator/brief_rl.py beispiel/brief_beispiel.py ausgabe/Bewerbung.pdf
```

Mehr braucht es nicht. `brief_rl.py` zeichnet die Seite direkt: Absender,
Empfänger auf 95 mm eingerückt, Betreff in Braun mit feiner Sandlinie,
Fliesstext in Carlito 11 pt, Sandbogen unten rechts, Unterschrift über dem
gedruckten Namen.

**Schrift.** Carlito ist massgleich mit Calibri. Das Skript sucht der Reihe
nach in den Schriftverzeichnissen von Linux, macOS und Windows sowie in
`daten/schriften/` und nimmt unter Windows ersatzweise Calibri. Wird gar
nichts gefunden, bricht es mit einer Meldung ab statt mit einem Traceback. Ein
eigener Pfad lässt sich vorgeben:

```bash
BRIEF_SCHRIFT_REGULAR=/pfad/zu/Carlito-Regular.ttf \
BRIEF_SCHRIFT_BOLD=/pfad/zu/Carlito-Bold.ttf \
python3 generator/brief_rl.py daten/brief.py ausgabe/Bewerbung.pdf
```

**Unterschrift.** Standardmässig wird **keine** eingesetzt: ohne eigenen Scan
setzt das Skript den Namen in einer Handschrift. Das ist Absicht — ein
gezeichneter fremder Schriftzug wäre eine Fälschung, siehe Regel 7 in
[`regeln.md`](regeln.md).

Den eigenen Scan gibt man in den Briefdaten an, freigestellt, mit
transparentem Hintergrund, etwa 360 × 125 px:

```python
BRIEF = {
    "unterschrift": "daten/unterschrift_echt.png",
    ...
}
```

Relative Pfade gelten ab dem Projektordner. Die Breite rechnet das Skript aus
dem Seitenverhältnis selbst aus. Als Handschrift wird Caveat oder Dancing
Script verwendet, unter Windows ersatzweise Segoe Script oder Ink Free; ein
eigener Pfad lässt sich über `BRIEF_SCHRIFT_HAND` vorgeben.

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
und macOS normal installieren. Wer die Schriften nicht systemweit installieren
will, legt die TTF-Dateien nach `daten/schriften/` — für das Einbetten reicht
das, der Ordner ist bereits aus dem Repository ausgeschlossen.

Fehlt Montserrat, erzeugt das Skript trotzdem eine Datei. Word ersetzt die
Schrift dann stillschweigend, und das Layout verschiebt sich, ohne dass eine
Fehlermeldung darauf hinweist. Deshalb der nächste Schritt.

**Foto.** `generator/cv/foto_portrait.png` ist ein Platzhalter. Ersetze ihn
durch ein eigenes Bild im Seitenverhältnis 4:5, etwa 400 × 500 px.

**Schriften einbetten**, damit die Datei auf fremden Rechnern gleich aussieht:

```bash
python3 generator/schriften_einbetten.py ausgabe/CV.docx
```

Das Skript sucht die TTF-Dateien selbst: in `daten/schriften/`, in den
Schriftverzeichnissen von Linux, macOS und Windows, und in einem eigenen
Ordner, wenn `BEWERBUNG_SCHRIFTEN` gesetzt ist. Was es nicht findet, meldet
es namentlich.

Ohne diesen Schritt sieht die Datei nur auf Rechnern richtig aus, auf denen
Montserrat installiert ist — beim Empfänger also vermutlich nicht.

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

Dafür braucht es `poppler-utils`. Unter Windows ist das mühsam zu beschaffen;
dort tut es `pypdfium2`, ein reiner pip-Install ohne Systemabhängigkeiten:

```bash
pip install pypdfium2
python3 -c "import pypdfium2 as p; d=p.PdfDocument('ausgabe/CV.pdf'); print(len(d), 'Seiten'); [d[i].render(scale=2).to_pil().save(f'kontrolle_{i+1}.png') for i in range(len(d))]"
```

Danach die Kontrollbilder wieder löschen.

Worauf beim Ansehen zu achten ist: verrutschte Unterschrift, zerschossene
Umbrüche, eine Überschrift allein am Seitenfuss, und eine zweite Seite, die
nur zu einem Viertel gefüllt ist.

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
