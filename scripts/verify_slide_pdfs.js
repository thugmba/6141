#!/usr/bin/env node

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const root = process.cwd();
const directory = path.join(root, 'slides');
const files = fs.readdirSync(directory)
  .filter((file) => /^session_\d{2}_\d{2}_lecture\.pdf$/.test(file))
  .sort();

if (files.length !== 16) throw new Error(`Expected 16 lecture PDFs, found ${files.length}.`);

for (const file of files) {
  const pdf = path.join(directory, file);
  const info = execFileSync('pdfinfo', [pdf], { encoding: 'utf8' });
  const images = execFileSync('pdfimages', ['-list', pdf], { encoding: 'utf8' });
  if (!/Pages:\s+8\b/.test(info)) throw new Error(`${file}: expected 8 pages.`);
  if (!/Page size:\s+1152 x 648 pts/.test(info)) throw new Error(`${file}: expected 16:9 1152 x 648pt pages.`);
  const embedded = images.split('\n')
    .map((line) => line.trim().split(/\s+/))
    .filter((columns) => columns[2] === 'image');
  if (embedded.length && (embedded.length !== 8 || embedded.some((columns) => columns[3] !== '2400' || columns[4] !== '1350' || columns[12] !== '150' || columns[13] !== '150'))) {
    throw new Error(`${file}: raster PDF pages must contain eight 2400 x 1350 images at 150dpi.`);
  }
}

console.log(`Verified ${files.length} lecture PDFs: 8 pages each, 1152 x 648pt, with vector output or 2400 x 1350 raster pages at 150dpi.`);
