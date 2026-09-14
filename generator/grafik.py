# -*- coding: utf-8 -*-
"""
Hintergrundgrafiken für Bewerbungsschreiben und Lebenslauf.

Jede Variante ist ein SVG in A4-Punktmassen (595.28 x 841.89), das als
Seitenhintergrund hinter den Brieftext gelegt wird. Der Sandton ist derselbe
wie im Lebenslauf (#D8BFA0), der Braunton derselbe wie die Namenszeile (#64493E).

Alle Varianten arbeiten in der unteren rechten Ecke, halten den Kopf des Briefs
frei und bleiben so blass, dass sie den Text nicht stören.

Varianten:
  "bogen"       – grosser geschichteter Bogen unten rechts               (Standard)
  "bogen_linie" – wie oben, dazu Betreff in Braun mit feiner Sandlinie
  "welle"       – flache Welle über die ganze untere Kante
  "diagonal"    – weiche Diagonale von unten rechts nach oben
  "keine"       – ohne Grafik

Zur Variante gehört jeweils eine Textauszeichnung in brief_style.css
(body-Klasse "v-<variante>").
"""

SAND = "#D8BFA0"

_VARIANTEN = {
    # Drei ineinanderliegende Viertelkreise, aussen blass, innen etwas kräftiger.
    "bogen": f"""
      <path d="M595.28 841.89 L595.28 511 A331 331 0 0 0 264 841.89 Z"
            fill="{SAND}" opacity="0.09"/>
      <path d="M595.28 841.89 L595.28 621 A221 221 0 0 0 374 841.89 Z"
            fill="{SAND}" opacity="0.11"/>
      <path d="M595.28 841.89 L595.28 719 A123 123 0 0 0 472 841.89 Z"
            fill="{SAND}" opacity="0.16"/>
    """,
    "bogen_linie": f"""
      <path d="M595.28 841.89 L595.28 511 A331 331 0 0 0 264 841.89 Z"
            fill="{SAND}" opacity="0.09"/>
      <path d="M595.28 841.89 L595.28 621 A221 221 0 0 0 374 841.89 Z"
            fill="{SAND}" opacity="0.11"/>
      <path d="M595.28 841.89 L595.28 719 A123 123 0 0 0 472 841.89 Z"
            fill="{SAND}" opacity="0.16"/>
    """,
    # Flache Welle, die über die gesamte Blattbreite laeuft.
    "welle": f"""
      <path d="M0 841.89 L0 762 C 150 700, 330 806, 595.28 668 L595.28 841.89 Z"
            fill="{SAND}" opacity="0.09"/>
      <path d="M0 841.89 L0 812 C 170 762, 360 848, 595.28 742 L595.28 841.89 Z"
            fill="{SAND}" opacity="0.13"/>
    """,
    # Weiche Diagonale, die von unten rechts gegen die Blattmitte laeuft.
    "diagonal": f"""
      <path d="M595.28 841.89 L595.28 372 L232 841.89 Z" fill="{SAND}" opacity="0.08"/>
      <path d="M595.28 841.89 L595.28 566 L358 841.89 Z" fill="{SAND}" opacity="0.11"/>
      <path d="M595.28 841.89 L595.28 731 L484 841.89 Z" fill="{SAND}" opacity="0.16"/>
    """,
    "keine": "",
}


def svg(variante="bogen"):
    inhalt = _VARIANTEN.get(variante, _VARIANTEN["bogen"])
    if not inhalt.strip():
        return None
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="595.28" height="841.89" '
        'viewBox="0 0 595.28 841.89">' + inhalt + "</svg>"
    )


# Der Lebenslauf ist dichter gesetzt als der Brief, deshalb liegt dieselbe Form
# dort eine Stufe blasser hinter dem Text.
# staerke: 1.0 = gleich kraeftig wie im Brief, kleiner = blasser.
# Ueber DATA["grafik_staerke"] pro Lebenslauf steuerbar.
def cv_svg(variante="bogen", staerke=1.0):
    """Dieselbe Form wie im Brief, auf Wunsch blasser."""
    import re
    bild = svg(variante)
    if bild is None:
        return None
    return re.sub(
        r'opacity="([0-9.]+)"',
        lambda m: 'opacity="%.3f"' % (float(m.group(1)) * staerke),
        bild,
    )


def cv_page_css(variante="keine", staerke=1.0):
    """@page-Regel fuer den Lebenslauf.

    Standard ist "keine": Der Lebenslauf traegt den Sandton bereits im Kopfbalken,
    ein zusaetzlicher Bogen wirkt dort unruhig. Die Funktion bleibt vorhanden,
    falls eine Variante doch einmal gewuenscht ist.
    """
    bild = cv_svg(variante, staerke)
    if bild is None:
        return ""
    import base64
    b64 = base64.b64encode(bild.encode("utf-8")).decode()
    return (
        "@page { background-image: url(data:image/svg+xml;base64,%s);"
        " background-position: 0 0; background-repeat: no-repeat;"
        " background-size: 595.28pt 841.89pt; }" % b64
    )


def page_css(variante="bogen", rand_oben="21mm", rand_links="25mm"):
    """Liefert die @page-Regel mit der Grafik als eingebettetes SVG.

    WeasyPrint setzt den Ursprung des Seitenhintergrunds an die innere Kante
    der Seitenraender. Damit die Grafik randabfallend sitzt, wird sie um genau
    diese Raender zurueckgeschoben.
    """
    bild = svg(variante)
    if bild is None:
        return ""
    import base64
    b64 = base64.b64encode(bild.encode("utf-8")).decode()
    return (
        "@page { background-image: url(data:image/svg+xml;base64,%s);"
        " background-position: -%s -%s; background-repeat: no-repeat;"
        " background-size: 595.28pt 841.89pt; }" % (b64, rand_links, rand_oben)
    )
