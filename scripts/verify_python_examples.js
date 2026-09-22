#!/usr/bin/env node

const fs = require('fs');
const { execFileSync } = require('child_process');

const source = fs.readFileSync('6141.md', 'utf8');
const blocks = [...source.matchAll(/```python\n([\s\S]*?)```/g)].map((match, index) => ({ index: index + 1, source: match[1] }));

function dedentPython(code) {
  const lines = code.replace(/\r/g, '').split('\n');
  const indents = lines.filter((line) => line.trim()).map((line) => line.match(/^\s*/)[0].length);
  const margin = Math.min(...indents);
  return lines.map((line) => line.trim() ? line.slice(margin) : '').join('\n');
}

const failures = [];
for (const block of blocks) {
  try {
    execFileSync('python3', ['-c', 'import sys; compile(sys.stdin.read(), "example.py", "exec")'], {
      input: dedentPython(block.source),
      stdio: ['pipe', 'pipe', 'pipe'],
    });
  } catch (error) {
    failures.push(`Block ${block.index}: ${error.stderr.toString().trim()}`);
  }
}

if (failures.length) throw new Error(failures.join('\n\n'));
console.log(`Verified ${blocks.length} Python code blocks: syntax and indentation are valid after Markdown dedenting.`);
