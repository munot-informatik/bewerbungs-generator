# -*- coding: utf-8 -*-
"""
Unterlagen durchsuchbar machen
==============================

Aufruf:  python scripts/unterlagen_lesen.py <datei-oder-ordner> [...] [-o unterlagen.txt]

Liest ein Bewerbungsdossier Seite für Seite aus und schreibt alles in eine
Textdatei. Gedacht als erster Schritt, bevor ein Lebenslauf zugeschnitten wird.

Warum das nötig ist: Der gepflegte Lebenslauf ist selten die ganze Wahrheit.
Arbeitszeugnisse, Diplome und Kursbestätigungen im Dossier enthalten regelmässig
Belege, die im Lebenslauf fehlen — eine Beurteilung der Arbeitsweise, eine
Tätigkeit, die damals nebensächlich schien, eine Weiterbildung, die man
vergessen hat. Nach docs/regeln.md sind das zulässige Quellen. Man muss sie nur
zuerst gelesen haben.

Das Skript meldet ausserdem zwei Dinge, die sonst niemandem auffallen:

  Seiten ohne Textebene. Eingescannte Zeugnisse sind Bilder. Weder dieses
  Skript noch ein Bewerbermanagementsystem liest sie. Sie müssen von Hand
  erfasst oder durch eine OCR geschickt werden.

  Durcheinandergeratene Spalten. Läuft der ausgelesene Text eines
  zweispaltigen Lebenslaufs ineinander, liest ihn eine Maschine genauso. Das
  ist ein Befund über den Lebenslauf, kein Fehler des Skripts.

Unterstützt .pdf, .docx, .txt und .md. Für PDF wird pypdfium2 benötigt.
"""

import re
import sys
import zipfile
from pathlib import Path

ENDUNGEN = {".pdf", ".docx", ".txt", ".md"}


def docx_text(pfad):
    """Fliesstext aus einer .docx-Datei, Absätze zeilenweise."""
    with zipfile.ZipFile(pfad) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    text = re.sub(r"</w:p>", "\n", xml)
    text = re.sub(r"<w:tab[^>]*/>", "\t", text)
    text = re.sub(r"<[^>]+>", "", text)
    for roh, klar in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'")):
        text = text.replace(roh, klar)
    return [z for z in (zeile.rstrip() for zeile in text.split("\n")) if z.strip()]


def pdf_seiten(pfad):
    """Text je Seite. Leere Einträge sind Seiten ohne Textebene."""
    try:
        import pypdfium2 as pdfium
    except ImportError:
        sys.exit(
            "Für PDF-Dateien wird pypdfium2 benötigt:\n"
            "    pip install pypdfium2"
        )
    dok = pdfium.PdfDocument(str(pfad))
    seiten = []
    for i in range(len(dok)):
        seiten.append(dok[i].get_textpage().get_text_range().strip())
    return seiten


def sammeln(pfade):
    """Alle unterstützten Dateien aus Dateien und Ordnern einsammeln."""
    gefunden = []
    for eintrag in pfade:
        p = Path(eintrag).expanduser()
        if p.is_dir():
            gefunden += sorted(k for k in p.rglob("*") if k.suffix.lower() in ENDUNGEN)
        elif p.is_file():
            gefunden.append(p)
        else:
            print(f"Übersprungen, nicht gefunden: {p}")
    return gefunden


def main():
    argumente = sys.argv[1:]
    if not argumente:
        sys.exit(
            "Aufruf: python scripts/unterlagen_lesen.py <datei-oder-ordner> [...] "
            "[-o unterlagen.txt]\n"
            "Beispiel: python scripts/unterlagen_lesen.py ~/Bewerbung/Dossier.pdf"
        )

    ziel = Path("unterlagen.txt")
    if "-o" in argumente:
        i = argumente.index("-o")
        if i + 1 >= len(argumente):
            sys.exit("Nach -o fehlt der Dateiname.")
        ziel = Path(argumente[i + 1])
        del argumente[i:i + 2]

    dateien = sammeln(argumente)
    if not dateien:
        sys.exit("Keine lesbaren Unterlagen gefunden. Unterstützt: " + ", ".join(sorted(ENDUNGEN)))

    teile = []
    bildseiten = []
    seiten_gesamt = 0
    seiten_mit_text = 0

    for datei in dateien:
        teile.append(f"\n\n{'=' * 70}\nDATEI: {datei.name}\n{'=' * 70}")
        endung = datei.suffix.lower()

        if endung == ".pdf":
            seiten = pdf_seiten(datei)
            for nummer, text in enumerate(seiten, 1):
                seiten_gesamt += 1
                if text:
                    seiten_mit_text += 1
                    teile.append(f"\n----- Seite {nummer} -----\n{text}")
                else:
                    bildseiten.append(f"{datei.name} Seite {nummer}")
                    teile.append(f"\n----- Seite {nummer}: ohne Textebene (Scan) -----")
        elif endung == ".docx":
            seiten_gesamt += 1
            seiten_mit_text += 1
            teile.append("\n" + "\n".join(docx_text(datei)))
        else:
            seiten_gesamt += 1
            seiten_mit_text += 1
            teile.append("\n" + datei.read_text(encoding="utf-8", errors="replace"))

    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text("".join(teile).lstrip(), encoding="utf-8")

    print(f"\n{len(dateien)} Datei(en) gelesen, {seiten_gesamt} Seite(n).")
    print(f"Mit Text: {seiten_mit_text}. Geschrieben nach: {ziel}")

    if bildseiten:
        print(f"\nOhne Textebene, also für Mensch und Maschine unlesbar: {len(bildseiten)}")
        for eintrag in bildseiten[:15]:
            print(f"  {eintrag}")
        if len(bildseiten) > 15:
            print(f"  ... und {len(bildseiten) - 15} weitere")
        print(
            "\nDiese Seiten sind Bilder. Was darin steht, muss von Hand erfasst\n"
            "oder durch eine OCR geschickt werden, sonst geht der Inhalt verloren."
        )

    print(
        "\nNächster Schritt: die Textdatei durchgehen und notieren, was darin\n"
        "belegt ist und im Lebenslauf fehlt. Der Ablauf steht in docs/unterlagen.md."
    )


if __name__ == "__main__":
    main()
