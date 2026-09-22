#!/usr/bin/env node

const fs = require('fs');

const course = fs.readFileSync('6141.md', 'utf8');
const sessions = [...course.matchAll(/### Session (\d)\.(\d): ([^\n]+)([\s\S]*?)(?=\n---\n|\n## Module|\n<a id=|$)/g)];
const escape = (text) => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const plain = (text) => text.replace(/`/g, '').replace(/\*+/g, '').replace(/\[[^\]]+\]\([^)]*\)/g, '').replace(/\s+/g, ' ').trim();
const dedent = (code) => {
  const lines = code.trim().split('\n');
  const margin = Math.min(...lines.filter((line) => line.trim()).map((line) => line.match(/^\s*/)[0].length));
  return lines.map((line) => line.trim() ? line.slice(margin) : '').join('\n');
};
const page = (content, n) => `<section class="slide">${content}<footer>Business Analytics &amp; AI Application | Course 6141 <span>Slide ${n} / 8</span></footer></section>`;
const card = (label, title, text) => `<article><b>${escape(label)}</b><h2>${escape(title)}</h2><p>${escape(text)}</p></article>`;
const codeSlide = (title, code, n) => page(`<header><b>MODULE</b><span>Style 2 Harvard Dual-Pane Editor</span></header><h1>${escape(title)}</h1><i></i><main class="code"><pre>${escape(code)}</pre><aside>${card('SYNTAX', 'Readable Structure', 'Observe the syntax and indentation that control execution.')}${card('RUNTIME', 'Verified Execution', 'Run the example in the integrated terminal and inspect the output.')}${card('BUSINESS VALUE', 'Applied Automation', 'Use the pattern to automate a repeatable business decision.')}</aside></main>`, n);

for (const match of sessions) {
  const module = match[1]; const session = match[2]; const title = match[3]; const body = match[4];
  const id = `0${module}_0${session}`;
  if (id === '01_02') continue;
  const keywordBlock = (body.match(/\* \*\*Keywords[^\n]*\n([\s\S]*?)\n\* \*\*Core/) || [, ''])[1];
  const coreBlock = (body.match(/\* \*\*Core[^\n]*\n([\s\S]*?)\n\* \*\*Hands-On/) || [, ''])[1];
  const keywords = keywordBlock.split('\n').filter((line) => /^\s*\*/.test(line)).slice(0, 4).map(plain);
  const foundations = coreBlock.split('\n').filter((line) => /^\s*\*/.test(line)).slice(0, 4).map(plain);
  const codes = [...body.matchAll(/```python\n([\s\S]*?)```/g)].map((block) => dedent(block[1]));
  while (codes.length < 3) codes.push('print("Session practice: verify execution")');
  const html = `<!doctype html><html lang="en-US"><meta charset="utf-8"><title>Session ${module}.${session}</title><style>
@page{size:16in 9in;margin:0}*{box-sizing:border-box}body{margin:0;font-family:"Times New Roman",serif;color:#18181B}.slide{width:16in;height:9in;padding:.45in .8in .4in;display:flex;flex-direction:column;background:#fff;page-break-after:always}header{font-size:15pt;color:#991B1B;font-weight:bold}header span{margin-left:.25in;color:#64748B;font-weight:normal}h1{font-size:34pt;line-height:1.08;margin:.13in 0 .08in}h2{font-size:21pt;margin:.06in 0}.slide>i{display:block;width:1.2in;height:4px;background:#991B1B;margin-bottom:.2in}main{flex:1;min-height:0;display:grid;grid-template-columns:repeat(2,1fr);gap:.2in}main.three{grid-template-columns:repeat(3,1fr);gap:.18in}article{border:1px solid #CBD5E1;border-radius:10px;padding:.18in;overflow:hidden}article b{font-size:14pt;color:#991B1B}p,li{font-size:17pt;line-height:1.25;margin:.06in 0}footer{margin-top:.18in;border-top:1px solid #CBD5E1;padding-top:.1in;font-size:15pt;color:#64748B;display:flex;justify-content:space-between}.code{display:flex;gap:.3in}.code pre{width:58%;margin:0;background:#18181B;border-radius:10px;color:#E5E7EB;padding:.22in;font:13.5pt/1.28 "DejaVu Sans Mono",monospace;white-space:pre-wrap;overflow-wrap:anywhere;overflow:hidden}.code aside{flex:1;display:flex;flex-direction:column;gap:.13in}.code aside article{flex:1}</style><body>
${page(`<header><b>MODULE ${module}</b><span>Session Overview</span></header><h1>Session ${module}.${session}: ${escape(title)}</h1><i></i><main>${card('1:2 DELIVERY RHYTHM','Applied Learning','60 minutes of focused instruction followed by 120 minutes of guided coding and debugging.')}${card('SESSION OUTCOME','Operational Competency','Students apply the session concept to a small, verifiable business dataset.')}</main>`,1)}
${page(`<header><b>MODULE ${module}</b><span>Core Vocabulary</span></header><h1>Concepts for This Session</h1><i></i><main class="three">${keywords.map((item, index) => card(`CONCEPT ${index + 1}`, item.split(':')[0], item.split(':').slice(1).join(':') || 'Core programming concept.')).join('')}</main>`,2)}
${page(`<header><b>MODULE ${module}</b><span>Computational Foundations</span></header><h1>How the Concept Works in Practice</h1><i></i><main>${foundations.map((item, index) => card(`FOUNDATION ${index + 1}`, item.split(':')[0], item.split(':').slice(1).join(':'))).join('')}</main>`,3)}
${page(`<header><b>MODULE ${module}</b><span>Development Workflow</span></header><h1>Build, Test, and Diagnose in the IDE</h1><i></i><main>${card('[1] FILE EXPLORER','Organize Assets','Use the session dataset and keep scripts in a clear workspace.')}${card('[2] CODE EDITOR','Write Small Segments','Run each completed segment before expanding the program.')}${card('[3] AI AGENT CHAT','Diagnose Errors','Capture the traceback, request an explanation, and review the fix.')}${card('[4] INTEGRATED TERMINAL','Verify Execution','Confirm the final program completes with return code 0.')}</main>`,4)}
${codeSlide(`Script Demonstration 1: ${title}`, codes[0], 5)}${codeSlide(`Script Demonstration 2: ${title}`, codes[1], 6)}${codeSlide(`Script Demonstration 3: ${title}`, codes[2], 7)}
${page(`<header><b>MODULE ${module}</b><span>Hands-On Practice</span></header><h1>Exercise 1 and Exercise 2</h1><i></i><main>${card('EXERCISE 1: GUIDED','Foundational Practice','Follow the lab protocol, run the script, and verify its output with the session dataset.')}${card('EXERCISE 2: DEBUGGING','Applied Challenge','Extend the program, diagnose an intentional error, apply the verified correction, and confirm return code 0.')}</main>`,8)}</body></html>`;
  fs.writeFileSync(`slides_src/session_${id}.html`, html);
}
console.log(`Generated HTML sources for ${sessions.length - 1} sessions; Session 1.2 retains its authored source.`);
