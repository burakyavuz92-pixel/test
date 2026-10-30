# Çalışma raporu

Durum: recipe-analysis-only

- **SCALE_MISMATCH / input / warning / model**: Çizim ölçekli değil: B ve 33 ölçüleri piksel oranlarıyla uyuşmuyor; yazılı ölçüler esas alındı.
  Aksiyon: Yazılı nominal değerleri kullanın, görsel oranlara güvenmeyin.

- **R8_INTERPRETATION / input / warning / model**: R8 iç köşe yarıçapı varsayıldı (dış R11); ön görünüşteki iç daire (~A-22) bunu destekliyor ama kesin değil.
  Aksiyon: R8'in iç mi dış mı olduğunu çizimden doğrulayın.

- **RIM_EDGE_ROUNDING / input / warning / model**: Kenar ucundaki küçük yuvarlatma ölçülmemiş, modele eklenmedi.
  Aksiyon: Gerekirse kenar ucu yarıçapı eklenmeli.

- **G_NOT_HALF_B / input / warning / model**: 11-30-92 satırında G, B/2'ye eşit değil; C merkezi B-G ile türetildi, delikler simetrik olmayabilir.
  Aksiyon: C deliği konumunu doğrulayın.

- **E_ABSENT_OR_ZERO_OFFSET / input / warning / model**: E boş satırlarda küçük delik yok. F=0 satırında delik merkezde oluşur.
  Aksiyon: 11-30-381 için merkez deliğin amaçlandığını doğrulayın.

Origin=model kayıtları model yorumudur; tek başına doğrulanmış girdi hatası sayılmaz. Bu rapor soru/cevap beklemez. Girdi eksikliği ile yazılımın desteklemediği özellik ayrı değerlendirilir.
