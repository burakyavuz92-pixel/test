# Ürün bazında hata yönetimi

`run-cadquery-group` ve `replay-cadquery-group` başarılı ürünleri STEP, montaj yüzeyi etiketi ve pafta aşamalarından geçirir. Bir ürünün hatası diğer ürünleri durdurmaz. Ortak betiğin yüklenememesi, API çağrısının kesilmesi veya süreç zaman aşımı gibi ortak hatalar sonraki aşamaları durdurabilir; önceki dosyalar korunur.

Model başarıda yalnız mevcut geometri/ölçü verisini döndürür. Yalnız başarısız parametre satırında `build_part(p)`, `build_face_tags(p)` veya `build_measurements(p)` fonksiyonu `{"error":"kısa Türkçe sebep"}` döndürebilir. Bu neden `model` kaynaklı olarak kaydedilir. Python/OCCT hataları `software`, çağrı/yanıt aktarım hataları `api` kaynaklıdır. Modelin kısa neden üretmesi sözleşmede istenir; yazılım kendiliğinden tasarım nedeni uydurmaz ve teknik hatayı modele açıklattırmak için ek çağrı yapmaz.

- `product-results.json`: her ürünün `outputId` ve `status` alanları. Başarılı üründe açıklama yok. Başarısız üründe ayrıca `reason`, `origin`, `stage` bulunur.
- `failed-products.txt`: yalnız başarısız ürünlerin numarası ve nedeni; konsolda da gösterilir.
- `product-failures.json`: aşamalar arasındaki hata kaydı; başarısız ürünler sonraki aşamalarda atlanır. İlk hata nedeni korunur.
- `run-report.json`: grubun durumu; kısmi başarı `partially-produced`, çıkış kodu 2. Tam başarısızlık çıkış kodu 1. Ölçü/etiket belirsizlikleri için mevcut inceleme durumu ve çıkış kodu 2 korunur.

Tek bir ölçünün `unresolved` olması ile ürün fonksiyonunun bütünüyle başarısız olması farklıdır. Mevcut çözülemeyen ölçü raporlaması korunur. Geometrinin geçerli olması taslak yorumunun doğruluğunu garanti etmez.

Testler: `tools/test_product_failures.py` ve kontrollü replay senaryoları. `previews/partial-products-review` içindeki hatalar test amacıyla bilerek eklenmiştir; modelin gerçek API yanıtındaki hatalar değildir.
