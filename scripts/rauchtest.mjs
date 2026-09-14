/**
 * Rauchtest
 * =========
 * Aufruf:  npm test
 *
 * Erzeugt beide Beispieldokumente in einem temporären Ordner und prüft, ob
 * dabei etwas Brauchbares herauskommt. Das ersetzt keine inhaltliche Prüfung,
 * fängt aber die Sorte Fehler, die einen Fremden beim ersten Versuch aufhält:
 * fehlende Ausgabeordner, fehlende Schriften, kaputte Argumente.
 *
 * Fehlt Python oder ReportLab, wird der Briefteil übersprungen statt zu
 * scheitern — der Lebenslauf lässt sich auch ohne Python erzeugen.
 */

import { execFileSync, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HIER = path.dirname(fileURLToPath(import.meta.url));
const WURZEL = path.join(HIER, "..");
const TEMP = fs.mkdtempSync(path.join(os.tmpdir(), "bewerbung-rauchtest-"));

let fehler = 0;
let uebersprungen = 0;

function melde(zustand, text, detail) {
  const marke = { ok: "  OK  ", fehler: " FEHL ", skip: " ÜBER " }[zustand];
  console.log(`[${marke}] ${text}`);
  if (detail) console.log(`         ${detail}`);
  if (zustand === "fehler") fehler += 1;
  if (zustand === "skip") uebersprungen += 1;
}

/** Datei muss existieren und grösser als die Mindestgrösse sein. */
function pruefeDatei(datei, minKB, text) {
  if (!fs.existsSync(datei)) return melde("fehler", text, "Datei wurde nicht erzeugt");
  const kb = fs.statSync(datei).size / 1024;
  if (kb < minKB) return melde("fehler", text, `nur ${kb.toFixed(1)} KB, erwartet mindestens ${minKB} KB`);
  melde("ok", text, `${kb.toFixed(0)} KB`);
}

/** Ersten funktionierenden Python-Aufruf finden. */
function findePython() {
  for (const kandidat of ["python3", "python", "py"]) {
    const r = spawnSync(kandidat, ["-c", "import reportlab"], { encoding: "utf8" });
    if (r.status === 0) return kandidat;
  }
  return null;
}

console.log(`Rauchtest, Arbeitsordner ${TEMP}\n`);

// ---------- Lebenslauf ----------
const cvZiel = path.join(TEMP, "unterordner", "CV.docx");
try {
  execFileSync("node", [
    path.join(WURZEL, "generator", "cv", "word_cv.js"),
    path.join(WURZEL, "beispiel", "cv_beispiel.json"),
    cvZiel,
  ], { stdio: "pipe" });
  // Der Unterordner existiert absichtlich nicht: so wird geprüft, dass der
  // Generator ihn selbst anlegt.
  pruefeDatei(cvZiel, 10, "Lebenslauf erzeugt, Ausgabeordner selbst angelegt");
} catch (e) {
  melde("fehler", "Lebenslauf erzeugt", String(e.stderr || e.message).split("\n")[0]);
}

// ---------- Lebenslauf, kompakte Variante ----------
const cvKompakt = path.join(TEMP, "CV_kompakt.docx");
try {
  execFileSync("node", [
    path.join(WURZEL, "generator", "cv", "word_cv.js"),
    path.join(WURZEL, "beispiel", "cv_beispiel.json"),
    cvKompakt, "--kompakt",
  ], { stdio: "pipe" });
  pruefeDatei(cvKompakt, 10, "Lebenslauf mit --kompakt erzeugt");
} catch (e) {
  melde("fehler", "Lebenslauf mit --kompakt erzeugt", String(e.stderr || e.message).split("\n")[0]);
}

// ---------- Argumentprüfung ----------
const ohneArgumente = spawnSync("node", [path.join(WURZEL, "generator", "cv", "word_cv.js")], { encoding: "utf8" });
if (ohneArgumente.status === 1 && /Aufruf:/.test(ohneArgumente.stderr)) {
  melde("ok", "Aufruf ohne Argumente zeigt einen Hinweis");
} else {
  melde("fehler", "Aufruf ohne Argumente zeigt einen Hinweis",
    `Rückgabewert ${ohneArgumente.status}, erwartet 1 mit Nutzungshinweis`);
}

// ---------- Anschreiben ----------
const python = findePython();
if (!python) {
  melde("skip", "Anschreiben erzeugt", "Python mit ReportLab nicht gefunden");
} else {
  const briefZiel = path.join(TEMP, "unterordner2", "Bewerbung.pdf");
  const r = spawnSync(python, [
    path.join(WURZEL, "generator", "brief_rl.py"),
    path.join(WURZEL, "beispiel", "brief_beispiel.py"),
    briefZiel,
  ], { encoding: "utf8" });

  if (r.status !== 0 && /Schrift nicht gefunden/.test(r.stdout + r.stderr)) {
    melde("skip", "Anschreiben erzeugt", "keine passende Schrift installiert, siehe docs/setup.md");
  } else if (r.status !== 0) {
    melde("fehler", "Anschreiben erzeugt", (r.stderr || "").trim().split("\n").pop());
  } else {
    pruefeDatei(briefZiel, 5, "Anschreiben erzeugt, Ausgabeordner selbst angelegt");
  }

  // Unterlagen einlesen: an einer Datei aus dem Repository selbst geprüft.
  const unterlagenZiel = path.join(TEMP, "unterordner3", "unterlagen.txt");
  const ru = spawnSync(python, [
    path.join(WURZEL, "scripts", "unterlagen_lesen.py"),
    path.join(WURZEL, "docs", "regeln.md"),
    "-o", unterlagenZiel,
  ], { encoding: "utf8" });

  if (ru.status !== 0 && /pypdfium2/.test(ru.stdout + ru.stderr)) {
    melde("skip", "Unterlagen eingelesen", "pypdfium2 nicht installiert");
  } else if (ru.status !== 0) {
    melde("fehler", "Unterlagen eingelesen", (ru.stderr || "").trim().split("\n").pop());
  } else if (!fs.existsSync(unterlagenZiel) || !/Quellenpflicht/.test(fs.readFileSync(unterlagenZiel, "utf8"))) {
    melde("fehler", "Unterlagen eingelesen", "Inhalt fehlt in der Ausgabedatei");
  } else {
    melde("ok", "Unterlagen eingelesen, Ausgabeordner selbst angelegt");
  }

  // Jede dokumentierte Grafikvariante muss auch tatsächlich zeichnen.
  const daten = fs.readFileSync(path.join(WURZEL, "beispiel", "brief_beispiel.py"), "utf8");
  const groessen = {};
  for (const variante of ["bogen", "welle", "diagonal", "keine"]) {
    const kopie = path.join(TEMP, `brief_${variante}.py`);
    fs.writeFileSync(kopie, daten.replace(/"grafik":\s*"[^"]*"/, `"grafik": "${variante}"`), "utf8");
    const ziel = path.join(TEMP, `Bewerbung_${variante}.pdf`);
    const rr = spawnSync(python, [path.join(WURZEL, "generator", "brief_rl.py"), kopie, ziel], { encoding: "utf8" });
    groessen[variante] = rr.status === 0 && fs.existsSync(ziel) ? fs.statSync(ziel).size : 0;
  }

  if (Object.values(groessen).some((g) => g === 0)) {
    melde("skip", "Grafikvarianten zeichnen unterschiedlich", "Brief liess sich nicht erzeugen");
  } else {
    const eindeutig = new Set(Object.values(groessen)).size;
    if (eindeutig === Object.keys(groessen).length) {
      melde("ok", "Jede Grafikvariante zeichnet etwas anderes",
        Object.entries(groessen).map(([k, v]) => `${k} ${v}`).join(", "));
    } else {
      melde("fehler", "Jede Grafikvariante zeichnet etwas anderes",
        "gleich grosse Dateien: " + Object.entries(groessen).map(([k, v]) => `${k} ${v}`).join(", "));
    }
  }
}

fs.rmSync(TEMP, { recursive: true, force: true });

console.log(`\n${fehler} Fehler, ${uebersprungen} übersprungen.`);
process.exit(fehler > 0 ? 1 : 0);
