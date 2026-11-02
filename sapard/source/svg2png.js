// Convertit les SVG d'un dossier en PNG (x1,6) avec Chromium.  node svg2png.js <dossier>
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const dir = process.argv[2]; const b = await chromium.launch(); const pg = await b.newPage({ deviceScaleFactor: 1.6 });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const m = svg.match(/width="([\d.]+)" height="([\d.]+)"/); const w = +m[1], h = +m[2];
    await pg.setViewportSize({ width: Math.ceil(w), height: Math.ceil(h) });
    await pg.setContent(`<html><body style="margin:0">${svg}</body></html>`);
    await pg.screenshot({ path: path.join(dir, f.replace('.svg', '.png')), clip: { x: 0, y: 0, width: w, height: h } });
    console.log(f);
  }
  await b.close();
})();
