# Çalışma raporu

Durum: blocked-with-report

- **OFFSET_SECTION_UNSUPPORTED / software / error / model**: Section A-A has a stepped cutting trace. The current backend supports only a planar X=0 section, so this offset section cannot be generated. The section is declared as offset and has not been flattened to X=0.
  Aksiyon: Keep the drawing as it is. Run the part again once the backend supports offset or stepped sections.

- **OPTIONAL_THIRD_HOLE_RULE / input / warning / model**: The third hole is treated as absent only when both E and F are blank. Rows 11-30-200 and 11-30-92 have both blank, so the hole is absent. Row 11-30-381 has F=0 with E=14, so the hole is real and sits at position 0. The presentIfColumn is set to E, but the both-blank rule also depends on F.
  Aksiyon: Treat the third hole as absent only when both E and F are empty. Do not treat F=0 as absent.

- **TOLERANCE_TEXT_IN_VALUES / input / warning / model**: Excel values contain tolerance text such as Ø160±1, 88,9±0,5 and Ø10 (+0,1|-0,0), and use decimal commas. Geometry expressions need plain numeric values.
  Aksiyon: Yerel ayrıştırıcı bu dosyadaki nominal/tolerans biçimlerini başarıyla okudu. Bu model önerisi nedeniyle Excel sütunlarını ayırmayın.

- **HOLE_POSITION_ASSUMPTION / input / warning / model**: The drawing does not state that holes h1 and h2 are symmetric about the center. The expressions B/2 and -B/2 are used because B is the center distance between them and G is the offset from the center. The third hole X position (column F) and its exact sign are read from the stepped trace and view only.
  Aksiyon: Add explicit position columns for the holes if they are not symmetric. Where G equals half of B, the hole lies on the center.

- **FIXED_DIMENSIONS_FROM_DRAWING / input / warning / model**: The green dimensions 33.0 (depth), R8 (outer radius) and 3 (thickness) are fixed across rows. All their annotations are hidden in the output.
  Aksiyon: Keep these values fixed and leave them without annotations.

- **CAMERA_APPROXIMATE / camera / warning / model**: The camera direction is a visual approximation of the shaded view.
  Aksiyon: Use the approximated direction as the reference-matching view.

- **UNSUPPORTED_SECTION / software / error / validator**: Taslak kademeli/ofset kesit gerektiriyor; yeni OCCT çizim yolu yalnızca X=0 düzlemini destekliyor.
  Aksiyon: Yazılıma kademeli kesit desteği eklenmeli. Doğru girdiyi değiştirmek gerekli değildir.

- **PLAN_VALIDATION / model / error / validator**: 11-30-212: Desteklenmeyen ifade: MINUSB/2
  Aksiyon: Planın özellik/sütun eşleşmeleri düzeltilmeli.

- **PLAN_VALIDATION / model / error / validator**: 11-30-200: Desteklenmeyen ifade: MINUSB/2
  Aksiyon: Planın özellik/sütun eşleşmeleri düzeltilmeli.

- **PLAN_VALIDATION / model / error / validator**: 11-30-92: Desteklenmeyen ifade: MINUSB/2
  Aksiyon: Planın özellik/sütun eşleşmeleri düzeltilmeli.

- **PLAN_VALIDATION / model / error / validator**: 11-30-381: Desteklenmeyen ifade: MINUSB/2
  Aksiyon: Planın özellik/sütun eşleşmeleri düzeltilmeli.

- **OPTIONAL_FEATURE_EXECUTOR / software / error / validator**: Şema v2 koşullu özellik yürütücüsü tamamlanmadı.
  Aksiyon: Yazılım desteği tamamlanmalı; boş hücreleri sıfırla doldurmayın.

Origin=model kayıtları model yorumudur; tek başına doğrulanmış girdi hatası sayılmaz. Bu rapor soru/cevap beklemez. Girdi eksikliği ile yazılımın desteklemediği özellik ayrı değerlendirilir.
