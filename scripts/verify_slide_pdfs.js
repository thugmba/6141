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
  const source = path.join(root, 'slides_src', file.replace('_lecture.pdf', '.html'));
  const expected = (fs.readFileSync(source, 'utf8').match(/<section class="slide"/g) || []).length;
  const info = execFileSync('pdfinfo', [pdf], { encoding: 'utf8' });
  const images = execFileSync('pdfimages', ['-list', pdf], { encoding: 'utf8' });
  if (!new RegExp(`Pages:\\s+${expected}\\b`).test(info)) throw new Error(`${file}: expected ${expected} pages to match its HTML source.`);
  if (!/Page size:\s+1152 x 648 pts/.test(info)) throw new Error(`${file}: expected 16:9 1152 x 648pt pages.`);
  const embedded = images.split('\n')
    .map((line) => line.trim().split(/\s+/))
    .filter((columns) => columns[2] === 'image');
  // Full-page raster slides are 2400 x 1350; smaller images are in-slide content such as screenshots.
  const rasterPages = embedded.filter((columns) => columns[3] === '2400' && columns[4] === '1350');
  if (rasterPages.length && (rasterPages.length !== expected || rasterPages.some((columns) => columns[12] !== '150' || columns[13] !== '150'))) {
    throw new Error(`${file}: raster PDF pages must contain ${expected} 2400 x 1350 images at 150dpi.`);
  }
}

console.log(`Verified ${files.length} lecture PDFs: page count matching each HTML source, 1152 x 648pt, with vector output or 2400 x 1350 raster pages at 150dpi.`);
