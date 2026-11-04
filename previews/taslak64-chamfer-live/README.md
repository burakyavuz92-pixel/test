# Taslak6.4 — Excel pah desteği ve canlı akış

Yeni Haiku 5.5/high geometri ve ölçü çağrılarıyla çalıştırıldı. Altı STEP ve altı antetli JPEG üretildi. Pah hücreleri: F/G 1x45°, J 3x35°. Parametrelerde boy ve açı ayrı sayılar olarak korunur. Model kodu F/G/J'nin hem boyunu hem açısını kullanır. K=9,5 geometride kullanıldı; K için ölçü referansı veya çizim etiketi üretilmedi.

Pah ayrıştırıcı testlerinde gerçek Excel'le 41 kontrol, önceki Excel uyumluluğunda 77 kontrol geçti. Pah geometrisi/bağlama ve K'nin köşeli parantez onayı olmadan çizilmemesi için Python testleri geçti.

## Çıktı sınırları

Her parçada A/B/D/F/G/J ve sabit 5 olmak üzere 7 gösterim yerleşti. Geometrik bağlantı hatası listesi boş. Ancak **C, E, 2,8 ve Ø25±0,5 için OCR onayı gelmediğinden bunlar çizilmedi**. K'nin çıkarılması kasıtlıdır; diğer dört gösterimin eksikliği başarı sayılmaz. OCR'nin 25 okuması `G2540,5` olmuş. Mevcut program bu atlamaları `sheets-produced` durumuna dahil edebiliyor; `audit-summary.json` inceleme sonucunu `rendered-with-unconfirmed-annotations` olarak kaydeder. Tam pafta başarısı iddia edilmez.

Montaj etiketi bu kez düzlem olarak döndü ve STEP'ten geri okundu. Kısa 733001-03 satırında D ve pahlar da yerleşti. Geometri kodu/model referansları elle değiştirilmedi; yüzeylerin taslakta amaçlanan anlamına tam uygunluğu teknik geri okuma kontrolleriyle garanti edilmez.

## Kullanım

| Çağrı | Input | Görünür yanıt | Reasoning | USD |
|---|---:|---:|---:|---:|
| Geometri | 8990 | 829 | 17736 | 0.0101815 |
| Ölçü | 9971 | 2833 | 17357 | 0.0110921 |
| Toplam | 18961 | 3662 | 35093 | 0.0212736 |

Görünür yanıt completion−reasoning olarak hesaplanır. Raw API yanıtları/reasoning yayımlanmaz. ZIP altı STEP/JPEG ve inceleme raporlarını içerir.
