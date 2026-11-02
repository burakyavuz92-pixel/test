# Taslak4.6 — yeni Haiku/high denemesi

Girdi: samples/taslak46-upload/taslak4.6.xlsx ve taslak4.6.jpg. Tek JPEG + yazılımın ayrıştırdığı nominal Excel tablosu gönderildi. Kullanıcı verisi, prompt veya model tarifi elle değiştirilmedi. Model anthropic/claude-haiku-5.5, reasoning high. Tek yeni çağrı; otomatik yeniden değerlendirme/tekrar çağrısı yok.

## Sonuç

Yeni tarif sözleşme kontrolünden geçti; altı satırın tamamında OCCT r_lip radyus işlemi başarısız oldu. Bu yeni çağrıdan JPEG/PDF üretilemedi. Mevcut model tarifi değiştirilmeden recipe.json içinde korunmuştur. Başarısızlık kesit veya ölçü yerleşimine ulaşılmadan gerçekleşti.

r_lip, 3 mm çeperin serbest ucundaki iç ve dış dairesel kenara aynı işlemde R1,5 uygular. İki radyus kalınlığın tamamını kaplar. Yerel teşhis: her bir kenar tek başına aynı nominal R1,5 ile başarılı, ikisi birlikte başarısız. Dolayısıyla sorun yalnız kenarın bulunamaması değildir; OCCT'nin bu çift radyus işlemini kurması başarısızdır. Kullanıcı çiziminin fiziksel olarak imkânsız olduğu sonucu çıkarılamaz. Tam yuvarlak kenarın desteklenen başka bir yapım yöntemiyle ifade edilmesi gerekebilir. Teşhis için yapılan tek-kenar denemeleri yeni üretim çıktısı olarak kullanılmadı.

Tarifte ayrıca F ölçüsünün Excel sütunu yerine sabit 0,5 olarak döndüğü görülüyor; bu bağlantı, tolerans ve taslak etiketi aktarımı bakımından ayrıca sorun olabilir. Üretim bu adıma ulaşmadığı için ölçülendirme sonucu varmış gibi değerlendirilmedi. R2'nin görsel olarak doğru konumda olduğunu bu çalışmayla doğrulayamadık.

## Kesit yazılımı değişikliği

Kesme düzlemi konturlarına ek olarak, kameranın karşı tarafında kalan malzemenin görünür kenarları OCCT HLR ile projekte edilir. Deliklerin kalınlık boyunca üst/alt kenarları bu gerçek geometriden gelir; delik sayısına veya ürün koduna özel çizgi eklenmez. Kademeli kesitte bağlantı bantları ayrı bir kesit olarak çizilmez; bant sınırlarında ek kenarlar kalabilir. Kesit taraması yine kesişim kapalı konturlarından üretilir.

Bir yeni delik-kenarı regresyon testi ve dokuz mevcut OCCT yürütücü testi geçti. Kayıtlı eski tarifle altı satırda ayrıca yerel kontrol yapıldı; bu eski tarif denemesi yeni model sonucu olarak sunulmadı.

## Kullanım

Input: 9.579 token. Output toplam: 34.263 token; bunun 32.072'si sağlayıcının raporladığı reasoning tokenı. Reasoning dışındaki fark 2.191 token. Toplam 43.842 token. Maliyet 0,0180894 USD; cached input 0. Ayrıntılar usage-summary.json içinde. Ham reasoning yayımlanmadı.
