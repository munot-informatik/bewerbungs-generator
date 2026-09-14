/**
 * Lebenslauf als Word-Datei
 * =========================
 * Aufruf:  node word_cv_nele.js <master.json> <ausgabe.docx>
 *
 * Zweispaltig anmutendes, technisch einspaltiges Layout in Braun, Sand und
 * Gold, gesetzt in Montserrat. ATS-freundlich: Name, Kontakt und alle Inhalte
 * stehen als echter Text im Dokumentkörper (nicht in Kopf-/Fusszeile, keine
 * Textfelder). Datumsspalte und Rubriken laufen über randlose Tabellen, die
 * zeilenweise (Datum → Inhalt) linear auslesbar sind.
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, VerticalAlign,
  Footer, PageNumber, TabStopType,
} = require("docx");

// Mindestschriftgrad: 9 pt = 18 Halbpunkte. Jeder Textlauf geht durch sz().
const SZ_MIN = 18;
function sz(n) { return Math.max(SZ_MIN, n); }

const DIR = __dirname;
const ASSET = (f) => path.join(DIR, f);
const PARENT = (f) => path.join(DIR, "..", f);

// ---------- Farben ----------
const BRAUN = "64493E";   // Name, Akzent
const SAND  = "D8BFA0";   // Rubrik-Linien
const GOLD  = "C1B293";   // Aufzählungspunkte, Trenner
const DUNKEL= "251D1A";   // Rubriktitel, Rollentitel
const TEXT  = "2E2A28";   // Fliesstext
const GRAU  = "6E6E6E";   // Datum, Sublines

// ---------- Masse ----------
// --kompakt: schmalere Ränder und Datumsspalte -> mehr Textbreite, damit
// Zeilen, die sonst mit einem einzelnen Wort überlaufen, einzeilig werden.
const KOMPAKT = process.argv.includes("--kompakt");
const PT = 20;                       // 1 pt = 20 DXA
const SEITE_B = 11906;               // A4 Breite
const M_LR = KOMPAKT ? 850 : 1134;   // Seitenrand links/rechts (~1.5 / 2 cm)
const M_TOP = 650, M_BOT = 560;
const INHALT_B = SEITE_B - 2 * M_LR; // Textbreite
const px = (pt) => Math.round(pt * PT);
const zeile = (pt) => ({ line: Math.round(pt * PT), lineRule: "exact" });

const daten = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const ausgabe = process.argv[3];

// ---------- Keyword-Hervorhebung (optional) ----------
// daten.keywords: Liste von Begriffen, die im Text fett (Montserrat SemiBold)
// erscheinen, damit Recruiter sie schneller scannen.
const KEYWORDS = (daten.keywords || []).slice().sort((a, b) => b.length - a.length);
const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\-]/g, "\\$&");
// Wortgrenzen: Keyword nur als eigenständiges Wort fett, nicht als Teil eines
// längeren Wortes (kein "Datenschutz" in "Datenschutzrichtlinien").
const KW_RE = KEYWORDS.length
  ? new RegExp("(?<![A-Za-zÄÖÜäöüß])(" + KEYWORDS.map(escapeRe).join("|") + ")(?![A-Za-zÄÖÜäöüß])", "gi")
  : null;

/** Text in Runs zerlegen und Keywords fett setzen. */
function hl(text, opt) {
  const base = { font: opt.font, size: opt.size, color: opt.color, italics: opt.italics };
  if (!KW_RE) return [new TextRun({ text, ...base })];
  const runs = []; let last = 0, m; KW_RE.lastIndex = 0;
  while ((m = KW_RE.exec(text)) !== null) {
    if (m.index > last) runs.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    runs.push(new TextRun({ text: m[0], font: "Montserrat SemiBold", size: opt.size, color: opt.color, italics: opt.italics }));
    last = m.index + m[0].length;
    if (m.index === KW_RE.lastIndex) KW_RE.lastIndex++;
  }
  if (last < text.length) runs.push(new TextRun({ text: text.slice(last), ...base }));
  return runs;
}

// ---------- Bausteine ----------

const keineRahmen = () => {
  const n = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: n, bottom: n, left: n, right: n, insideHorizontal: n, insideVertical: n };
};

/** Rubriktitel: Grossbuchstaben, kurze Sandlinie darunter. */
function sektion(text, vor = 10) {
  return new Paragraph({
    spacing: { before: px(vor), after: px(3.5), ...zeile(14) },
    // Rechter Einzug kürzt die Unterlinie; breit genug, dass auch der
    // längste Titel einzeilig bleibt.
    indent: { right: INHALT_B - 345 * PT },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: SAND, space: 4 } },
    keepNext: true,
    children: [new TextRun({ text: text.toUpperCase(), font: "Montserrat Medium", size: sz(21), color: BRAUN, characterSpacing: 22 })],
  });
}

/** Ein Aufzählungspunkt (markanter Bullet, luftiger Zeilenabstand).
 *  tight=true verdichtet die Skills-Liste, ohne die Erfahrungs-Bullets anzufassen. */
function bullet(inhalt, erster, tight) {
  return new Paragraph({
    spacing: {
      before: tight ? (erster ? px(2.0) : px(1.3)) : (erster ? px(2.2) : px(1.6)),
      after: 0, ...zeile(tight ? 12.9 : 13.0),
    },
    indent: { left: 11 * PT, hanging: 11 * PT },
    children: [
      new TextRun({ text: "•", font: "Montserrat", size: sz(20), color: GOLD }),
      new TextRun({ text: "   ", font: "Montserrat", size: sz(17), color: GOLD }),
      ...hl(inhalt, { font: "Montserrat Light", size: sz(17), color: TEXT }),
    ],
  });
}

/** Randlose zweispaltige Zeile: linke schmale Spalte (Datum), rechte Inhalt. */
function reihe(datumRuns, inhaltKinder, datumsBreite, opt = {}) {
  return new TableRow({
    cantSplit: true,
    children: [
      new TableCell({
        width: { size: datumsBreite, type: WidthType.DXA },
        margins: { top: px(opt.vor || 0), bottom: px(opt.nach || 0), left: 0, right: 120 },
        verticalAlign: VerticalAlign.TOP,
        children: [new Paragraph({ spacing: { before: 0, after: 0, ...zeile(12) }, children: datumRuns })],
      }),
      new TableCell({
        width: { size: INHALT_B - datumsBreite, type: WidthType.DXA },
        margins: { top: px(opt.vor || 0), bottom: px(opt.nach || 0), left: 0, right: 0 },
        verticalAlign: VerticalAlign.TOP,
        children: inhaltKinder,
      }),
    ],
  });
}

function tabelle(rows, datumsBreite) {
  return new Table({
    columnWidths: [datumsBreite, INHALT_B - datumsBreite],
    width: { size: INHALT_B, type: WidthType.DXA },
    borders: keineRahmen(),
    rows,
  });
}

/** Skills als zweispaltiges Raster (spart Platz, wirkt wie ein Kompetenz-Grid). */
function skillCell(s, width) {
  const kids = [new Paragraph({
    spacing: { before: 0, after: 0, ...zeile(12.6) },
    children: [new TextRun({ text: s.title, bold: true, font: "Montserrat", size: sz(16), color: DUNKEL })],
  })];
  s.bullets.forEach((b, j) => kids.push(bullet(b, j === 0, true)));
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    margins: { top: 0, bottom: px(3), left: 0, right: 200 },
    verticalAlign: VerticalAlign.TOP,
    children: kids,
  });
}

/** Kennzahlen als zweispaltiges Raster: Label links, Wert rechts, feine Linie. */
function kpiGrid(kpis) {
  const colW = Math.floor(INHALT_B / 2);
  const pad = 260;
  const cell = (pair) => {
    if (!pair) return new TableCell({ width: { size: colW, type: WidthType.DXA }, children: [new Paragraph({ children: [] })] });
    const [k, v] = pair;
    return new TableCell({
      width: { size: colW, type: WidthType.DXA },
      margins: { top: px(2.6), bottom: px(2.6), left: 0, right: pad },
      children: [new Paragraph({
        spacing: { before: 0, after: 0, ...zeile(13) },
        tabStops: [{ type: TabStopType.RIGHT, position: colW - pad }],
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "E4E4E4", space: 3 } },
        children: [
          new TextRun({ text: k, font: "Montserrat Light", size: sz(16.5), color: TEXT }),
          new TextRun({ text: "\t" + v, bold: true, font: "Montserrat", size: sz(16.5), color: DUNKEL }),
        ],
      })],
    });
  };
  const rows = [];
  for (let i = 0; i < kpis.length; i += 2) rows.push(new TableRow({ cantSplit: true, children: [cell(kpis[i]), cell(kpis[i + 1])] }));
  return new Table({ columnWidths: [colW, colW], width: { size: INHALT_B, type: WidthType.DXA }, borders: keineRahmen(), rows });
}
function skillsGrid(cats) {
  const colW = Math.floor(INHALT_B / 2);
  const rows = [];
  for (let i = 0; i < cats.length; i += 2) {
    const cells = [skillCell(cats[i], colW)];
    cells.push(cats[i + 1]
      ? skillCell(cats[i + 1], colW)
      : new TableCell({ width: { size: colW, type: WidthType.DXA }, children: [new Paragraph({ children: [] })] }));
    rows.push(new TableRow({ cantSplit: true, children: cells }));
  }
  return new Table({ columnWidths: [colW, colW], width: { size: INHALT_B, type: WidthType.DXA }, borders: keineRahmen(), rows });
}

// ---------- Kopfbereich ----------

function kopf() {
  const fotoB = 1660;                 // ~2.9 cm Fotospalte
  const linkeB = INHALT_B - fotoB;
  // Bei 9 pt bricht eine dreiteilige Kontaktzeile um; deshalb bewusst gesetzte Zeilen.
  const kontakt1 = daten.contact.slice(0, 1);
  const kontakt2 = daten.contact.slice(1, 3);
  const kontakt3 = daten.contact.slice(3);

  const trenner = (arr) => {
    const runs = [];
    arr.forEach((w, i) => {
      if (i > 0) runs.push(new TextRun({ text: "  ·  ", font: "Montserrat Light", size: sz(15), color: GOLD }));
      runs.push(new TextRun({ text: w, font: "Montserrat Light", size: sz(15), color: GRAU }));
    });
    return runs;
  };

  const linkeKinder = [
    // Akzentquadrat in Braun
    new Paragraph({
      spacing: { before: 0, after: px(7) },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(ASSET("accent_square.png")), transformation: { width: 50, height: 50 } })],
    }),
    // Name
    new Paragraph({
      spacing: { before: 0, after: 0, ...zeile(26) },
      children: [new TextRun({ text: daten.name.toUpperCase(), bold: true, font: "Montserrat", size: sz(40), color: BRAUN, characterSpacing: 10 })],
    }),
    // Zielposition
    new Paragraph({
      spacing: { before: px(3), after: px(7), ...zeile(15) },
      children: [new TextRun({ text: daten.role, font: "Montserrat Medium", size: sz(19), color: DUNKEL, characterSpacing: 8 })],
    }),
    // Kontakt
    new Paragraph({ spacing: { before: 0, after: 0, ...zeile(13.5) }, children: trenner(kontakt1) }),
    new Paragraph({ spacing: { before: px(1.5), after: 0, ...zeile(13.5) }, children: trenner(kontakt2) }),
    new Paragraph({ spacing: { before: px(1.5), after: 0, ...zeile(13.5) }, children: trenner(kontakt3) }),
  ];

  return new Table({
    columnWidths: [linkeB, fotoB],
    width: { size: INHALT_B, type: WidthType.DXA },
    borders: keineRahmen(),
    rows: [new TableRow({
      children: [
        new TableCell({
          width: { size: linkeB, type: WidthType.DXA },
          margins: { top: 0, bottom: 0, left: 0, right: 200 },
          verticalAlign: VerticalAlign.TOP,
          children: linkeKinder,
        }),
        new TableCell({
          width: { size: fotoB, type: WidthType.DXA },
          margins: { top: 0, bottom: 0, left: 0, right: 0 },
          verticalAlign: VerticalAlign.TOP,
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            spacing: { before: 0, after: 0 },
            children: [new ImageRun({ type: "png", data: fs.readFileSync(ASSET(daten.photo || "foto_portrait.png")), transformation: { width: 122, height: 152 } })],
          })],
        }),
      ],
    })],
  });
}

// ---------- Dokument ----------

const inhalt = [];
inhalt.push(kopf());

// Persönliche Daten
inhalt.push(sektion("Persönliche Daten", 13));
inhalt.push(tabelle(daten.personal.map(([label, wert]) =>
  reihe(
    [new TextRun({ text: label, font: "Montserrat Light", size: sz(16), color: GRAU })],
    [new Paragraph({ spacing: { before: 0, after: 0, ...zeile(13) }, children: [new TextRun({ text: wert, font: "Montserrat Light", size: sz(17), color: TEXT })] })],
    2500, { nach: 1.6 }
  )
), 2500));

// Über mich
inhalt.push(sektion("Über mich"));
inhalt.push(new Paragraph({
  spacing: { before: px(4.5), after: 0, ...zeile(14.2) },
  // "Über mich" bewusst ohne Keyword-Hervorhebung.
  children: [new TextRun({ text: daten.profile, font: "Montserrat Light", size: sz(17), color: TEXT })],
}));

// Arbeitserfahrung
inhalt.push(sektion(daten.exp_title || "Arbeitserfahrungen"));
const DATE_B = KOMPAKT ? 1820 : 1900;
inhalt.push(tabelle(daten.experience.map((e, i) => {
  const kinder = [];
  // Job oben ...
  kinder.push(new Paragraph({
    spacing: { before: 0, after: 0, ...zeile(12.8) },
    children: [
      new TextRun({ text: e.title, bold: true, font: "Montserrat", size: sz(18.5), color: DUNKEL }),
      ...(e.tag ? [new TextRun({ text: "   " + e.tag.toUpperCase(), font: "Montserrat SemiBold", size: sz(12.5), color: BRAUN, characterSpacing: 12 })] : []),
    ],
  }));
  // ... Firma darunter
  kinder.push(new Paragraph({
    spacing: { before: px(1.6), after: 0, ...zeile(12) },
    children: [new TextRun({ text: [e.employer, e.location].filter(Boolean).join(" · "), italics: true, font: "Montserrat", size: sz(16.5), color: GRAU })],
  }));
  e.bullets.forEach((b, j) => kinder.push(bullet(b, j === 0)));
  return reihe(
    [new TextRun({ text: e.date, font: "Montserrat Light", size: sz(16), color: GRAU })],
    kinder, DATE_B, { vor: i === 0 ? 4 : 6, nach: 0 }
  );
}), DATE_B));

// Aus- und Weiterbildung
inhalt.push(sektion(daten.edu_title || "Aus- und Weiterbildungen"));
inhalt.push(tabelle(daten.education.map((e, i) => {
  const kinder = [new Paragraph({
    spacing: { before: 0, after: 0, ...zeile(12.4) },
    children: [new TextRun({ text: e.title, bold: true, font: "Montserrat", size: sz(17.5), color: DUNKEL })],
  })];
  if (e.sub) kinder.push(new Paragraph({
    spacing: { before: 0, after: 0, ...zeile(11.5) },
    children: [new TextRun({ text: e.sub, italics: true, font: "Montserrat", size: sz(15.5), color: GRAU })],
  }));
  return reihe(
    [new TextRun({ text: e.date, font: "Montserrat Light", size: sz(16), color: GRAU })],
    kinder, DATE_B, { vor: i === 0 ? 5 : 5.5, nach: 0 }
  );
}), DATE_B));

// Sprachen & Persönliches (kompakter Block zuerst) ...
const LBL_B = daten.skills_label_width || 3200;
inhalt.push(sektion(daten.skills_title || "Weitere Fähigkeiten und Kenntnisse"));
inhalt.push(tabelle(daten.skills.map(([label, wert], i) =>
  reihe(
    [new TextRun({ text: label, bold: true, font: "Montserrat", size: sz(16.5), color: DUNKEL })],
    [new Paragraph({ spacing: { before: 0, after: 0, ...zeile(13) }, children: hl(wert, { font: "Montserrat Light", size: sz(17), color: TEXT }) })],
    LBL_B, { vor: i === 0 ? 4 : 0, nach: 3 }
  )
), LBL_B));

// Ausführliche Skills-Liste ...
if (daten.skills_detail && daten.skills_detail.length) {
  inhalt.push(sektion(daten.skills_detail_title || "Kenntnisse & Skills"));
  if (daten.skills_detail_layout === "liste") {
    // Aufgeräumte Label-Wert-Liste (wie «Sprachen & Persönliches»).
    const lb = 3300;
    inhalt.push(tabelle(daten.skills_detail.map((s, i) =>
      reihe(
        [new TextRun({ text: s.title, bold: true, font: "Montserrat", size: sz(16.5), color: DUNKEL })],
        [new Paragraph({ spacing: { before: 0, after: 0, ...zeile(13) }, children: [new TextRun({ text: s.bullets.join(" · "), font: "Montserrat Light", size: sz(17), color: TEXT })] })],
        lb, { vor: i === 0 ? 4 : 0, nach: 3.5 }
      )
    ), lb));
  } else {
    inhalt.push(new Paragraph({ spacing: { before: 0, after: px(1), line: 12, lineRule: "exact" }, children: [] }));
    inhalt.push(skillsGrid(daten.skills_detail));
  }
}

// ... dann Erfolge & Kennzahlen als abschliessender Block (Label links, Wert rechts).
if (daten.kpis && daten.kpis.length) {
  inhalt.push(sektion(daten.kpi_title || "Erfolge & Kennzahlen"));
  const valW = 100 * PT;
  const n = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const linie = { style: BorderStyle.SINGLE, size: 4, color: "E4E4E4" };
  inhalt.push(new Paragraph({ spacing: { before: 0, after: px(3), line: 10, lineRule: "exact" }, children: [] }));
  inhalt.push(new Table({
    columnWidths: [INHALT_B - valW, valW],
    width: { size: INHALT_B, type: WidthType.DXA },
    borders: { top: n, bottom: n, left: n, right: n, insideVertical: n, insideHorizontal: linie },
    rows: daten.kpis.map(([k, v]) => new TableRow({
      children: [
        new TableCell({ width: { size: INHALT_B - valW, type: WidthType.DXA }, margins: { top: px(2.8), bottom: px(2.8), left: 0, right: 0 },
          children: [new Paragraph({ spacing: { before: 0, after: 0, ...zeile(13.5) }, children: [new TextRun({ text: k, font: "Montserrat Light", size: sz(17), color: TEXT })] })] }),
        new TableCell({ width: { size: valW, type: WidthType.DXA }, margins: { top: px(2.8), bottom: px(2.8), left: 0, right: 0 },
          children: [new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { before: 0, after: 0, ...zeile(13.5) }, children: [new TextRun({ text: v, bold: true, font: "Montserrat", size: sz(17), color: DUNKEL })] })] }),
      ],
    })),
  }));
  if (daten.kpi_note) inhalt.push(new Paragraph({
    spacing: { before: px(5), after: 0, ...zeile(12.6) },
    children: [new TextRun({ text: daten.kpi_note, font: "Montserrat Light", size: sz(15.5), color: GRAU })],
  }));
}

// Auszeichnungen & Zertifikate (optional) – volle Breite, goldene Bullets.
if (daten.awards && daten.awards.length) {
  inhalt.push(sektion(daten.awards_title || "Auszeichnungen & Zertifikate"));
  inhalt.push(new Paragraph({ spacing: { before: 0, after: px(2), line: 10, lineRule: "exact" }, children: [] }));
  daten.awards.forEach((a, i) => inhalt.push(bullet(a, i === 0)));
}

const fuss = new Footer({
  children: [new Paragraph({
    alignment: AlignmentType.RIGHT,
    spacing: { before: 0, after: 0 },
    children: [
      new TextRun({ text: "Lebenslauf – " + daten.name + "   ", font: "Montserrat Light", size: sz(14), color: GRAU }),
      new TextRun({ children: ["Seite ", PageNumber.CURRENT], font: "Montserrat Light", size: sz(14), color: GRAU }),
    ],
  })],
});

const doc = new Document({
  creator: daten.name,
  title: "Lebenslauf " + daten.name,
  description: "Lebenslauf " + daten.name + " – " + daten.role,
  sections: [{
    properties: { page: { margin: { top: M_TOP, right: M_LR, bottom: M_BOT, left: M_LR } } },
    footers: { default: fuss },
    children: inhalt,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(ausgabe, buf);
  console.log("geschrieben: " + ausgabe);
});
