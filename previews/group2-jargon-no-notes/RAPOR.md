# Çalışma raporu

Durum: blocked-with-report

- **B_G_REDUNDANT / input / warning / model**: B ve 2G ilişkisi satırlarda tutarsız (ör. 88.9 vs 2×44.45 uyumlu, 89 vs 2×44.5 uyumlu, 165.4 vs 157.4 uyumsuz).
  Aksiyon: Delik konumları için G kullanıldı; 11-30-92 satırında B ile G doğrulanmalı.

- **E_F_BLANK_OR_ZERO / input / warning / model**: Bazı satırlarda E/F boş; 11-30-381'de F sıfır ve E deliği eksen üzerinde, çizimdeki sol konumla farklı.
  Aksiyon: Boş E için delik oluşturulmaz; F=0 sayısal sıfır olarak işlenir.

- **MEASUREMENT_ENDPOINT_CONFLICT / model / error / validator**: F: ölçü kaynağının uçları, ölçülendirme tanımıyla uyuşmuyor.
  Aksiyon: Modelin renk/ölçü eşlemesi incelenmeli; kaynak veri değiştirilmez.

- **MEASUREMENT_ENDPOINT_CONFLICT / model / error / validator**: G: ölçü kaynağının uçları, ölçülendirme tanımıyla uyuşmuyor.
  Aksiyon: Modelin renk/ölçü eşlemesi incelenmeli; kaynak veri değiştirilmez.

- **COLOR_VISIBILITY_APPLIED / presentation / warning / validator**: Yeşil sabit ölçünün gösterimi yerel kuralla kapatıldı.
  Aksiyon: Girdi değişikliği gerekmez; geometri korunur.

- **COLOR_VISIBILITY_APPLIED / presentation / warning / validator**: Yeşil sabit ölçünün gösterimi yerel kuralla kapatıldı.
  Aksiyon: Girdi değişikliği gerekmez; geometri korunur.

- **COLOR_VISIBILITY_APPLIED / presentation / warning / validator**: Yeşil sabit ölçünün gösterimi yerel kuralla kapatıldı.
  Aksiyon: Girdi değişikliği gerekmez; geometri korunur.

- **MODEL_MEASUREMENT_CONFLICT / model / error / validator**: 11-30-92: modelde B=157.4, Excel nominali 165.4.
  Aksiyon: Model geometrik ilişkisi düzeltilmeli; geçerli Excel değeri değiştirilmemeli.

Origin=model kayıtları model yorumudur; tek başına doğrulanmış girdi hatası sayılmaz. Bu rapor soru/cevap beklemez. Girdi eksikliği ile yazılımın desteklemediği özellik ayrı değerlendirilir.
