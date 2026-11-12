/* Titres du haut de page : sur téléphone, aussi grands que la largeur le permet.
   Chaque ligne du titre est agrandie jusqu'à toucher les deux marges (le titre peut passer sur plusieurs lignes). */
(() => {
  const SEL = '.hero h1, .hero .titres span';
  const widest = el => {
    const r = document.createRange(); r.selectNodeContents(el);
    const rows = {};
    for (const b of r.getClientRects()) {                  // une boîte par morceau de ligne : on additionne par ligne
      const k = Math.round(b.top);
      rows[k] = rows[k] ? { l: Math.min(rows[k].l, b.left), r: Math.max(rows[k].r, b.right) } : { l: b.left, r: b.right };
    }
    return Math.max(0, ...Object.values(rows).map(x => x.r - x.l));
  };
  const fit = () => {
    const narrow = matchMedia('(max-width: 700px)').matches;
    document.querySelectorAll(SEL).forEach(el => {
      el.style.fontSize = '';
      if (!narrow) return;
      const wrap = el.closest('.wrap'); if (!wrap) return;
      const cs = getComputedStyle(wrap);
      const avail = wrap.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      for (let i = 0; i < 4; i++) {
        const w = widest(el); if (!w) return;
        const fs = parseFloat(getComputedStyle(el).fontSize);
        el.style.fontSize = Math.min(fs * avail * 0.97 / w, 260) + 'px';
      }
    });
  };
  const run = () => (document.fonts ? document.fonts.ready : Promise.resolve()).then(fit);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
  let t; addEventListener('resize', () => { clearTimeout(t); t = setTimeout(fit, 120); });
})();
