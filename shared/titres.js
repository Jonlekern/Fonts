/* Titres sur téléphone : aussi grands que la largeur le permet.
   - en haut des pages : le nom de la police et les mots d'exemple touchent les deux marges ;
   - sur l'accueil : le nom de chaque police touche les deux bords de sa carte.
   Chaque ligne est agrandie jusqu'aux bords (un titre peut passer sur plusieurs lignes). */
(() => {
  const RULES = [
    ['.hero h1, .hero .titres span', el => el.closest('.wrap')],
    ['.font-card .name', el => el]                         // la place du nom : sa propre colonne (sans ses marges invisibles)
  ];
  const widest = el => {
    const r = document.createRange(); r.selectNodeContents(el);
    const rows = {};
    for (const b of r.getClientRects()) {                  // une boîte par morceau de ligne : on regroupe par ligne
      const k = Math.round(b.top);
      rows[k] = rows[k] ? { l: Math.min(rows[k].l, b.left), r: Math.max(rows[k].r, b.right) } : { l: b.left, r: b.right };
    }
    return Math.max(0, ...Object.values(rows).map(x => x.r - x.l));
  };
  const inner = box => {
    const cs = getComputedStyle(box);
    return box.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  };
  const fit = () => {
    const narrow = matchMedia('(max-width: 700px)').matches;
    for (const [sel, boxOf] of RULES) {
      document.querySelectorAll(sel).forEach(el => {
        if (el.dataset.fs0 === undefined) el.dataset.fs0 = el.style.fontSize || '';
        el.style.fontSize = el.dataset.fs0;                  // taille d'origine (ordi)
        if (!narrow) return;
        const box = boxOf(el); if (!box || el.closest('[hidden]')) return;
        const avail = inner(box);
        for (let i = 0; i < 4; i++) {
          const w = widest(el); if (!w) return;
          const fs = parseFloat(getComputedStyle(el).fontSize);
          el.style.fontSize = Math.min(fs * avail * 0.97 / w, 260) + 'px';
        }
      });
    }
  };
  const run = () => (document.fonts ? document.fonts.ready : Promise.resolve()).then(fit);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
  let t; addEventListener('resize', () => { clearTimeout(t); t = setTimeout(fit, 120); });
  document.addEventListener('click', e => { if (e.target.closest('.filtre')) setTimeout(fit, 30); });   // cartes qui réapparaissent après un filtre
})();
