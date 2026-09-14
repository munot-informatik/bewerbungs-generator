# -*- coding: utf-8 -*-
"""Bewerbungsschreiben als PDF – Renderer auf Basis von ReportLab.

Hintergrund: In dieser Umgebung lassen sich keine Pakete nachinstallieren,
WeasyPrint fehlt. Dieses Skript erzeugt dasselbe Layout wie brief.py/
brief_style.css, aber direkt mit ReportLab: Geschäftsbrief in Carlito 11 pt,
Empfänger auf 95 mm eingerückt, Betreff braun mit feiner Sandlinie,
Sandbogen unten rechts, Unterschrift über dem gedruckten Namen.

Aufruf:  python3 brief_rl.py <brief_daten.py> <ausgabe.pdf>
"""

import importlib.util
import os
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

BASE = Path(__file__).parent

SAND = HexColor("#D8BFA0")
BRAUN = HexColor("#64493E")
GRAU = HexColor("#6E6E6E")
SCHWARZ = HexColor("#000000")

SCHRIFT = "Carlito"
GROESSE = 11
ZEILE = 14.9                      # line-height aus brief_style.css
RAND_O, RAND_R, RAND_U, RAND_L = 21 * mm, 25 * mm, 20 * mm, 25 * mm
BREITE, HOEHE = A4
TEXTBREITE = BREITE - RAND_L - RAND_R
EINZUG = 95 * mm                  # Empfängerblock

def schrift_suchen(kandidaten):
    """Erste tatsächlich vorhandene Schriftdatei aus der Liste zurückgeben."""
    for eintrag in kandidaten:
        if not eintrag:
            continue
        pfad = Path(eintrag).expanduser()
        if pfad.is_file():
            return str(pfad)
    return None


# Carlito ist massgleich mit Calibri. Deshalb darf unter Windows Calibri
# einspringen, ohne dass sich das Layout verschiebt. Eigene Pfade lassen sich
# über BRIEF_SCHRIFT_REGULAR und BRIEF_SCHRIFT_BOLD vorgeben.
SCHRIFT_REGULAR = schrift_suchen([
    os.environ.get("BRIEF_SCHRIFT_REGULAR"),
    "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf",
    "/usr/share/fonts/truetype/carlito/Carlito-Regular.ttf",
    "~/.fonts/Carlito-Regular.ttf",
    "~/Library/Fonts/Carlito-Regular.ttf",
    "/Library/Fonts/Carlito-Regular.ttf",
    r"C:\Windows\Fonts\Carlito-Regular.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
])
SCHRIFT_BOLD = schrift_suchen([
    os.environ.get("BRIEF_SCHRIFT_BOLD"),
    "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
    "/usr/share/fonts/truetype/carlito/Carlito-Bold.ttf",
    "~/.fonts/Carlito-Bold.ttf",
    "~/Library/Fonts/Carlito-Bold.ttf",
    "/Library/Fonts/Carlito-Bold.ttf",
    r"C:\Windows\Fonts\Carlito-Bold.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
])

if not SCHRIFT_REGULAR or not SCHRIFT_BOLD:
    sys.exit(
        "Schrift nicht gefunden.\n"
        "Carlito installieren (im LibreOffice-Paket enthalten oder bei Google "
        "Fonts) oder die Pfade über die Umgebungsvariablen "
        "BRIEF_SCHRIFT_REGULAR und BRIEF_SCHRIFT_BOLD setzen.\n"
        "Details in docs/setup.md."
    )

pdfmetrics.registerFont(TTFont(SCHRIFT, SCHRIFT_REGULAR))
pdfmetrics.registerFont(TTFont(SCHRIFT + "-Bold", SCHRIFT_BOLD))

# Handschrift für den Namenszug, wenn kein eigener Unterschriften-Scan
# vorliegt. Bewusst keine gezeichnete Unterschrift: ein fremder Schriftzug
# unter einem Brief wäre eine Fälschung.
SCHRIFT_HAND = schrift_suchen([
    os.environ.get("BRIEF_SCHRIFT_HAND"),
    BASE.parent / "daten" / "schriften" / "Caveat-Regular.ttf",
    BASE.parent / "daten" / "schriften" / "DancingScript-Regular.ttf",
    "~/.fonts/Caveat-Regular.ttf",
    "/usr/share/fonts/truetype/google-fonts/Caveat-Regular.ttf",
    "/usr/share/fonts/truetype/google-fonts/DancingScript-Regular.ttf",
    "~/Library/Fonts/Caveat-Regular.ttf",
    r"C:\Windows\Fonts\segoesc.ttf",
    r"C:\Windows\Fonts\Inkfree.ttf",
])
HANDSCHRIFT = "Handschrift" if SCHRIFT_HAND else None
if SCHRIFT_HAND:
    pdfmetrics.registerFont(TTFont(HANDSCHRIFT, SCHRIFT_HAND))


def umbrechen(c, text, breite, fett=False):
    """Text auf die gegebene Breite umbrechen."""
    font = SCHRIFT + "-Bold" if fett else SCHRIFT
    worte, zeilen, aktuell = text.split(), [], ""
    for w in worte:
        probe = (aktuell + " " + w).strip()
        if c.stringWidth(probe, font, GROESSE) <= breite:
            aktuell = probe
        else:
            if aktuell:
                zeilen.append(aktuell)
            aktuell = w
    if aktuell:
        zeilen.append(aktuell)
    return zeilen


def _flaeche(c, deckung, form):
    """Eine blasse Sandfläche zeichnen. form() beschreibt den Pfad."""
    c.saveState()
    c.setFillColor(SAND)
    c.setFillAlpha(deckung)
    p = c.beginPath()
    form(p)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def bogen(c):
    """Drei ineinanderliegende Viertelkreise in der unteren rechten Ecke."""
    for radius, deckung in ((331, 0.09), (221, 0.11), (123, 0.16)):
        def form(p, r=radius):
            p.moveTo(BREITE, 0)
            p.lineTo(BREITE, r)
            # Viertelkreis um die Blattecke (BREITE, 0): von (BREITE, r)
            # nach (BREITE - r, 0).
            p.arcTo(BREITE - r, -r, BREITE + r, r, 90, 90)
        _flaeche(c, deckung, form)


def welle(c):
    """Flache Welle über die gesamte untere Blattkante."""
    # Alle Werte sind Abstände von der Unterkante, umgerechnet aus den
    # SVG-Pfaden in grafik.py (dort zählt y von oben).
    formen = (
        (0.09, 79.89, (150, 141.89), (330, 35.89), 173.89),
        (0.13, 29.89, (170, 79.89), (360, -6.11), 99.89),
    )
    for deckung, start, s1, s2, ende in formen:
        def form(p, start=start, s1=s1, s2=s2, ende=ende):
            p.moveTo(0, 0)
            p.lineTo(0, start)
            p.curveTo(s1[0], s1[1], s2[0], s2[1], BREITE, ende)
            p.lineTo(BREITE, 0)
        _flaeche(c, deckung, form)


def diagonal(c):
    """Weiche Diagonale von unten rechts gegen die Blattmitte."""
    for deckung, hoehe, links in ((0.08, 469.89, 232), (0.11, 275.89, 358), (0.16, 110.89, 484)):
        def form(p, h=hoehe, l=links):
            p.moveTo(BREITE, 0)
            p.lineTo(BREITE, h)
            p.lineTo(l, 0)
        _flaeche(c, deckung, form)


# "bogen_linie" teilt die Form mit "bogen"; sie unterscheiden sich nur in der
# Auszeichnung des Betreffs, nicht im Hintergrund.
GRAFIKEN = {
    "bogen": bogen,
    "bogen_linie": bogen,
    "welle": welle,
    "diagonal": diagonal,
    "keine": None,
}


class Stift:
    """Schreibt von oben nach unten und merkt sich die Position."""

    def __init__(self, c):
        self.c = c
        self.y = HOEHE - RAND_O

    def abstand(self, punkte):
        self.y -= punkte

    def zeile(self, text, x=RAND_L, fett=False, farbe=SCHWARZ, groesse=GROESSE):
        font = SCHRIFT + "-Bold" if fett else SCHRIFT
        self.c.setFont(font, groesse)
        self.c.setFillColor(farbe)
        self.c.drawString(x, self.y - groesse, text)
        self.y -= ZEILE

    def block(self, zeilen, x=RAND_L, ersteFett=False):
        for i, z in enumerate(zeilen):
            fett = ersteFett and i == 0
            self.zeile(z, x=x, fett=fett, farbe=BRAUN if fett else SCHWARZ)

    def absatz(self, text, breite=TEXTBREITE, x=RAND_L):
        for z in umbrechen(self.c, text, breite):
            self.zeile(z, x=x)


def zeichnen(b, ziel):
    c = rl_canvas.Canvas(str(ziel), pagesize=A4)
    c.setTitle(b["betreff"])
    c.setAuthor(b["signatur"])

    variante = b.get("grafik", "bogen")
    if variante not in GRAFIKEN:
        print(f"Hinweis: Grafikvariante {variante!r} ist unbekannt – gezeichnet wird 'bogen'. "
              f"Möglich sind: {', '.join(GRAFIKEN)}.")
        variante = "bogen"
    if GRAFIKEN[variante] is not None:
        GRAFIKEN[variante](c)

    s = Stift(c)
    s.block(b["absender"], ersteFett=True)

    s.abstand(34)
    s.block(b["empfaenger"], x=EINZUG)

    s.abstand(22.5)
    s.zeile(b["datum"], x=EINZUG)

    s.abstand(28.3)
    c.setFont(SCHRIFT + "-Bold", GROESSE)
    c.setFillColor(BRAUN)
    c.drawString(RAND_L, s.y - GROESSE, b["betreff"])
    if b.get("stellennummer"):
        c.setFont(SCHRIFT, 9.5)
        c.setFillColor(GRAU)
        c.drawRightString(BREITE - RAND_R, s.y - GROESSE, f"Referenz {b['stellennummer']}")
    s.y -= ZEILE
    # feine Sandlinie unter dem Betreff
    linie_y = s.y - 5
    c.setStrokeColor(SAND)
    c.setLineWidth(0.7)
    c.line(RAND_L, linie_y, BREITE - RAND_R, linie_y)
    s.y = linie_y

    s.abstand(21)
    s.zeile(b["anrede"])

    for a in b["absaetze"]:
        s.abstand(13)
        s.absatz(a)

    s.abstand(21)
    s.zeile(b["gruss"])

    # Eingesetzt wird ausschliesslich ein eigener Scan, angegeben über
    # "unterschrift" in den Briefdaten. Ohne eigene Datei wird der Name in
    # einer Handschrift gesetzt.
    unterschrift = None
    if b.get("unterschrift"):
        kandidat = Path(b["unterschrift"]).expanduser()
        if not kandidat.is_absolute():
            kandidat = BASE.parent / kandidat
        if kandidat.is_file():
            unterschrift = kandidat
        else:
            print(f"Hinweis: {kandidat} nicht gefunden – Name wird in Handschrift gesetzt.")

    if unterschrift:
        # Masse exakt wie .sig in brief_style.css: 40 pt hoch, 6 pt Abstand
        # nach oben, 8 pt negativer Abstand nach unten, dazu 4 pt margin-top
        # der Namenszeile. Netto ragt die Unterschrift 4 pt in die Namenszeile.
        from PIL import Image
        with Image.open(unterschrift) as im:
            seitenverhaeltnis = im.width / im.height
        hoehe = 40
        s.abstand(6)
        oben = s.y
        c.drawImage(str(unterschrift), RAND_L, oben - hoehe,
                    width=hoehe * seitenverhaeltnis, height=hoehe, mask="auto")
        s.y = oben - hoehe + 4
    elif HANDSCHRIFT:
        s.abstand(12)
        c.setFont(HANDSCHRIFT, 22)
        c.setFillColor(SCHWARZ)
        c.drawString(RAND_L, s.y - 16, b["signatur"])
        s.y -= 24
    else:
        print("Hinweis: keine Handschrift gefunden – es steht nur der gedruckte Name.")
        s.abstand(8)

    s.zeile(b["signatur"], fett=True, farbe=BRAUN)

    c.showPage()
    c.save()


def main():
    if len(sys.argv) != 3:
        sys.exit(
            "Aufruf: python brief_rl.py <briefdaten.py> <ausgabe.pdf>\n"
            "Beispiel: python generator/brief_rl.py beispiel/brief_beispiel.py "
            "ausgabe/Bewerbung.pdf"
        )

    data_file = Path(sys.argv[1])
    if not data_file.is_file():
        sys.exit(f"Briefdaten nicht gefunden: {data_file}")

    ziel = Path(sys.argv[2])
    # Der Ausgabeordner steht in der .gitignore und fehlt deshalb in einem
    # frischen Klon. Ohne diese Zeile scheitert der erste Aufruf.
    ziel.parent.mkdir(parents=True, exist_ok=True)

    spec = importlib.util.spec_from_file_location("brief_daten", data_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    zeichnen(mod.BRIEF, ziel)
    print(f"geschrieben: {ziel}")


if __name__ == "__main__":
    main()
