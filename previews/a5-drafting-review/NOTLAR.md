# A5 yatay — teknik görünüş düzeni

Kullanıcı A5 baskıyı seçti. Fiziksel hedef 210×148 mm. JPEG 1754×1236 piksel, yaklaşık 212 DPI. Önceki kaynak DPI'sını aynen alma kuralı bırakıldı; aksi halde baskı boyutu A5 olmayacaktı. PDF sayfa boyutu 210×147,98 mm, A5'e yuvarlama farkıyla karşılık gelir. Baskıda gerçek boyut/%100 kullanılmalı; sayfaya sığdır ölçeği değiştirir.

Yeni API çağrısı yapılmadı. Önceki Haiku no-colors tarifi değişmeden kullanıldı; R2 ve iç köşe geometrisi bu değişiklikte düzeltilmedi. Her üç üründe ana görünüş ve kesit ortak sayısal ölçekle yerleştirildi. İzometrik bağımsız yerleştirilir ve ölçek dışı olarak işaretlendi.

| Ürün | Ana görünüş/kesit ölçeği |
|---|---|
| 11-24-13 | 1:4 |
| 11-24-216 | 1:2 |
| 11-24-372 | 1:1,5 |

Eksen/merkez çizgileri siyah ince uzun-kısa çizgi düzenindedir. Delik eksenleri nihai katıdaki bakış doğrultusuyla hizalı dairesel kenarların merkezlerinden türetilir; modelden yeni bilgi alınmaz. Kontur 0,25 mm, eksen/tarama yaklaşık 0,13 mm, kesit izi 0,35 mm olarak çizilir. Tarama 45 derece, 2 mm kâğıt aralığıyla uygulanır. Piksel rasterleştirme ve JPEG sıkıştırması çok ince çizgileri etkileyebilir.

Genel tarama yöntemi ve kesit sınır çizgisi görünürlüğü henüz bütün parçalar için doğrulanmadı. Özellikle kademeli kesitte boşluk sınırları önceki sınırlamaları taşır; bu çıktı eksiksiz üretim paftası değildir. Antet yeniden kurulmadı; ölçüler hâlâ tablodadır. Görünürlük Excel düzeni eklenmediği için dönen ölçüler gösterilmeye devam eder.

3 yeni ölçek/kâğıt testi ve mevcut 9 native test geçti. Üç ürünün native üretimi ve STEP yeniden okuma kontrolleri de geçti. İlk JPEG görsel olarak incelendi. A5 çıktıda puntolar ve çizgi ağırlıkları kullanıcı baskı incelemesine sunuluyor.
