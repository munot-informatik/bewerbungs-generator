# Unterlagen sichten, bevor geschrieben wird

Der erste Schritt jeder Bewerbung ist nicht das Schreiben. Er ist das Lesen.

Der gepflegte Lebenslauf ist selten die ganze Wahrheit über ein Berufsleben. Er
ist eine Auswahl, die irgendwann getroffen wurde, oft unter Zeitdruck und für
eine andere Stelle. Im Dossier liegen daneben Arbeitszeugnisse, Diplome,
Kursbestätigungen und Referenzen, und darin steht regelmässig etwas, das im
Lebenslauf fehlt.

Nach [`regeln.md`](regeln.md) sind das zulässige Quellen. Man muss sie nur
gelesen haben, bevor man behauptet, es gebe keinen Beleg.

Ein Beispiel aus der Praxis. In einem Dossier lag auf Seite 8 ein
Arbeitszeugnis über einen dreimonatigen Einsatz, der im Lebenslauf gar nicht
auftauchte. Darin standen Sätze wie «sorgfältig und genau», «die Quantität
entsprach den Vorgaben» und «das Einhalten von Regeln war für ihn
selbstverständlich». Für eine Stelle, die Zuverlässigkeit und körperlich
genaues Arbeiten verlangte, war das der beste Beleg im ganzen Dossier — und er
wäre ungenutzt geblieben.

---

## Schritt 1: alles einlesen

```bash
python scripts/unterlagen_lesen.py ~/Bewerbung/Dossier.pdf -o daten/unterlagen.txt
```

Es lassen sich auch mehrere Dateien oder ein ganzer Ordner übergeben.
Unterstützt werden PDF, Word, Text und Markdown.

Das Skript meldet zwei Dinge, die man sonst übersieht.

**Seiten ohne Textebene.** Eingescannte Zeugnisse sind Bilder. Weder dieses
Skript noch ein Bewerbermanagementsystem liest sie. Wer ein solches Dossier
verschickt, verschickt für die Maschine leere Seiten. Das ist kein
Schönheitsfehler, sondern der Grund, weshalb gute Bewerbungen manchmal
spurlos verschwinden. Was darin steht, gehört von Hand erfasst oder durch eine
OCR geschickt.

**Durcheinandergeratene Spalten.** Läuft der ausgelesene Text eines
zweispaltigen Lebenslaufs ineinander, dann liest ihn eine Maschine genauso.
Steht in der Textdatei «Kundenbetreuung via TelefonSachbearbeiterin
Kundendienst», ist das ein Befund über den Lebenslauf, kein Fehler des
Skripts. Mehr dazu in [`keywords.md`](keywords.md).

---

## Schritt 2: Fundliste anlegen

Die Textdatei durchgehen und notieren, was belegt ist und im Lebenslauf fehlt.
Fünf Dinge lohnen die Suche besonders:

**Beurteilungen der Arbeitsweise.** Arbeitszeugnisse formulieren, was man
selbst nur als Adjektiv hinschreiben würde. «Sorgfältig und genau» aus einem
Zeugnis ist ein Beleg, «sorgfältig» im eigenen Profil ist eine Behauptung.

**Zahlen.** Stückzahlen, Quoten, Bewertungen, Teamgrössen, Budgets. Eine Zahl
aus einem Zeugnis oder einer Auswertung schlägt jedes Eigenschaftswort.

**Vergessene Stationen.** Befristete Einsätze, Praktika, Aushilfen,
Nebenprojekte. Was damals nebensächlich schien, kann für diese eine Stelle der
einzige direkte Beleg sein.

**Weiterbildungen ohne Diplom.** Interne Schulungen, Kurse, Zertifikate mit
Ablaufdatum. Steht selten im Lebenslauf, ist aber belegt.

**Werkzeuge und Systeme.** Programme, die in einem Zeugnis namentlich stehen.
Nach Regel 5 darf nur genannt werden, was tatsächlich benutzt wurde — ein
Zeugnis ist genau dieser Nachweis.

Zu jedem Fund gehört die Quelle: Datei und Seite. Ohne Quellenangabe ist es
später nicht mehr nachvollziehbar.

---

## Schritt 3: fragen, bevor geschrieben wird

Die Fundliste beantwortet nicht alles. Bevor irgendetwas entsteht, werden
diese Fragen gestellt — und zwar vorher, nicht wenn der Entwurf schon steht:

1. **Gibt es Unterlagen, die hier nicht dabei sind?** Arbeitszeugnisse,
   Diplome, Kursbestätigungen, Referenzen, ein zweiter Lebenslauf für eine
   andere Branche.
2. **Was steht auf den Seiten ohne Textebene?** Wenn OCR keine Option ist,
   reicht eine mündliche Zusammenfassung der wichtigsten Sätze.
3. **Steht etwas bewusst nicht im Lebenslauf?** Eine Station, eine Lücke, ein
   Arbeitgeber. Wer das nicht fragt, trägt es hilfsbereit wieder ein.
4. **Welche Lücken sind bekannt?** Was die Stelle verlangt und im Profil
   fehlt, wird weggelassen, nicht erfunden und nicht verneint
   ([`regeln.md`](regeln.md), Abschnitt «Lücken, die nicht gefüllt werden»).
5. **Was ist seit der letzten Fassung dazugekommen?** Der Lebenslauf ist meist
   älter als das Berufsleben.

Dazu kommen die Fragen zur konkreten Stelle: Pensum, Eintritt, besondere
Einsatzzeiten, und alles, was die Ausschreibung verlangt und wofür sich in den
Unterlagen kein Beleg findet.

**Die Antworten gehören in die Fundliste**, mit dem Vermerk, dass sie aus einer
Aussage der Bewerberin stammen. Auch das ist nach Regel 1 eine Quelle.

---

## Schritt 4: erst jetzt schreiben

Der Lebenslauf entsteht aus dem Quell-Lebenslauf **plus** der Fundliste. Was
neu dazukommt, kommt aus einem Zeugnis oder aus einer Antwort — nicht aus der
Stellenanzeige und nicht aus der Vorstellung davon, was gut klingen würde.

Zwei Dinge gelten dabei weiter:

Eine bestehende Vorlage ist kein Grund, nicht zu suchen. Gerade eine gut
gepflegte Vorlage verleitet dazu, sie für vollständig zu halten.

Und die Fundliste ist ein Angebot, keine Pflicht. Nicht jeder Fund gehört in
jede Bewerbung. Was für diese Stelle nichts beiträgt, bleibt draussen — siehe
[`regeln.md`](regeln.md), «Weglassen ist nicht Ausdünnen».
