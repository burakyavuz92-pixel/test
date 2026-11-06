# Cıvata 730001 — kontur denemesi

Aynı mevcut STL, kamera ve mevcut siluet/keskin ağ kenarı filtresi kullanıldı.
Kontur modunda yüzey beyaz ve ışıksız; opak yüzey arkadaki çizgileri derinlik
testiyle gizlemeyi sürdürür. Üçgen kenarlarının tamamını gösterme kapalıdır.
Mevcut 50 derece özellik açısı korunur; bu gerçek CAD kenarlarının tamamı veya
teğet geçiş çizgileri değildir. Geometri ve STEP değişmedi; API çağrısı yok.
Varsayılan Phong korundu; rendering.shading=contour yalnız deneme seçeneğidir.
