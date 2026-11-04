# Taslak6.6 — yerel kontrollerden sonra yeni API çağrıları

## Sonuç

Haiku 5.5 / high ile iki yeni API çağrısı yapıldı. Sonuç: **sheets-produced**. Altı STEP ve altı JPEG üretildi. Her parçada **11/11 gösterim yerleşti**, unresolvedDimensions ve unconfirmedVisualLabels listeleri boş. Yalnız K, köşeli parantezsiz geometri verisi olduğu için kasıtlı olarak çizilmedi. Beş parça 1:1; 733001-03 2:1.

## Yerel ön kontrol

Excel altı satırda ayrıştırıldı. F/G/J boy+açıları, K=9,5, L=Ø25 ve ±0,5 toleransları kontrol edildi. OCR'de A/B/C/D/E/F/G/J/L/5/2,8 gösterimlerinin tamamının doğru metinleri bulundu. Yanlış alternatifler ayrıca korunuyor; yalnız adayda bulunmaları nihai onay anlamına gelmez. Aynı konumlu yanlış okumalar model eşleştirmesinde kullanılmadı. K, beklenen görsel etiket listesine alınmadı.

Ön kontrolde kullanılan aynı JPEG hash'i ve OCR sürümüyle elde edilen sonuç cache'e kaydedildi; API sonrası aynı OCR taraması tekrar çalıştırılmadı. Giriş JPEG'i veya kullanıcı Excel'i değiştirilmedi. Yeni model çağrıları yalnız yerel kontrollerden sonra başlatıldı. Yerel OCR bulguları local-preflight klasöründedir. İlgili OCR, pah bağlama ve geometri destek birim testleri de geçti.

## Model ve çizim

Model L, K ve pah parametrelerini yeni geometri kodunda kullandı. Modelden gelen geometri veya ölçü kodu elle düzeltilmedi. STEP'lerde tek geçerli katı ve geri okuma kontrolleri geçti; montaj etiketi düzlem olarak seçildi, altı STEP'te yazılıp geri okundu. Geometri A ucunda Z=0, gövde/flanş −Z olacak şekilde kuruldu. Kamera yazılımda çevrilmedi.

L kimliği sayesinde Ø25/tolerans bilgisini OCR'den çözmek gerekmiyor; bu bilgi Excel'den geliyor. JPEG'lerde Ø25 (±0,5) eğik gösteriliyor. Önceki D ve 25 referans hataları bu yeni yanıtta tekrarlanmadı. Bu teknik bağlantı/yerleşim kontrolleri geometrinin bütün tasarım niyetine uygunluğuna dair bağımsız mühendislik onayı değildir; kullanıcı STEP ve çizimleri incelemelidir.

## Kullanım

| Çağrı | Input | Görünür yanıt | Reasoning | USD |
|---|---:|---:|---:|---:|
| Geometri | 9314 | 1122 | 17222 | 0.0101034 |
| Ölçü | 10452 | 4009 | 20487 | 0.0132932 |
| Toplam | 19766 | 5131 | 37709 | 0.0233966 |

Görünür yanıt completion−reasoning hesabıdır. Raw API yanıtları ve reasoning metni yayımlanmadı. ZIP altı STEP/JPEG'i, kod/veri kayıtlarını ve yerel test raporlarını içerir. Bu görevde yazılım kodu değiştirilmedi.
