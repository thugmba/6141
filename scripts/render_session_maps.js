#!/usr/bin/env node

// Renders a session map image (assets/session_MM_SS_map.png) for every session in
// 6141.md whose learning sections are numbered ("* **1. Session Purpose:**" ... "* **13. ...").
const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const root = process.cwd();
const course = fs.readFileSync(path.join(root, '6141.md'), 'utf8');
const sessions = [...course.matchAll(/### Session (\d)\.(\d): ([^\n]+)([\s\S]*?)(?=\n---\n|\n## Module|\n<a id=|\n### Session|$)/g)];
const escape = (text) => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const plain = (text) => text.replace(/`/g, '').replace(/\*+/g, '').trim();

const shortName = (number, heading) => {
  const name = heading.replace(/\s*\(.*\)\s*/, ' ').replace(/:\s*$/, '').trim();
  if (number === 2) return 'Learning Outcomes';
  if (name.startsWith('Core Programming')) return 'Core Foundations';
  if (name.startsWith('Development Workflow')) return 'IDE Workflow';
  if (name.startsWith('Hands-On Coding')) return 'Code Examples + Quick Checks';
  if (name.startsWith('Official')) return 'Official References';
  if (name.startsWith('Business Context')) return name.replace('Business Context: ', 'Business Context: ');
  return name.replace(/^Exercise (\d): (Guided|Applied|Advanced) Practice - /, 'Exercise $1: $2 - ');
};

const phases = [
  { title: 'Why it matters', time: 'Lecture, part 1', range: [1, 4] },
  { title: 'Learn the tools', time: 'Lecture, part 2', range: [5, 10] },
  { title: 'Practice', time: 'Lab', range: [11, 13] },
];

const page = (id, title, question, items) => `<!doctype html><html lang="en-US"><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0}
.map{width:1920px;height:1080px;background:#FFFFFF;padding:70px 96px 56px;display:flex;flex-direction:column;font-family:"Times New Roman",serif;color:#18181B}
.eyebrow{color:#991B1B;font-size:26px;font-weight:bold;letter-spacing:.04em}
h1{font-size:54px;line-height:1.1;margin:10px 0 0}
.rule{width:150px;height:5px;background:#991B1B;margin:18px 0 26px}
.question{border:3px solid #991B1B;border-radius:18px;padding:18px 28px;font-size:34px;font-style:italic;background:#FEF2F2;align-self:flex-start;max-width:1700px}
.question b{font-style:normal;color:#991B1B;margin-right:12px}
.phases{flex:1;min-height:0;display:flex;gap:22px;margin-top:30px;align-items:stretch}
.phase{flex:1;border:2px solid #CBD5E1;border-radius:16px;padding:22px 26px;display:flex;flex-direction:column}
.phase.p3{border:3px solid #15803D;background:#F0FDF4}
.phase-head{display:flex;align-items:center;gap:16px;border-bottom:2px solid #E2E8F0;padding-bottom:14px;margin-bottom:16px}.phase-name{display:flex;flex-direction:column}
.step{background:#991B1B;color:#FFF;border-radius:50%;width:46px;height:46px;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:bold;flex-shrink:0;align-self:center}
.p3 .step{background:#15803D}
.phase-title{font-size:40px;font-weight:bold;line-height:1.1}
.time{font-size:24px;color:#64748B}
.item{display:flex;gap:16px;font-size:33px;line-height:1.25;padding:11px 0}
.num{font-family:"DejaVu Sans Mono",monospace;font-weight:bold;color:#991B1B;min-width:58px;text-align:right}
.p3 .num{color:#15803D}
.arrow{align-self:center;font-size:54px;color:#991B1B}
.foot{margin-top:22px;font-size:22px;color:#64748B;display:flex;justify-content:space-between}
</style><body><div class="map">
<div class="eyebrow">SESSION ${id} &#183; SESSION MAP</div>
<h1>${escape(title)}</h1><div class="rule"></div>
<div class="question"><b>Today's question:</b>${escape(question)}</div>
<div class="phases">${phases.map((phase, index) => `${index ? '<div class="arrow">&#8594;</div>' : ''}<div class="phase p${index + 1}">
<div class="phase-head"><span class="step">${index + 1}</span><span class="phase-name"><span class="phase-title">${phase.title}</span><span class="time">${phase.time}</span></span></div>
${items.filter((item) => item.number >= phase.range[0] && item.number <= phase.range[1]).map((item) => `<div class="item"><span class="num">${item.number}.</span><span>${escape(item.name)}</span></div>`).join('')}
</div>`).join('')}</div>
<div class="foot"><span>Business Analytics &amp; AI Application | Course 6141</span><span>Lecture 60 min + Lab 120 min &#183; Follow the numbers in each session</span></div>
</div></body></html>`;

(async () => {
  const browser = await chromium.launch({ headless: true });
  const tab = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const stage = fs.mkdtempSync(path.join(require('os').tmpdir(), 'session-map-'));
  let count = 0;
  for (const match of sessions) {
    const [, module, session, title, body] = match;
    const items = [...body.matchAll(/^\* \*\*(\d+)\. ([^*]+)\*\*/gm)].map((m) => ({ number: Number(m[1]), name: shortName(Number(m[1]), plain(m[2])) }));
    if (items.length !== 13) continue;
    const asks = body.match(/asks: ([^?]+\?)/);
    if (!asks) throw new Error(`Session ${module}.${session}: Session Purpose needs a "... asks: <question>?" line for the map.`);
    const question = asks[1].charAt(0).toUpperCase() + asks[1].slice(1);
    const file = path.join(stage, `map_${module}_${session}.html`);
    fs.writeFileSync(file, page(`${module}.${session}`, title, question, items));
    await tab.goto(pathToFileURL(file).href);
    await tab.evaluate(() => document.fonts.ready);
    const overflow = await tab.evaluate(() => [...document.querySelectorAll('.phase, .question, h1')].some((el) => el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1));
    if (overflow) throw new Error(`Session ${module}.${session}: map content overflows its box.`);
    await tab.screenshot({ path: path.join(root, 'assets', `session_0${module}_0${session}_map.png`) });
    count += 1;
  }
  await browser.close();
  console.log(`Rendered ${count} session map images (1920 x 1080).`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
