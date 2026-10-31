# R2 konum araştırması

Yeni API çağrısı yapılmadı. Kullanıcının taslak4.2.jpg dosyası, Sonnet high ve Haiku high ham tarifleri, çözümlenmiş tarifler ve OCCT kenar/yüz geometrileri karşılaştırıldı. Tarifler değiştirilmedi.

## Kanıt

Her iki model ilk ürün için aynı seçimi yaptı: near=[-59.75,0,-3], axis=[0,0,1], radius=2. Bu nokta merkezi [-73,0] olan J+6=26,5 mm dış çapın r=13,25 mm dairesel kenarında, pleytin arka yüzü z=-3 üzerinde. İşlem frame=world; koordinat dönüşümü konumu değiştirmiyor.

Fillet öncesi OCCT gövdesinde seçime uyan daire r=13,25 ve z=-3. Fillet sonrası yüz geometrisinde merkezi [-73,0,-5], büyük yarıçapı 15,25 ve küçük yarıçapı 2 olan torus oluşuyor. Bu, dış çıkıntı ile arka pleyt yüzünün birleşimine uygulanan radyustur. İki ayrı modelde konum aynı; OCCT tarifi ters çevirmemiş.

Taslaktaki R2 oku ise delik iç geçişindeki kıvrıma yöneliyor. Modeller delikli kıvrımı silindirik bir çıkıntı ve ayrı düz delik/boşaltma işlemleriyle tarif edip R2'yi dış arka köke yerleştirmiş. Sadece radyusun görünüşte saklanması değil, yanlış kenarın seçilmesi söz konusu. Önceki kullanıcı açıklamasındaki yalnız görünürlük gerekçesi eksikti.

## Yazılım ve sözleşmedeki eksikler

- Native fillet seçicisi yakın nokta ve eksen/teğet yönünü kullanıyor. Yakınlık toleransı 0,001 mm. Seçilen yanlış köşe verilen noktaya gerçekten uyuyor; rastgele yakın kenar seçimi kanıtı yok.
- Sözleşmenin optional operation alanı native seçicide uygulanmıyor. Sonnet seçicisine derleyici hubHole, Haiku seçicisine hub ekliyor; yürütücü her iki durumda da mevcut gövdenin bütün kenarlarını tarıyor. Bu gerçek bir sözleşme/yürütücü uyumsuzluğu; ancak burada yanlış near noktası zaten model yanıtında var. Tek başına operation düzeltmesi R2'yi doğru köşeye taşımaz.
- BRep/STEP kontrolleri katının teknik olarak geçerli olduğunu doğruluyor; taslakla semantik eşleşmeyi doğrulamıyor. Bu nedenle başarılı işlemi doğru yorumlanmış parça gibi sunmamak gerekiyor.

## Öneri

Bu araştırmada üretim kodu değiştirilmedi. Geometrik yapının delik iç ve dış kıvrımlarını birlikte doğru tarif etmesi gerekiyor; arka dış kökten iç geçişe yazılımın tahminle radyus taşıması genel çözüm değil. Önce sözleşmedeki operation alanının gerçek anlamı ile yürütücünün davranışı eşleştirilmeli (gerçek kenar köken takibi uygulanmalı veya desteklenmeyen daraltma taahhüdü kaldırılmalı). Ardından ölçü/işlem referansları üzerinden radyusun hangi iki yüzü bağladığını incelemeye elverişli kısa yapısal bir tanım değerlendirilebilir. R2'ye özel sabit koordinat kuralı eklenmemeli. Aynı köşede iç/dış radyusu ayırt eden yerel regresyon testi gereklidir.
