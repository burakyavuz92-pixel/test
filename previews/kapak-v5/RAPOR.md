# Çalışma raporu

Durum: recipe-analysis-only

- **PITCH_DIAMETER_SYMBOL / input / warning / model**: B girdisinde çap sembolü yok ancak çizimde ∅'B' var; B delik daire çapı olarak yorumlandı.
  Aksiyon: B'nin delik dairesi çapı olduğunu doğrulayın.

- **BOSS_DIAMETER_UNMEASURED / input / warning / model**: Delik çevresi yükselti çapı ölçülü değil; plandan yaklaşık 21,6 mm varsayıldı. Yükselti kenar geçişi/yuvarlatması da modellenmedi.
  Aksiyon: Yükselti çapı ve kenar geometrisi ölçüsünü doğrulayın.

- **SLOT_ASSUMPTIONS / input / warning / model**: Yuva açısı (45° ve 225°) görselden tahmin edildi; 16,50 ölçüsünün dış çevreden yuva dibine olduğu ve yuva uzunluğunun toplam uzunluk olduğu varsayıldı; taşma 10 mm varsayım.
  Aksiyon: Yuva açısı ve derinlik referansını doğrulayın.

- **SLOT_QUANTITY / input / warning / model**: Yuva ölçüleri yalnız bir yuvada verilmiş; ikinci yuvanın aynı olduğu varsayıldı.
  Aksiyon: İkinci yuva ölçülerini doğrulayın.

Origin=model kayıtları model yorumudur; tek başına doğrulanmış girdi hatası sayılmaz. Bu rapor soru/cevap beklemez. Girdi eksikliği ile yazılımın desteklemediği özellik ayrı değerlendirilir.
