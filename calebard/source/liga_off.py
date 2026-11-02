"""Goofy : ligatures coupées, pour que chaque lettre penche (comme dans Extra Goofy)."""
import sys
from fontTools.ttLib import TTFont
f = TTFont(sys.argv[1]); g = f['GSUB'].table; fl = g.FeatureList.FeatureRecord
liga = {i for i, fr in enumerate(fl) if fr.FeatureTag in ('liga', 'dlig', 'clig')}
for sr in g.ScriptList.ScriptRecord:
    for ls in [sr.Script.DefaultLangSys] + [r.LangSys for r in sr.Script.LangSysRecord]:
        if ls is None: continue
        ls.FeatureIndex = [i for i in ls.FeatureIndex if i not in liga]; ls.FeatureCount = len(ls.FeatureIndex)
f.save(sys.argv[1])
