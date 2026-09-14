# -*- coding: utf-8 -*-
"""
Schriften in eine Word-Datei einbetten
======================================

Aufruf:  python3 schriften_einbetten.py <datei.docx> [weitere.docx ...]

Word ersetzt eine Schrift stillschweigend, wenn sie auf dem Rechner fehlt, und
genau daran scheitert sonst das Layout: Poppins und Carlito sind auf einem
frischen Windows nicht installiert. Beide stehen unter der SIL Open Font
License und dürfen deshalb in ein Dokument eingebettet werden.

OOXML legt eingebettete Schriften unter word/fonts/ ab, allerdings verschleiert:
Die ersten 32 Bytes der Datei sind mit dem sogenannten Font-Key verXORt, einer
GUID, die in fontTable.xml neben der Schrift steht. Genau das macht obfuskieren()
weiter unten.
"""

import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path

# Welche Schnitte zu welcher Word-Schriftfamilie gehören.
SCHRIFTEN = {
    "Poppins": {
        "embedRegular": "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
        "embedBold": "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    },
    "Poppins Light": {
        "embedRegular": "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
    },
    "Poppins Medium": {
        "embedRegular": "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf",
    },
    "Carlito": {
        "embedRegular": "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf",
        "embedBold": "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
    },
    "Montserrat": {
        "embedRegular": "/root/.fonts/Montserrat-Regular.ttf",
        "embedBold": "/root/.fonts/Montserrat-Bold.ttf",
    },
    "Montserrat Light": {
        "embedRegular": "/root/.fonts/Montserrat-Light.ttf",
    },
    "Montserrat Medium": {
        "embedRegular": "/root/.fonts/Montserrat-Medium.ttf",
    },
    "Montserrat SemiBold": {
        "embedRegular": "/root/.fonts/Montserrat-SemiBold.ttf",
    },
}

NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
TYP_FONT = NS_R + "/font"


def obfuskieren(rohdaten, guid):
    """Die ersten 32 Bytes mit dem Font-Key verXORen, wie Word es erwartet."""
    hexziffern = guid.strip("{}").replace("-", "")
    schluessel = bytes.fromhex(hexziffern)[::-1]      # Bytefolge umgekehrt
    kopf = bytearray(rohdaten[:32])
    for i in range(32):
        kopf[i] ^= schluessel[i % 16]
    return bytes(kopf) + rohdaten[32:]


def einbetten(docx_pfad):
    docx_pfad = Path(docx_pfad)
    quelle = zipfile.ZipFile(docx_pfad)
    dateien = {n: quelle.read(n) for n in quelle.namelist()}
    quelle.close()

    font_table = dateien.get("word/fontTable.xml", b"").decode("utf-8")

    # docx-js legt eine leere Schrifttabelle an. Die Einträge für die tatsächlich
    # verwendeten Familien werden deshalb hier erzeugt.
    benutzt = set()
    for name, inhalt in dateien.items():
        if name.startswith("word/") and name.endswith(".xml"):
            for treffer in re.findall(r'w:ascii="([^"]+)"', inhalt.decode("utf-8", "ignore")):
                benutzt.add(treffer)
    fehlend = [f for f in SCHRIFTEN if f in benutzt and f'w:name="{f}"' not in font_table]
    if fehlend:
        neu = "".join(
            f'<w:font w:name="{f}"><w:charset w:val="00"/><w:family w:val="swiss"/>'
            f'<w:pitch w:val="variable"/></w:font>' for f in fehlend
        )
        if font_table.rstrip().endswith("/>"):
            font_table = font_table.rstrip()[:-2] + ">" + neu + "</w:fonts>"
        else:
            font_table = font_table.replace("</w:fonts>", neu + "</w:fonts>")
    rels = dateien.get(
        "word/_rels/fontTable.xml.rels",
        b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns='
        b'"http://schemas.openxmlformats.org/package/2006/relationships"/>',
    ).decode("utf-8")

    neue_rels = []
    nummer = 0
    eingebettet = []

    for familie, schnitte in SCHRIFTEN.items():
        # Nur einbetten, was im Dokument auch vorkommt.
        if f'w:name="{familie}"' not in font_table:
            continue
        eintraege = ""
        for element, quelldatei in schnitte.items():
            if not Path(quelldatei).exists():
                print(f"  fehlt: {quelldatei}")
                continue
            nummer += 1
            guid = "{%s}" % str(uuid.UUID(int=nummer * 0x1111111111111111111111111111111)).upper()
            rid = f"rIdFont{nummer}"
            ziel = f"word/fonts/font{nummer}.odttf"
            dateien[ziel] = obfuskieren(Path(quelldatei).read_bytes(), guid)
            eintraege += f'<w:{element} r:id="{rid}" w:fontKey="{guid}" w:subsetted="false"/>'
            neue_rels.append(
                f'<Relationship Id="{rid}" Type="{TYP_FONT}" Target="fonts/font{nummer}.odttf"/>'
            )
            eingebettet.append(f"{familie} ({element[5:].lower()})")

        if eintraege:
            # Die Einbettungs-Elemente gehören ans Ende des jeweiligen w:font-Blocks.
            muster = re.compile(
                r'(<w:font w:name="' + re.escape(familie) + r'">)(.*?)(</w:font>)', re.S
            )
            font_table = muster.sub(lambda m: m.group(1) + m.group(2) + eintraege + m.group(3),
                                    font_table, count=1)

    if not eingebettet:
        print(f"{docx_pfad.name}: keine passende Schrift gefunden")
        return

    if "</Relationships>" in rels:
        rels = rels.replace("</Relationships>", "".join(neue_rels) + "</Relationships>")
    else:                                    # leeres Element <Relationships .../>
        rels = rels.rstrip().rstrip("/>") + ">" + "".join(neue_rels) + "</Relationships>"

    dateien["word/fontTable.xml"] = font_table.encode("utf-8")
    dateien["word/_rels/fontTable.xml.rels"] = rels.encode("utf-8")

    # settings.xml: Word muss das Einbetten auch eingeschaltet bekommen.
    # settings.xml folgt einer festen Elementreihenfolge: embedTrueTypeFonts steht
    # direkt nach displayBackgroundShape, sonst weist Word die Datei zurueck.
    settings = dateien["word/settings.xml"].decode("utf-8")
    if "embedTrueTypeFonts" not in settings:
        anker = "<w:displayBackgroundShape/>"
        if anker in settings:
            settings = settings.replace(anker, anker + "<w:embedTrueTypeFonts/>", 1)
        else:
            settings = re.sub(r"(<w:settings[^>]*>)", r"\1<w:embedTrueTypeFonts/>",
                              settings, count=1)
        dateien["word/settings.xml"] = settings.encode("utf-8")

    # Content-Type für .odttf ergänzen.
    ct = dateien["[Content_Types].xml"].decode("utf-8")
    if 'Extension="odttf"' not in ct:
        ct = ct.replace(
            "<Types ",
            "<Types ", 1
        ).replace(
            ">", '><Default Extension="odttf" ContentType="application/vnd.openxmlformats-'
                 'officedocument.obfuscatedFont"/>', 1
        )
        dateien["[Content_Types].xml"] = ct.encode("utf-8")

    ziel = docx_pfad.with_suffix(".tmp.docx")
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        for name, inhalt in dateien.items():
            z.writestr(name, inhalt)
    shutil.move(str(ziel), str(docx_pfad))
    print(f"{docx_pfad.name}: eingebettet – {', '.join(eingebettet)}")


if __name__ == "__main__":
    for pfad in sys.argv[1:]:
        einbetten(pfad)
