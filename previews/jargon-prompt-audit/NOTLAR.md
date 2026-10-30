# Başarısız sade promptun ayrıntılı incelemesi

Bu incelemede yeni çağrı/çizim veya uygulama kodu değişikliği yapılmadı. Kaydedilmiş gerçek sent-prompt, özgün API cevabı, ayrıştırılmış Excel ve ilişkileri değerlendiren kod karşılaştırıldı. Gönderilmiş metin sent-prompt.txt içinde (anahtar/gizli bilgi içermez); seçilmiş somut kayıtlar facts.json içinde.

## Ana bulgu: B okundu, sonra konum hesabında kullanılmadı

Model B kaydında aynen "Üst ve alt delik merkezleri arası dikey ölçü" diyor. G'yi alt merkezin ana eksene uzaklığı olarak açıklıyor. Orijin gövde merkezinde doğru. F işareti ve üçüncü delik konumu doğru.

Ancak geometride C deliği Y=+G, D deliği Y=-G. B hiçbir konum bağında yok. Daha sonra B_G_REDUNDANT kaydında 165,4 ile 2×78,7'nin tutmadığını kendisi açıklıyor ve "Delik konumları için G kullanıldı" diyor. Bu, ölçü harfinin kaybolması veya Excel'in bozuk gelmesi değil; gözlenen ilişkinin tutarsız geometriye çevrilmesi. Ham yanıt ile saklanan plan eşit; sonradan kod yanlış bir simetri eklememiş. Yanıt kesilmemiş (finish=stop).

92 satırı: gerekli eşitlikler üstY-altY=165,4 ve 0-altY=78,7. Bunlar birlikte üstY=86,7 ve altY=-78,7 verir. Simetriyi kabul etmeyi gerektiren eksik bir ölçü yoktur. Modelin +78,7/-78,7 seçimi açık B ölçüsünü 8 mm ihlal eder. Bu satırın simetrik olmaması girdi tutarsızlığı değildir.

## Prompt gerçekten ne diyor?

Başlangıçta "Explicit drawing information takes precedence" yazıyor. Yani açık ölçünün önceliği hiç belirtilmemiş değil. X/Y orijini ve JSON alanları mevcut. Promptta +G/-G veya B=2G simetri talimatı yok. JSON şeması doğru bağımlılığı da temsil edebiliyor; önceki başarılı yanıtta aynı şemayla üst delik alt deliğe B ile bağlanmıştı. Dolayısıyla bu yanlış sonuç şemanın doğru çözümü ifade edememesinden kaynaklanmıyor.

Buna rağmen prompt ve sözleşmede mimari zayıflıklar var:

- Model aynı ölçüyü measurementSources (gözlem), geometry (konum bağı) ve annotations (gösterim) içinde ayrı ayrı kuruyor. Bunlar birbirinin tek kaynağı değil. B gözlemi doğruyken B'yi kullanmayan konumlar üretilebiliyor.
- "Her ölçü sütununun dimension mapping'i olsun" şartı yalnızca annotations'da kapsam kontrolü yaratıyor. Her açık geometrik ilişkinin koordinatların çözümünde korunması, üretici sözleşmesinde yapısal bir zorunluluk değil. Sonraki validator bunu yakalıyor ama modelin doğru geometrisini kendisi çözen bir kısıt motoru yok.
- Mevcut Solve/Offset kodu bildirilen bağımlılıkları doğrudan hesaplıyor; tüm gözlenen ilişkileri birlikte çözen bir denklem/kısıt çözücüsü değil. Bu nedenle modelin yanlış bağımlılığını B'ye bakarak düzeltemiyor. Bu kod modeli yanlış anlamaya zorlamıyor; anlama ile koordinat üretimi arasındaki yükü modele bırakıyor.
- Aynı yanıtta B_G_REDUNDANT uyarısıyla geometri üretilebiliyor. Bütün verilen ilişkileri sağlayan çözüm olup olmadığını değerlendirmek yerine model bir yorumu seçip kalan ölçüyü girdi sorunu saymış.

## Olası etkenler (kesin iç neden olarak kanıtlanamaz)

Dört örneğin üçünde B=2G: 88,9/44,45; 89/44,5; 70/35. Taslak görünüşü de simetrik referans ürünü gösteriyor. Modelin bu örüntüyü bütün gruba yaymış olması, B_G_REDUNDANT açıklamasıyla uyumlu güçlü bir olasılık. Ama iç muhakemeye erişim olmadığından tek kesin neden ilan edilemez.

Tek çağrıda görsel okuma, koordinat üretme, görünürlük, kesit, kamera ve rapor isteniyor. reasoning.effort=low ve tam pafta görüntüleri değişmedi. Bunlar olası etken; ayarlar arasında kontrollü yeni karşılaştırma yapılmadı. B uçlarının sözlü olarak doğru yazılması, "B çizgisini hiç göremedi" açıklamasını tek başına yetersiz kılıyor.

Asistanın değerlendirmesi, önceki konuşmalarda B/G ilişkisini ve referans ürününü öğrenmiş bağlamdan yararlanıyor. API yalnızca programın gönderdiği mesajları alıyor. Bu fark başarı beklentisini kaldırmaz; ikisinin tamamen aynı bağlamda yaptığı bir kör test olmadığı anlamına gelir.

## Sonraki adım önerisi

B/G için doğru cevapları ayrı ayrı prompta yazmak yerine, modelin okuduğu bütün açık ölçü ilişkilerini bir kez tanımlatmak; koordinat bağımlılığı ve annotation bağlantısını bu aynı ilişkilerden türetmek. Model parçayı ve ölçü uçlarını tanımaya devam eder, kullanıcı koordinat hazırlamaz. Matematiksel çözücü verilmiş ilişkileri birlikte korur; simetri yalnızca gerçekten serbest kalan ilişkiler için tamamlayıcı olabilir.

Bu örnekte doğru gözlem zaten çıktı içinde var: B iki delik arası, G orijin-alt delik arası. Bunlardan koordinatı yerelde hesaplamak parçayı elle tarif etmek değildir; modelin doğru gözlemini ikinci kez yeniden yorumlatmamaktır. Ancak genel kısıt çözümü/yön ve görünüş eşleştirmesi ayrı bir geliştirmedir, şu anda uygulanmış sayılmaz. Yeni bir model/akıl yürütme ayarı karşılaştırması da mümkün; mevcut tek başarısız deneme modelin her koşulda yapamayacağını kanıtlamaz.
