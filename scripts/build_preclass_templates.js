// Builds the A4 Word report templates of the pre-class homework for Sessions 3.3 and 3.4.
// Usage (needs the docx package: npm install docx):
//   node scripts/build_preclass_templates.js homework/preclass_session_03_03_template.docx 33
//   node scripts/build_preclass_templates.js homework/preclass_session_03_04_template.docx 34

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, ImageRun, AlignmentType, HeadingLevel, Footer, PageNumber, LevelFormat, HeightRule,
  VerticalAlign, TableLayoutType, ExternalHyperlink,
} = require("docx");

const FONT = "Times New Roman";
const MONO = "Consolas";
const W = 9638; // A4 text width with 2.2 cm side margins (11906 - 2 * 1134)
const RED = "991B1B";
const GREY = "64748B";
const LINE = { style: BorderStyle.SINGLE, size: 6, color: "94A3B8" };
const BOX = { style: BorderStyle.DASHED, size: 8, color: "94A3B8" };
const borders = (b) => ({ top: b, bottom: b, left: b, right: b });

// inline `code` becomes a monospace run
const runs = (text, opts = {}) => text.split(/(`[^`]+`)/).filter(Boolean).map((part) =>
  part.startsWith("`")
    ? new TextRun({ text: part.slice(1, -1), font: MONO, size: (opts.size || 22) - 2, ...opts, bold: false })
    : new TextRun({ text: part, ...opts }));

const p = (text, opts = {}, para = {}) => new Paragraph({ children: runs(text, opts), spacing: { after: 80 }, ...para });
const bullet = (text) => new Paragraph({ children: runs(text), numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 } });

const cell = (children, width, extra = {}) => new TableCell({
  children: Array.isArray(children) ? children : [children],
  width: { size: width, type: WidthType.DXA },
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  verticalAlign: VerticalAlign.CENTER,
  ...extra,
});

// a labeled answer row: label on the left, empty space to type on the right
const answerTable = (rows, labelWidth = 3200) => new Table({
  width: { size: W, type: WidthType.DXA },
  columnWidths: [labelWidth, W - labelWidth],
  layout: TableLayoutType.FIXED,
  rows: rows.map(([label, hint]) => new TableRow({
    cantSplit: true,
    height: { value: 560, rule: HeightRule.ATLEAST },
    children: [
      cell(p(label, { bold: true }, { spacing: { after: 0 } }), labelWidth,
        { shading: { type: ShadingType.CLEAR, color: "auto", fill: "F1F5F9" }, borders: borders(LINE) }),
      cell(p(hint || "", { color: GREY, italics: true }, { spacing: { after: 0 } }), W - labelWidth, { borders: borders(LINE) }),
    ],
  })),
});

// a dashed box to paste a screenshot into
const shotBox = (label, heightCm = 6.5) => new Table({
  width: { size: W, type: WidthType.DXA },
  columnWidths: [W],
  layout: TableLayoutType.FIXED,
  rows: [new TableRow({
    cantSplit: true,
    height: { value: Math.round(heightCm * 567), rule: HeightRule.ATLEAST },
    children: [cell([].concat(label).map((line, i) => p(i === 0 ? `Paste screenshot here: ${line}` : line,
      { color: GREY, italics: true }, { alignment: AlignmentType.CENTER, spacing: { after: 40 } })),
      W, { borders: borders(BOX) })],
  })],
});

// a table with a header row and empty rows to fill in
const gridTable = (headers, widths, nRows, firstCol) => new Table({
  width: { size: W, type: WidthType.DXA },
  columnWidths: widths,
  layout: TableLayoutType.FIXED,
  rows: [
    new TableRow({
      tableHeader: true,
      children: headers.map((h, i) => cell(p(h, { bold: true }, { spacing: { after: 0 } }), widths[i],
        { shading: { type: ShadingType.CLEAR, color: "auto", fill: "F1F5F9" }, borders: borders(LINE) })),
    }),
    ...Array.from({ length: nRows }, (_, r) => new TableRow({
      cantSplit: true,
      height: { value: 520, rule: HeightRule.ATLEAST },
      children: widths.map((w, i) => cell(p(i === 0 && firstCol ? firstCol(r) : "", {}, { spacing: { after: 0 } }), w, { borders: borders(LINE) })),
    })),
  ],
});

const gap = () => new Paragraph({ spacing: { after: 120 }, children: [] });
const heading = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(text, { font: FONT, size: 28, bold: true, color: RED }) });
const submit = (text) => p(`Submit: ${text}`, {}, { spacing: { after: 120 } });
const note = (text) => p(text, { italics: true }, { spacing: { after: 120 } });


// ---- pre-class report templates ----
const which = process.argv[3];
const S = {
  "33": {
    title: "Before Session 3.3: Pre-Class Report", guide: "preclass_session_03_03.pdf",
    due: "Due: Tuesday, November 24, 2026, 5 pm (Taiwan time), on iLearn", file: "StudentID_Name_PreClass_S33.pdf",
    example: "S11312345_JohnSmith_PreClass_S33.pdf",
    pages: [
      [["Task 1: Check Your Tools", "a screenshot of the four version lines.", [shotBox("python YourName_P33_task1.py", 4)]],
       ["Task 2: Load the Data and Look at It", "a screenshot of the output and three answers.", [shotBox("python YourName_P33_task2.py", 5.5), gap(),
         answerTable([["Which column is the target?", "one column name"], ["Which columns are the features?", "two column names"], ["How many days are weekends?", "a number"]], 4200)]]],
      [["Task 3: Draw a Scatter Plot", "the picture itself and your answer.", [shotBox("drinks_scatter.png (insert the picture file: Insert > Pictures)", 7), gap(),
         answerTable([["What happens to sales when it gets hotter? Do some dots sit above the others?", "one or two sentences"]], 4200)]],
       ["Task 4: Predict by Hand", "the completed table, the MAE, and one sentence.", [
         note("Formula: cups = -15.3 + 5.51 x temperature. Round to 1 decimal."),
         gridTable(["Day", "Temp", "Predicted cups", "Actual", "Error (predicted - actual)"], [1500, 1000, 2900, 1200, W - 6600], 4, (r) => ["DAY-01", "DAY-02", "DAY-06", "DAY-15"][r]),
         gap(), answerTable([["MAE (show the calculation)", "(|e1| + |e2| + |e3| + |e4|) / 4 = ..."], ["What does 5.51 mean for the drink stand?", "one sentence"]], 4200)]]],
      [["Task 5: Train and Test a Model in Python", "a screenshot of the output and two sentences.", [shotBox("python YourName_P33_task5.py", 8), gap(),
         answerTable([["Do the numbers match your hand calculation in Task 4?", "one sentence"], ["Is the model worth using, compared with guessing the average?", "one sentence"]], 4200)]]],
      [["Task 6: Add a Second Clue", "a screenshot of the output and two sentences.", [shotBox("python YourName_P33_task6.py", 7), gap(),
         answerTable([["What does 22.81 mean?", "one sentence"], ["Why did the typical error fall from 16.3 to 4.2?", "one or two sentences"]], 4200)]]],
    ],
  },
  "34": {
    title: "Before Session 3.4: Pre-Class Report", guide: "preclass_session_03_04.pdf",
    due: "Due: Tuesday, December 1, 2026, 5 pm (Taiwan time), on iLearn", file: "StudentID_Name_PreClass_S34.pdf",
    example: "S11312345_JohnSmith_PreClass_S34.pdf",
    pages: [
      [["Task 1: Rank the Orders by Their Chance", "a screenshot of the output and one sentence.", [shotBox("python YourName_P34_task1.py", 8), gap(),
         answerTable([["Is the ranking perfect? Name one late order with a chance below 0.5.", "one sentence"]], 4200)]]],
      [["Task 2: Count the Four Cases by Hand", "the confusion matrix at threshold 0.5 and three calculations.", [
         gridTable(["Threshold 0.5", "Warning shown", "No warning"], [3200, 3200, W - 6400], 2, (r) => ["Really late", "Really on time"][r]),
         gap(), answerTable([["Accuracy", "(caught + left alone) / 16 = ..."], ["Precision", "caught / (caught + false alarms) = ..."], ["Recall", "caught / (caught + missed) = ..."]], 2600)]],
       ["Task 3: Let Python Count and Score", "a screenshot of the output and one sentence.", [shotBox("python YourName_P34_task3.py", 4.5), gap(),
         answerTable([["Did Python agree with your hand count?", "one sentence"]], 4200)]]],
      [["Task 4: Move the Threshold", "a screenshot of the output and two sentences.", [shotBox("python YourName_P34_task3.py with threshold = 0.3", 4.5), gap(),
         answerTable([["What improved, and what got worse?", "one sentence"], ["If a late order without a warning makes customers very angry, which threshold would you choose?", "one sentence"]], 4200)]],
       ["Task 5: The Accuracy Trap", "a screenshot of the output and one sentence.", [shotBox("python YourName_P34_task5.py", 3), gap(),
         answerTable([["What is the recall of \"never warn\", and why does accuracy not show the problem?", "one sentence"]], 4200)]]],
      [["Task 6: Find Groups Without the Answers (K-Means)", "a screenshot of the output and two sentences.", [shotBox("python YourName_P34_task6.py", 5), gap(),
         answerTable([["A short name for each group", "Group 0: ...   Group 1: ..."], ["Which group should the app watch most closely, and why?", "one sentence"]], 4200)]]],
    ],
  },
}[which];

const children = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: S.title, font: FONT, size: 36, bold: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "Course 6141: Business Analytics and AI Application", font: FONT, size: 22, color: GREY })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: S.due, font: FONT, size: 24, bold: true, color: RED })] }),
  answerTable([["Name (in English letters)", "e.g., John Smith"], ["Student ID", ""], ["Computer", "Mac Apple Silicon / Mac Intel / Windows (delete the others)"], ["Date submitted", ""]], 3600),
  gap(),
  new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs("How to complete and submit", { size: 24, bold: true }) }),
  bullet(`Follow the guide \`${S.guide}\` (course page). Do the six tasks in order; each task says what goes into this report.`),
  bullet("The grey text in each box and table is only a hint: click it, delete it, then paste or type in its place."),
  bullet("Screenshots must be readable: capture only the Terminal, with the text made bigger first (Python Setup Clinic, How to Take a Readable Screenshot)."),
  bullet("Fill in this template in Microsoft Word only (not Pages or Google Docs). Word is free for Tunghai University students."),
  new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 40 }, children: [
    new TextRun("Download Word from "),
    new ExternalHyperlink({ link: "https://software.thu.edu.tw/new/", children: [new TextRun({ text: "https://software.thu.edu.tw/new/", style: "Hyperlink" })] }),
    new TextRun(" (Microsoft campus license)."),
  ] }),
  bullet(`When finished, save it as PDF in Word (File > Save As, then choose PDF) named \`${S.file}\`, for example \`${S.example}\`, and upload it to iLearn by the deadline above.`),
  bullet("Stuck on a task? Do not leave it blank: write the error and what you tried in the box at the end, and bring the same laptop to class."),
];

S.pages.forEach((page) => {
  page.forEach(([title, sub, body], i) => {
    children.push(new Paragraph({ pageBreakBefore: i === 0, heading: HeadingLevel.HEADING_1, children: runs(title, { font: FONT, size: 28, bold: true, color: RED }) }));
    children.push(submit(sub));
    children.push(...body);
    children.push(gap());
  });
});
children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs("Where I got stuck, and my questions for class (optional)", { size: 24, bold: true }) }));
children.push(answerTable([["Task, error, and what I tried", ""], ["A question I want to ask in class", ""]], 3600));

const doc = new Document({
  creator: "Course 6141", title: S.title,
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 28, bold: true, color: RED }, paragraph: { spacing: { before: 120, after: 80 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 24, bold: true }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text: `Course 6141 | ${S.title} | Page `, size: 18, color: GREY }),
      new TextRun({ children: [PageNumber.CURRENT], size: 18, color: GREY }),
    ] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(process.argv[2], buf); console.log("wrote", process.argv[2]); });
