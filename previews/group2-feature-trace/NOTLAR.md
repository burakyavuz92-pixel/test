# Taslak2 özellik referanslı kesit denemesi

Aynı taslak2guncel.xlsx ve notsuz yerel JPEG yazılıma verildi; high, tek çağrı. Kod/prompt değiştirilmedi. Yanıt elle değiştirilmedi. Çizim/STEP üretilmedi.

Giriş9592; akıl yürütme4151; görünür çıktı2672; toplam çıktı6823. Maliyet0.087414 USD, cache0. Önceki taslak kesiti çağrısı0.128836 USD/7628 akıl yürütme; bu denemede azalma var, tek deneme nedensel kanıt değil.

Dört satırın yerel çözümlemesi geçti. Model ana referansı holeC ekseni, geçilecek özellikleri holeD/holeE eksenleri seçti. C y=B−G, D y=−G, E x=−F; boş E atlanıyor, F0 gerçek delik korunuyor. 200/92 ve381 düz kesite,212 kademeli kesite dönüştü. Birim/boş parametre/sıfır uzunluk hatası yok. Aday tarif kaydedildi; insan onayı verilmedi.

**İncelemede yazılım hatası bulundu:**212 yolunda ilk sapma y187.225'te yapılıyor; üst C deliği y44.45'te. Bu nedenle çizginin delik seviyesindeki x'i−44.5 ve üst C deliği kaçırılıyor. FeatureSectionTrace ana referansı koordinat başlangıcı olarak alıyor fakat ziyaret edilecek noktalar listesine dahil etmiyor. C'yi main seçmek sözleşmeye uygun; hata yerel yol oluşturucuda. Hata doğrulayıcı tarafından yakalanmadı. Dört JSON'un çıkmış olması kesit doğruluğu onayı değil. Bu denemede kod düzeltilmedi; uygun sonraki adım ana referansı da izde zorunlu geçiş noktası olarak ele almak ve tüm referansların gerçek sonlu kesit izinde kapsandığını kontrol etmek.

Muhafazakâr iz uçları çizim sınırlarına göre kırpılmadı; genel native pafta yürütücüsü henüz yok. Tarif onaylanmış veya üretime hazır olarak işaretlenmedi. Ham özel akıl yürütme yayımlanmadı.
