"""Pravi podskupljene fontove za varijantu B: samo ASCII i znakovi potrebni za
srpski jezik (č ć ž š đ, navodnici, crtice), u kompresovanom formatu WOFF.
Rezultat: poppins-regular.woff i poppins-bold.woff (oko 6,5 KB svaki).
Potrebno: pip install fonttools; izvorni Poppins-Regular.ttf i Poppins-Bold.ttf
(Google Fonts, licenca SIL Open Font License 1.1) u istom folderu."""
from fontTools.ttLib import TTFont
from fontTools import subset

ZNAKOVI = ''.join(chr(c) for c in range(32, 127)) + 'čćžšđČĆŽŠĐ–—„“”’…'
for tezina in ('Regular', 'Bold'):
    f = TTFont(f'Poppins-{tezina}.ttf')
    opcije = subset.Options(); opcije.flavor = 'woff'
    s = subset.Subsetter(opcije); s.populate(text=ZNAKOVI); s.subset(f)
    f.flavor = 'woff'; f.save(f'poppins-{tezina.lower()}.woff')
    print(f'poppins-{tezina.lower()}.woff')
