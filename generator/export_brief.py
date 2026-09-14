# -*- coding: utf-8 -*-
"""Wandelt eine Briefdatendatei in JSON für den Word-Generator um."""
import importlib.util, json, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("brief_daten", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
Path(sys.argv[2]).write_text(json.dumps(mod.BRIEF, ensure_ascii=False, indent=1), encoding="utf-8")
print("geschrieben:", sys.argv[2])
