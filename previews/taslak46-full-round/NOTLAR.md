# Çift R1,5 — tam yuvarlak uç

Son Haiku/high yanıtı değiştirilmeden tekrar yürütüldü. Yeni API çağrısı ve yeni API maliyeti yok. Recipe SHA256 summary.json içinde; önceki başarısız yeni yanıt ile byte olarak aynı olduğu kontrol edildi. Kullanıcı Excel/JPEG verileri değiştirilmedi.

## Çözülen işlem

Normal OCCT fillet başarısız olduğunda, seçilen iki tam dairesel kenarın eş merkezli ve aynı düzlemde olması, tek bir düz halka yüzünü ve eş eksenli silindirik yan yüzleri paylaşması, kalınlığın tam 2×R olması ve yuvarlatılacak bölgede kesinti bulunmaması kontrol edilir. Şartlar sağlanırsa uç bölgesinin tam torus zarfı dışında kalan malzemesi çıkarılır. Böylece kesit tam yarım daire olur; R=1,5 değiştirilmez. R=1,499 gibi bir yaklaşım kullanılmaz.

Bu, ürün adı veya kolon adına göre bir istisna değildir. Farklı eksen ve ötelenmiş koordinat testleri vardır. Kısmi yay, konik yan yüz, kesintili uç veya kalınlığa uymayan radyus bu yöntemle tahmin edilmez. Her fillet hatasını çözmez; desteklenmeyen durumda hata raporu sürer. checks kayıtlarında nativeMethod=exact-annular-full-round olarak izlenir.

## Sonuç ve sınırlar

Altı JPEG, altı PDF ve altı STEP üretildi. Her STEP yeniden açıldı, katı sayısı ve hacim kontrolü geçti. Tüm satırlar r_lip işleminde tam yuvarlak yöntemi kullandı. Ana geometri/radyus tarifi elle düzeltilmedi.

Bununla birlikte yeni Haiku tarifinin ölçü bağlantılarında üç sorun vardır: dimA (dış çap), dimE (eksenel ölçü) ve dimRimWall (3 mm). Bunlar çizimin altındaki kontrol tablosunda ve placement JSON dosyalarında gösterilir; ölçüler gizlice başka geometrilere bağlanmadı. F'yi Excel sütunu yerine sabit 0,5 olarak döndürmesi nedeniyle F etiketiyle yerel bağlama oluşmaz ve F çizilmez. R2'nin taslakla eşleşmesi görsel onay bekler.

Yeni Haiku tarifindeki geometri, eski yerleşim denemesinde kullanılan tarifle aynı değildir (örneğin H=A×0,31 ve T=7 seçilmiştir). Bu çalışmanın başarısı tam yuvarlak uç işlemini çalıştırmaktır; tüm parça ve ölçü yorumunun doğruluğu onaylanmış değildir.

## Doğrulama

5 tam yuvarlak testi, 9 mevcut OCCT yürütücü testi ve 1 kesit testi geçti. Hacim testi analitik olarak beklenen çıkarılan malzemeyle karşılaştırır; oluşan torus yüzünün gerçek küçük radyusunun 1,5 kaldığını kontrol eder. Yanlış radyus ve tek kenar yanlışlıkla bu yönteme geçirilmez. Altı satırlık üretim de son koruma kontrolleri dahil kodla yeniden çalıştırılmıştır.
