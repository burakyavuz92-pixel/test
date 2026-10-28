# Çalışma raporu

Durum: analysis-only

- **HOLE_E_OPTIONAL / input / warning / model**: E ve F boş olan satırlarda holeE yoktur; F=0 olan satırda delik orijinde bulunur ve F ölçüsü gizlenir.
  Aksiyon: Boş E için deliği atlayın; F=0 gerçek konumdur.

- **HOLE_C_ANCHOR / input / warning / model**: holeC konumu holeD'ye B ile bağlanmıştır; yeni delikler G ve B ile birlikte simetrik olmak zorunda değildir.
  Aksiyon: B ve G değerlerini bağımsız kullanın.

Origin=model kayıtları model yorumudur; tek başına doğrulanmış girdi hatası sayılmaz. Bu rapor soru/cevap beklemez. Girdi eksikliği ile yazılımın desteklemediği özellik ayrı değerlendirilir.
