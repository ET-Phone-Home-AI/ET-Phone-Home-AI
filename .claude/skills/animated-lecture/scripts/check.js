#!/usr/bin/env node
// Usage: node check.js deck.html [outdir]
// Opens the deck headless, plays every box of every slide to its end, saves one PNG per slide,
// and reports JavaScript errors. Exit code 1 if anything failed.
const path = require('path'); const fs = require('fs');
let chromium; try { ({ chromium } = require('playwright')); } catch (e) { console.error('playwright is not installed here; open the file in a browser and step through it by hand instead.'); process.exit(2); }
(async () => {
  const file = path.resolve(process.argv[2] || 'deck.html'); const out = path.resolve(process.argv[3] || path.dirname(file)); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(2500);
  const n = await p.evaluate(() => window.__deck ? window.__deck.count : -1);
  if (n < 1) { console.error('FAIL: the deck did not start (no slides, or a script error):', errs); await b.close(); process.exit(1); }
  for (let i = 0; i < n; i++) {
    const ds = await p.evaluate(i => { window.__deck.go(i); return window.__deck.boxes(i); }, i);
    for (let k = 0; k < ds.length; k++) {
      if (k > 0) await p.evaluate(() => window.__deck.next());
      for (const frac of [0.25, 0.5, 0.75, 1]) { await p.evaluate(s => window.__deck.shift(s), ds[k] * 0.25 + (frac === 1 ? 0.3 : 0)); await p.waitForTimeout(120); }
    }
    await p.waitForTimeout(300); const shot = path.join(out, `slide-${i + 1}.png`); await p.screenshot({ path: shot });
    console.log(`slide ${i + 1}/${n}: ${ds.length} box(es), durations ${ds.join(' + ')} s -> ${shot}`);
  }
  await b.close();
  if (errs.length) { console.error('FAIL: errors while playing:\n' + [...new Set(errs)].join('\n')); process.exit(1); }
  console.log('OK: every box played to the end with no errors. Look at the PNGs for overlaps and text running off the box.');
})();
