#!/usr/bin/env node

const fs = require('fs');
const { execFileSync } = require('child_process');

const root = process.cwd();
const course = fs.readFileSync(`${root}/6141.md`, 'utf8');
const sessions = [...course.matchAll(/### Session (\d)\.(\d): ([^\n]+)([\s\S]*?)(?=\n---\n|\n## Module|\n<a id=|$)/g)]
  .map((match) => ({
    module: match[1],
    session: match[2],
    title: match[3],
    code: [...match[4].matchAll(/```python\n([\s\S]*?)```/g)].map((block) => block[1].trim()),
  }));

if (sessions.length !== 16) {
  throw new Error('Expected 16 sessions.');
}

function run(command, args) {
  execFileSync(command, args, { cwd: root, stdio: 'inherit' });
}

function dedentPython(source) {
  const lines = source.replace(/\r/g, '').split('\n');
  const indents = lines.filter((line) => line.trim()).map((line) => line.match(/^\s*/)[0].length);
  const margin = Math.min(...indents);
  return lines.map((line) => line.trim() ? line.slice(margin) : '').join('\n');
}

function drawText(image, text, x, y, pointSize, color, maxChars = 92) {
  const lines = text.split('\n').flatMap((line) => {
    if (line.length <= maxChars) return [line];
    const words = line.split(' ');
    const wrapped = [];
    let current = '';
    for (const word of words) {
      if (`${current} ${word}`.trim().length > maxChars) {
        wrapped.push(current);
        current = word;
      } else current = `${current} ${word}`.trim();
    }
    if (current) wrapped.push(current);
    return wrapped;
  });
  lines.forEach((line, index) => run('convert', [
    image, '-font', 'DejaVu-Sans-Mono', '-pointsize', String(pointSize), '-fill', color,
    '-annotate', `+${x}+${y + index * Math.round(pointSize * 1.45)}`, line, image,
  ]));
}

function repairCodeSlide(path, session, example, number) {
  run('convert', [path, '-fill', '#18181B', '-draw', 'rectangle 100,350 1170,950', path]);
  run('convert', [path, '-fill', '#FFFFFF', '-draw', 'rectangle 90,110 2310,245', path]);
  drawText(path, `Script Demonstration ${number}: ${session.title}`, 102, 175, 29, '#18181B', 94);
  const lines = example.split('\n').slice(0, 18).map((line) => line.length > 72 ? `${line.slice(0, 69)}...` : line);
  lines.forEach((line, index) => {
    const numberLabel = String(index + 1).padStart(2, ' ');
    drawText(path, `${numberLabel}  ${line}`, 190, 395 + index * 36, 22, '#E5E7EB', 85);
  });
}

function repairFoundationSlide(path) {
  run('convert', [path, '-fill', '#FFFFFF', '-draw', 'rectangle 130,350 995,560', path]);
  drawText(path, 'Core Programming & Computational Foundations', 140, 405, 23, '#18181B', 56);
  drawText(path, 'Trace execution step by step, use clear program structure, and diagnose errors from the traceback.', 140, 455, 18, '#4B5563', 72);
}

for (const session of sessions) {
  const directory = `${root}/assets/lecture_slides/session_${session.module}_${session.session}`;
  repairFoundationSlide(`${directory}/slide_3.png`);
  [5, 6, 7].forEach((page, index) => {
    const fallback = [
      `import pandas as pd\n\ndf = pd.read_csv("data/session_0${session.module}_0${session.session}_dataset.csv")\nprint(df.head())`,
      `summary = df.describe(include="all")\nprint(summary)`,
      `if df.empty:\n    raise ValueError("Dataset is empty")\nprint("Workflow completed: Exit 0")`,
    ][index];
    repairCodeSlide(`${directory}/slide_${page}.png`, session, dedentPython(session.code[index] || fallback), index + 1);
  });
  const pdf = `${root}/slides/session_0${session.module}_0${session.session}_lecture.pdf`;
  const pages = Array.from({ length: 8 }, (_, index) => `${directory}/slide_${index + 1}.png`);
  run('convert', [
    ...pages, '-units', 'PixelsPerInch', '-density', '150',
    '-compress', 'Zip', pdf,
  ]);
}
