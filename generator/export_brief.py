# -*- coding: utf-8 -*-
"""Wandelt eine Briefdatendatei in JSON um.

Aufruf:  python export_brief.py <briefdaten.py> <ausgabe.json>

Nützlich, um Briefdaten an ein anderes Werkzeug weiterzureichen oder zwei
Fassungen miteinander zu vergleichen.
"""
import importlib.util, json, sys
from pathlib import Path

if len(sys.argv) != 3:
    sys.exit("Aufruf: python export_brief.py <briefdaten.py> <ausgabe.json>")

quelle = Path(sys.argv[1])
if not quelle.is_file():
    sys.exit(f"Briefdaten nicht gefunden: {quelle}")

ziel = Path(sys.argv[2])
ziel.parent.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("brief_daten", quelle)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ziel.write_text(json.dumps(mod.BRIEF, ensure_ascii=False, indent=1), encoding="utf-8")
print("geschrieben:", ziel)
