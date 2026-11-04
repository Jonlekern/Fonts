/* Spécimen commun : liste des graisses, testeur, grille de caractères.
   Chaque page de police définit window.SPECIMEN avant de charger ce script :
   { family, sample, styles:[{n,w,label?,fam?}], testerDefault, testerExtra?:[styles en plus dans le testeur], glyphs, glyphChips:[index], glyphDefault, glyphsGarder? } */
/* Règle du site : les signes ajoutés pour le standard Google (Europe de l'Est, turc, gallois, accents seuls) ne sont pas montrés
   dans la grille des caractères. Ils restent dans les polices et s'affichent quand on les tape dans le testeur.
   Une page peut en garder certains avec glyphsGarder (ex. Clebard : Ă ă Đ đ du vietnamien). */
const SIGNES_CACHES = "ĀāĂăĄąĆćĊċČčĎďĐđĒēĖėĘęĚěĞğĠġĢģĦħĪīĮįİıĶķĹĺĻļĽľŁłŃńŅņŇňŐőŔŕŘřŚśŞşŠšŤťŪūŮůŰűŲųŹźŻżŽžȘșȚțȷŴŵŶŷẀẁẂẃẄẅỲỳˆˇ˘˙˚˛˜˝";
(function () {
  const C = window.SPECIMEN; if (!C) return;
  const fam = s => `'${s.fam || C.family}'`;
  const esc = c => c.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  const W = document.getElementById("weights");
  if (W) W.innerHTML = C.styles.map(s =>
    `<div class="wrow"><div class="meta"><b>${s.n}</b><small>${s.label || s.w}</small></div>` +
    `<div class="sample" style="font-family:${fam(s)};font-weight:${s.w}">${esc(C.sample)}</div></div>`).join("");

  const sel = document.getElementById("tw"), size = document.getElementById("ts"), txt = document.getElementById("tester-text");
  if (sel && size && txt) {
    const TS = C.styles.concat(C.testerExtra || []);
    sel.innerHTML = TS.map((s, i) => `<option value="${i}" ${i === C.testerDefault ? "selected" : ""}>${s.n}</option>`).join("");
    const apply = () => { const s = TS[+sel.value]; txt.style.fontFamily = fam(s); txt.style.fontWeight = s.w; txt.style.fontSize = size.value + "px"; };
    size.value = Math.min(56, Math.max(16, Math.round((txt.clientWidth || 340) / 16.5)));
    sel.addEventListener("change", apply); size.addEventListener("input", apply); apply();
  }

  const grid = document.getElementById("glyphs"), gw = document.getElementById("gw");
  if (grid && gw) {
    const caches = new Set([...SIGNES_CACHES].filter(c => !(C.glyphsGarder || "").includes(c)));
    grid.innerHTML = [...C.glyphs].filter(c => !caches.has(c)).map(c => `<div aria-label="${esc(c)}" style="font-family:inherit">${esc(c)}</div>`).join("");
    const chips = C.glyphChips.map(i => C.styles[i]);
    gw.innerHTML = chips.map((s, i) => `<button class="chip" data-i="${i}">${s.n}</button>`).join("");
    const apply = i => { const s = chips[i]; grid.style.fontFamily = fam(s); grid.style.fontWeight = s.w;
      gw.querySelectorAll(".chip").forEach(b => b.setAttribute("aria-pressed", b.dataset.i == i)); };
    gw.addEventListener("click", e => { const b = e.target.closest(".chip"); if (b) apply(+b.dataset.i); });
    apply(C.glyphDefault);
  }
})();
