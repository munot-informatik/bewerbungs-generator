# Begriffe aus dem Inserat spiegeln

Viele Bewerbungen laufen durch ein Bewerbermanagementsystem, bevor ein Mensch
sie sieht. Zwei Dinge muss man darüber wissen, bevor man Begriffe verteilt.

**Es wird exakt gesucht, nicht sinngemäss.** Ein System, das nach
«Microsoft 365» sucht, findet «M365» nicht zuverlässig und «Office-Paket» gar
nicht. Beide Schreibweisen unterbringen, wo es natürlich geht.

**Die Stellenanzeige ist die Begriffsliste.** Kein generischer Katalog schlägt
das Spiegeln des konkreten Inserats. Vor dem Absenden das Inserat durchgehen,
die Substantive markieren und prüfen, ob sie im Lebenslauf vorkommen. Fehlt
einer und stimmt inhaltlich, einbauen. Fehlt einer und stimmt nicht,
weglassen — siehe [`regeln.md`](regeln.md).

---

## Wo die Begriffe hingehören

| Ort | Wirkung | Regel |
|---|---|---|
| Rollenzeile unter dem Namen | sehr hoch | beschreibt dich, nicht die Zielstelle |
| Kurzprofil | sehr hoch | vier bis sechs Kernbegriffe in ganzen Sätzen |
| Stellenbezeichnungen | hoch | Funktionsbezeichnung statt Fantasietitel |
| Aufzählungen der Stationen | hoch | der beste Ort, weil belegt und im Kontext |
| Kenntnisse-Block | mittel | Sammelbecken für alles, was oben keinen Platz fand |
| Kopf- und Fusszeile, Grafik | null | wird oft nicht ausgelesen |

Ein Begriff wirkt am stärksten, wenn er zweimal vorkommt: einmal im
Kurzprofil, einmal in einer Station. Dreimal und öfter wirkt gestopft und
fällt beim menschlichen Lesen unangenehm auf.

**Die Rollenzeile beschreibt dich, nicht die Stelle.** «Kaufmännischer
Sachbearbeiter mit IT-Kompetenz» ist richtig. Den Titel der Ausschreibung dort
hineinzuschreiben, obwohl man den Beruf nie ausgeübt hat, ist keine
Anpassung, sondern eine Behauptung.

---

## Lesbarkeit für Maschinen

- **Einspaltig.** Verschachtelte Layouts mit überlappenden Elementen bringen
  Parser durcheinander. Randlose Tabellen sind meist unkritisch, solange sie
  zeilenweise gelesen sinnvoll bleiben.
- **Kontaktdaten in den Textkörper**, nicht in eine gestalterische Kopfzeile.
- **Icons kosten Treffer.** Ein Symbol vor der Nummer ist unproblematisch, ein
  Symbol *anstelle* des Wortes «Telefon» wird nicht gefunden.
- **Text in Grafiken ist unsichtbar.** Skill-Balken und Diagramme existieren
  für den Parser nicht — ein Grund mehr, sie wegzulassen.
- **Als PDF exportieren, nicht als Bild.**
- **Schriften einbetten**, sonst rendert die Datei auf einem fremden Rechner
  mit einer Ersatzschrift und zerfällt. Dafür gibt es
  `generator/schriften_einbetten.py`.

Prüfen lässt sich das mit zwei Zeilen:

```bash
pdftotext ausgabe/CV.pdf - | less     # kommt der Text in sinnvoller Reihenfolge?
```

Stimmt die Reihenfolge und sind alle Begriffe da, ist die Datei lesbar.

---

## Ablauf vor jedem Versand

1. Inserat durchlesen, alle Substantive und Systemnamen markieren.
2. Prüfen, welche davon inhaltlich zutreffen.
3. Zutreffende Begriffe an der passenden Station einbauen, falls sie fehlen.
4. Nicht Zutreffendes weglassen.
5. PDF-Text auslesen und gegenlesen: Reihenfolge stimmig, keine zerrissenen
   Wörter, alle Begriffe da.
