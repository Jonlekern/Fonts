// Pour chaque police de l'accueil : le texte qu'elle affiche (toutes les cartes, téléphone et ordi, clair et sombre). Appelé par outils/accueil.py.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const out = {};
  for (const w of [390, 1280]) for (const scheme of ['light', 'dark']) {
    const p = await b.newPage({ viewport: { width: w, height: 900 }, colorScheme: scheme });
    await p.goto(process.argv[3], { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const m = {};
      const tf = (t, cs) => cs.textTransform === 'uppercase' ? t.toUpperCase() : cs.textTransform === 'lowercase' ? t.toLowerCase() : t;
      document.querySelectorAll('[hidden]').forEach(e => e.removeAttribute('hidden'));
      const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walk.nextNode()) {
        const n = walk.currentNode; if (!n.textContent.trim()) continue; const el = n.parentElement; const cs = getComputedStyle(el);
        const k = [cs.fontFamily, cs.fontWeight, cs.fontStyle].join('|'); m[k] = (m[k] || '') + tf(n.textContent, cs);
      }
      return m;
    });
    for (const [k, v] of Object.entries(r)) out[k] = (out[k] || '') + v;
    await p.close();
  }
  for (const k in out) out[k] = [...new Set(out[k])].sort().join('');
  require('fs').writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
  await b.close();
})();
