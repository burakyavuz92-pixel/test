# Tek görüntülü CAD sözleşmesi v7 — kapak denemesi

Girdi: kapaktaslak.jpg ve kapaktaslak.xlsx. Yazılım tek orijinal JPEG, tek ayrıştırılmış tablo ve güncel sözleşme promptuyla OpenRouter'a bağlandı. Haricen hazırlanan geometri/model tarifi kullanılmadı. Kaynak JPEG düzenlenmedi. Model high akıl yürütme ile çalıştı. Çizim/STEP üretilmedi.

## Yapılan düzenlemeler

- İkinci JPEG (kırmızı temizlenmiş türev) ve ikinci nominal tablo kaldırıldı.
- Dış sözleşme v7: geometry ve drawing ayrıldı. Geometri nominal değerlerle çözülüyor; ölçüler doğrudan Excel sütununa bağlanıyor ve yazılım toleransı kaynaktan ekliyor.
- `uses` listesi modelin geometrik bağımlılıklarını taşıyor; yazılım eski target/tool/inputs ayrımını iç derleyici temsiline çeviriyor. Koşullu gövde aktarımı yazılımda kalıyor.
- Kaynak sütun/birim/sabit kesinliği korunuyor. Tolerans değişiminin aynı geometriyi üretmesi test edildi.
- Yaylı kapalı profiller, geometrik kenar seçimi ve koordinatlı kesit izi tarif edilebiliyor. Bu tanımların native OCCT uygulaması henüz tamamlanmadı.
- Kısa açıklama ve sekiz kelimelik kanıt kısıtı kaldırıldı. İlk denemede kullanılan prompt kaynak karakter sayısı 7492'den 6758'e, kelime sayısı 736'dan 617'ye indi; bunlar token ölçümü değildir.
- 42 kontrol geçti. Sıfır uyarı/hata ile derlendi. Testler native katı/pafta doğruluğunu kanıtlamaz.

## İlk deneme

20.000 çıktı token sınırına takıldı (`finish_reason=length`). Giriş 8836; çıktı 20000, bunun 13389'u akıl yürütme; maliyet 0.217672 USD; cache 0. JSON kesit tanımında yarıda kaldı; yazılım eksik yanıtı kabul etmedi. Çıktı sınırı 32768, HTTP zaman aşımı beş dakika yapıldı ve ikinci bir deneme başlatıldı. Bu bir defalık geliştirme denemesidir; uygulamada otomatik yeniden değerlendirme/tekrar çağrı döngüsü yok.

Ham API yanıtı özel akıl yürütme içerebildiği için yayımlanmadı. Kullanım sayıları ayrıca dosyalandı.


## Tamamlanan ikinci deneme

`finish_reason=stop`; giriş **8836**, toplam çıktı **24826** (akıl yürütme **16165**, geri kalan **8661**), maliyet **0.265932 USD**, cache **0**. İlk kesilen denemeyle toplam **0.483604 USD**. Sonraki normal çalışmanın maliyeti bu iki denemenin toplamı olarak düşünülmemeli; girdi/çıktı ve model muhakemesi değiştikçe fiyat değişir.

Model **22 parametre, 4 baz, 15 özellik, 9 ölçü, 3 görünüş ve bir düzlemsel kesit** döndürdü. Üç satır da çözüldü. Modelin ham tarifi değiştirilmedi; son yazılımla yerel inceleme yapıldı, yeni API çağrısı eklenmedi. Buradaki JSON'lar çizilmiş JPEG/STEP değildir.

| Ürün | Dış çap A | Hatve çapı B | Merkez deliği D | 4 delik C | Çıkıntı E | Sac F |
|---|---:|---:|---:|---:|---:|---:|
|30-24-422|236|200|70|11.7|5|5|
|30-24-143|236|143.7|70|11.7|5|5|
|30-24-54|255|143.7|47|11.7|5|5|

### Gelen tarifin değerlendirmesi

- Dört delik B/2 yarıçapında 0/90/180/270° konumlarında; tek merkez deliği D. Her deliğin etrafında E yüksekliğinde çıkıntı var. Nominal ölçüler/tolerans bağlantıları doğru kaynak sütunlarında.
- İki U-kanal 45° ve 225° bazlarında; genişlik14, yarıçap7, dış kenardan iç uca derinlik16.5. Kanal kesici toplam uzunluğu30.5, uçtan uca kabul edilmiş. Kanalların iç uç yarıçapı A/2-16.5; böylece çap değişince yerleri güncelleniyor. Yeşil ölçüler modelde kullanılmış, ölçülendirmede görünmez.
- Çıkıntı dış çapı yaklaşık20 mm: model bunu `estimated` olarak işaretlemiş. Önceki tarifte yaklaşık21.6 idi; bu ölçülendirilmemiş görsel detayın tahmininin değişebildiğini gösterir. Model geçiş/pah/radyus ve delik ağzı detaylarını düz silindire sadeleştirdiğini açıkça bildiriyor.
- A-A kesit yolu sectionFrame üzerinden dünya x=0, Y doğrultusunda; Z boyunca süpürüldüğünde merkez ve üst/alt deliklerden geçen düzlem oluşuyor. Özel üçüncü delik mantığı kullanılmadı.
- E çıkıntı yüksekliği, F sac kalınlığı kabul edilmiş; modelin bu yorumuna asistan düzeltmesi yapılmadı. +Z çıkıntı yüzü ve izometrik kamera da modelden geldi.
- Model yedi uyarı döndürdü. B=200 satırının taslak oranından farklı olması ve çizimdeki boş artı işareti gibi uyarılar üretimi durduracak hata sayılmadı. Bu tür olağan farklılıkların ileride daha az gereksiz rapor üretmesi ayrıca değerlendirilebilir; yeni uyarı promptları eklenmedi.

### Yazılımda yapılan müdahale

Model E=0/boş olduğunda çıkıntısız ana gövdenin devam edeceğini yazmıştı, ancak önceki iç derleyicide fuse oluşturma işlemi sayıldığı için gövdeyi atlayabilirdi. Üç kaynak satırda E pozitif olduğundan bu dal çalışmıyordu. Genel çözüm: dış `fuse` ilk girdiyi ana gövde, diğerlerini eklenecek gövdeler sayıyor; iç derleyici `join` işlemine indiriyor. Koşul false veya ekler yokken ana gövde ileri taşınıyor. Bu davranış E boş, sıfır ve pozitif için test edildi. Tarif elle onarılmadı, API tekrar çağrılmadı.

Tariften sonra roundedSlot uzunluğunun uçtan uca olması ve koşullu fuse davranışı promptta da açık arayüz tanımı olarak netleştirildi; bu değişiklik için yeniden ücretli deneme yapılmadı. `request-prompt.txt` ikinci çağrıda gerçekten gönderilen sürümdür; src/CadRecipePrompt.cs son sürümdür.

### Kalan sınır

Bu deney modelin ana parçayı anlaması ve sözleşmenin kayıpsız çözümlenmesi açısından olumlu. Native katı yürütücüsü, ölçü hedeflerini gerçek OCCT topolojisine bağlama ve pafta yerleşimi henüz tamamlanmadı. Özellikle serbest semantik ölçü hedefleri (outerDiameter/pitchCircle vb.) o katmanda uygulanmalı; biçim doğrulaması tek başına geometrik doğruluk kanıtı değildir.
