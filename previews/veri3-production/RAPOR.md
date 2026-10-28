# Çalışma raporu

Durum: produced-awaiting-review

- **E_PRESENCE_ROWS / input / warning / model**: 11-30-10 satırında E ve F boş; E deliği yok sayılır. 11-30-260 satırında F=0, E deliği dikey eksende mevcut.
  Aksiyon: Boş E/F değerlerini yok say; F=0 değerini mevcut delik olarak işle.

- **G_B_SIGN_ASSUMPTION / input / warning / model**: Üst delik, alt deliğe B ile bağlanıyor; alt delik G ile merkez eksenin altında. B≠2G olan satırlarda (11-30-13, 11-30-989) geometri tutarsız olabilir.
  Aksiyon: B ve G değerlerini kaynakta doğrula; nominal değerleri değiştirme.

- **COLOR_VISIBILITY_APPLIED / presentation / warning / validator**: Yeşil sabit ölçünün gösterimi yerel kuralla kapatıldı.
  Aksiyon: Girdi değişikliği gerekmez; geometri korunur.

- **COLOR_VISIBILITY_APPLIED / presentation / warning / validator**: Yeşil sabit ölçünün gösterimi yerel kuralla kapatıldı.
  Aksiyon: Girdi değişikliği gerekmez; geometri korunur.

- **COLOR_VISIBILITY_APPLIED / presentation / warning / validator**: Yeşil sabit ölçünün gösterimi yerel kuralla kapatıldı.
  Aksiyon: Girdi değişikliği gerekmez; geometri korunur.

Origin=model kayıtları model yorumudur; tek başına doğrulanmış girdi hatası sayılmaz. Bu rapor soru/cevap beklemez. Girdi eksikliği ile yazılımın desteklemediği özellik ayrı değerlendirilir.
