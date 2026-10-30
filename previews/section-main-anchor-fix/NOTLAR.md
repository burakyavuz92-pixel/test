# Ana kesit referansının korunması

FeatureSectionTrace ana referansı da zorunlu ziyaret noktaları arasına katıyor. İstenen özellikler iz doğrultusunda sıralanıyor; kademe geçişleri komşu noktalar arasına yerleştiriliyor. Böylece üst deliği main olarak seçmek artık o deliğin atlanmasına neden olmuyor. Aynı iz seviyesindeki referansların sırası modelin referans sırasıyla korunuyor; yatay geçiş oluşabiliyor. Yinelenen noktalar temizleniyor.

Yol üretiminden sonra tüm mevcut referansların izdüşümlerinin sonlu çizgi parçaları üzerinde bulunduğu kontrol ediliyor. Yalnızca sonsuz düzleme üyelik yeterli sayılmıyor. Eksik özelliğin atlanması ve sıfır ofsetli gerçek deliğin korunması değişmedi. Prompt ve ham model tarifleri değiştirilmedi.

71 yerel kontrol geçti. Yeni testler ana/yan/alt referansın kapsanmasını, yok/sıfır davranışını ve eski hatalı yol biçiminin reddini kapsıyor.

Kayıtlı model yanıtlarıyla yerel review-cad-group çalıştırıldı; kaynak dosya özetleri doğrulandı. **API çağrısı0, yeni API maliyeti0.** Taslak2 dört satır ve kapak üç satır çözümlendi. 212 kesiti üst (0,44.45), yan (−44.5,0) ve alt (0,−44.45) noktalarının üçünden de geçiyor. Geçişler y=±22.225'te. 200/92 ve381 düz kesit; kapakların üçü de düz kesit kaldı. JSON'lar bu klasörde; bunlar JPEG/STEP değildir.

Tarifler insan onaylı üretim kaydı olarak işaretlenmedi. Genel native OCCT yürütücüsü hâlâ tamamlanmadı. İz uçlarının gerçek BRep sınırlarına kırpılması ve kesitin paftada gösterimi sonraki aşamadır. Bu düzeltme sadece yol/özellik geometrik tutarlılığını doğrular; bütün ürün geometrisini veya imalat uygunluğunu kanıtlamaz.
