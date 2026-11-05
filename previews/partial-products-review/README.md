Ürün bazında hata yönetimi — kontrollü testler

Bu hatalar test amacıyla kayıtlı betiklere bilerek eklenmiştir; yeni API çağrısı yapılmamıştır.

- partial-products-review: 6 üründen 2 model-hatası, kalan 4 ürün STEP/JPEG/PDF tamamlandı.
- partial-stages-review: geometri/yüzey etiketi/ölçü aşamalarında toplam 3 hata; diğer 3 ürün tamamlandı.
- all-products-failed-review: 6 hata; sonraki aşamalara geçilmeden her ürüne nedeni kaydedildi.

Başarılı kayıtlar yalnız outputId/status içerir. Başarısızların nedeni failed-products.txt ve product-results.json içinde bulunur. Örnek geometriler taslak6.6 kayıtlarından gelir; bilinen 1 mm geometri yorum hatası değiştirilmemiştir.
