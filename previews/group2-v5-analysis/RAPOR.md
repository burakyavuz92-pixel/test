# Çalışma raporu

Durum: blocked-with-report

- **SCALE_MISMATCH / input / warning / model**: Çizim ölçekli değil; piksel oranları B ve F değerleriyle uyuşmuyor, parametreler esas alındı.
  Aksiyon: Ölçü değerlerini doğrulayın.

- **HOLE_E_SIDE / input / warning / model**: E deliğinin sol tarafta olduğu ön görünüşten çıkarıldı; yansıma yönü kesin değil.
  Aksiyon: Delik yönünü doğrulayın.

- **RIM_EDGE_UNMEASURED / input / warning / model**: Kap ağzındaki hafif yuvarlatma ölçüsüz olduğu için modele eklenmedi.
  Aksiyon: Gerekirse ağız kenarı yarıçapını belirtin.

- **RECIPE_VALIDATION / model / error / validator**: 11-30-212: Geçersiz işlem girdi sayısı: holeC
  Aksiyon: Tarif veya desteklenen işlem sözleşmesi incelenmeli.

- **RECIPE_VALIDATION / model / error / validator**: 11-30-200: Geçersiz işlem girdi sayısı: holeC
  Aksiyon: Tarif veya desteklenen işlem sözleşmesi incelenmeli.

- **RECIPE_VALIDATION / model / error / validator**: 11-30-92: Geçersiz işlem girdi sayısı: holeC
  Aksiyon: Tarif veya desteklenen işlem sözleşmesi incelenmeli.

- **RECIPE_VALIDATION / model / error / validator**: 11-30-381: Geçersiz işlem girdi sayısı: holeC
  Aksiyon: Tarif veya desteklenen işlem sözleşmesi incelenmeli.

Origin=model kayıtları model yorumudur; tek başına doğrulanmış girdi hatası sayılmaz. Bu rapor soru/cevap beklemez. Girdi eksikliği ile yazılımın desteklemediği özellik ayrı değerlendirilir.
