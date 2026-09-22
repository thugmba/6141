#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { chromium } = require('playwright');

const sessionId = process.argv[2];
if (!/^\d{2}_\d{2}$/.test(sessionId || '')) {
  throw new Error('Usage: node scripts/render_with_playwright.js MM_SS');
}

const root = process.cwd();
const [moduleNumber, sessionNumber] = sessionId.split('_').map((value) => Number(value));
const source = path.join(root, 'slides_src', `session_${sessionId}.html`);
const pdf = path.join(root, 'slides', `session_${sessionId}_lecture.pdf`);
const pageDirectory = path.join(root, 'assets', 'lecture_slides', `session_${moduleNumber}_${sessionNumber}`);

if (!fs.existsSync(source)) throw new Error(`Missing HTML source: ${source}`);

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 2400, height: 1350 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(source).href, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const slides = page.locator('.slide');
  const count = await slides.count();
  if (count !== 8) throw new Error(`${source} must contain exactly 8 .slide elements; found ${count}.`);

  await page.pdf({ path: pdf, width: '16in', height: '9in', preferCSSPageSize: true, printBackground: true });
  for (let index = 0; index < count; index += 1) {
    await slides.nth(index).screenshot({ path: path.join(pageDirectory, `slide_${index + 1}.png`) });
  }
  fs.copyFileSync(path.join(pageDirectory, 'slide_1.png'), path.join(root, 'assets', `session_${sessionId}_slide.png`));
  await browser.close();
  console.log(`Rendered Session ${moduleNumber}.${sessionNumber}: vector PDF plus ${count} 2400 x 1350 PNG previews.`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
