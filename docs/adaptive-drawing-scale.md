# Uyarlanabilir çizim ölçeği ve görünüş yerleşimi

Durum: temel uygulama tools/adaptive_scale.py üzerinden çizim akışına bağlandı. Yazı rezervleriyle paketler oluşturulur; iki deterministik sayfa bölgesinde gerçek ölçü yerleşimi sınanır. Aynı ölçekte toplam açıklama çizgisi uzunluğu düşük yerleşim seçilir. Tasarımın genel keyfî engel paketleme araması yerine şu an antet/izometrik için iki geçerli çalışma bölgesi kullanılıyor. Görünüş başlıkları, glif ve çizgi taşmaları denetlenir.

## Amaç ve sabitler

Her parça için kesit ve ana görünüşün ortak, ölçülendirmeyle birlikte sayfaya sığan en büyük tercih edilen ölçeğini seç. Görünüş yönünü ölçek için döndürme, aynalama veya değiştirme. Kesit solda, ana görünüş sağında, küçük izometrik sağ üstte, antet aynı yerde kalır. Kısa-geniş ve uzun-dar geometriler için ayrı parça kuralları yoktur.

Sayfa fiziksel mm ile tanımlanır (mevcut A5: 210 × 148). JPEG çözünürlüğü yalnız son raster dönüşümünü etkiler. Yazı, ok, çizgi kalınlığı ve ölçü şeridi aralıkları fiziksel kâğıt boyutlarıdır; parça ölçeğiyle büyümez. Kesit ve ana görünüş aynı ölçekte; izometrik kendi alanına sığan ayrı ölçektedir ve ayrı ölçek bilgisi taşır.

## Girdiler

- Doğrulanmış STEP ve yönü belirlenmiş görünüş kameraları.
- Aynı kamera ile projekte edilmiş gerçek geometri sınırları: görünür/gizli çizgiler, kesit konturları, merkez çizgilerinin taşmaları.
- OCR tarafından onaylanmış ölçü örnekleri ve BRep üzerinde çözülmüş bağlantıları.
- Son gösterim metinleri: `_METIN` önceliği, kullanıcının Ø tercihi ve tolerans düzeni uygulanmış metinler.
- Arial glif ölçülerinden hesaplanan gerçek yazı kutuları; eşit toleransta ±, farklı toleransta üst üste sapmalar.
- Antet, sayfa kenar payları, izometrik alanı ve görünüş başlıkları gibi kullanılamayan alanlar.

Geometrik referansı çözülemeyen ölçüleri önce kaydet. Bunları ölçek hatası sayma; ölçek küçültmek eksik referansı düzeltemez. Mevcut çözülemeyenler tablosu kullanılacaksa onun alanını da yerleşim öncesinde ayır. Böyle çıktılar tam başarılı sayılmaz.

## Alan hesabı

Antet ve sabit öğeleri sayfa üzerinde engel dikdörtgenleri olarak tut. Sağ üst izometrik alanını da engel olarak ayır; yalnız onun kapladığı yüksekliği kullan, bütün sağ sütunu boş bırakma. Kesit/ana görünüş alanlarına sabit 240/850 piksel genişlik verme.

Her görünüş için bir paket oluştur: geometri, merkez çizgileri, başlık ve ölçü yerleşimi. Paket dış kutusunu gerçek çizim öğelerinin birleşiminden hesapla. Geometri sınırı tek başına yeterli değildir. Yazıların parçayla veya başka yazılarla temas etmemesi ve ölçülerin dış şeritlerde durması mevcut yerleşim kısıtları olarak korunur.

## Ölçek adayları

Tercih edilen sıra 10:1, 5:1, 2:1, 1:1, 1:2, 1:5, 1:10 ... şeklindedir. Çok küçük/büyük parçalar için aynı tercih dizisini onluk kuvvetlerle genişlet. Geometri ve kullanılabilir alanla bulunan kaba üst sınırdan büyük adayları baştan ele. Keyfî ara ölçek üretme. Özel ara ölçekler gerekiyorsa tercih listesine açıkça eklenir.

İlk uygulanabilir aday kazanır. Daha küçük bir ölçeğin daha estetik görünmesi, bütün katı kısıtları sağlayan büyük ölçeği geçersiz kılmaz. İstenmeyen kenar yakınlığını puanla gizlemek yerine fiziksel kenar payı kısıtıyla ifade et.

## Bir ölçeği deneme

1. Kameralar sabitken ana/kesit geometrisini aday ölçeğe getir. Ayrı ölçülendirme paketlerini oluştur; yazı/ok boyutunu sabit tut.
2. Her paketi yerel koordinatlarda ölçülendir. Dış ölçü şeritleri ve liderlerin alternatifleriyle gereken kenar alanlarını bul. Önceki denemeden çizgi veya yazı bırakmayan geçici bir çizim kullan.
3. Gerçek paket boyutlarıyla kesit solda kalacak şekilde yan yana yerleştir. Her paket kullanılabilir alanda farklı genişlik/yükseklik alabilir. Görünüşteki eksen yönlerini değiştirme.
4. Yerleşim adaylarını engel kenarlarından üret: sayfa kullanılabilir sol/üst sınırları, antet/izometrik sınırları ve diğer paketin kenarı + asgari boşluk. İki görünüş için bunların sonlu kombinasyonlarını değerlendir; rastgele arama kullanma.
5. Yerleşimden sonra lider/yazı alternatiflerini gerçek sayfa engellerine karşı tekrar değerlendir. Bu alternatifler paketi büyütürse kutuyu yeniden hesapla ve aynı aday ölçeğin kalan yerleşimlerini dene. Daha önce denenmiş yerleşim durumlarını tekrar etme; aday listesi sonlu olsun.
6. Geometri, başlık, yazı, ok veya uzatma çizgisi sayfa/antet/ayrılmış alan dışına taşıyorsa; gerekli açıklıklar sağlanmıyorsa; çözümlenmiş bir ölçü yerleştirilemiyorsa bu yerleşimi reddet. Ölçü çizgisinin hedef geometriye kasıtlı teması hata değildir; yasak olan metin kutusunun geometriyle teması ve izinsiz çakışmalardır.
7. Aynı ölçekte birden fazla geçerli yerleşim varsa sırasıyla: en kısa toplam lider, taslaktaki ölçü taraflarını en iyi koruma, daha dengeli boşluk dağılımı; son eşitlikte sabit koordinat sırası. Sonuç aynı girdide aynı olmalı.
8. Hiçbiri geçmezse sonraki küçük ölçeğe geç. Geçerli yerleşimi kaydet ve yalnız bu geçici çizimi nihai çıktıya aktar.

Kullanıcının kestiği V/H düzlemini, fiziksel üst yüzünü veya kamerayı değiştirerek yer kazanma. Ölçek değerlendirmesi mevcut API'den dönen geometriyi yeniden yorumlamaz ve API çağrısı yapmaz.

## Sonuç ve açıklanabilir kayıt

- Seçilen ortak ölçek ve izometrik ölçek.
- Geometri ve tüm açıklamalar dahil paket sınırları, fiziksel kenar açıklıkları.
- Denenen daha büyük her ölçek için somut ret: örneğin `kesit paketi + ana görünüş + boşluk: 178 mm; kullanılabilir genişlik: 164 mm` veya `üst tolerans yazısı izometrik alanına taşıyor`.
- Geometrik bağlantı hataları ile yerleşim/ölçek hataları ayrı listelerde.
- Tüm adaylar başarısızsa ölçüleri düşürerek başarılı sayma. Gerekli fiziksel alanı ve engeli raporla; çıktı inceleme çıktısıysa bunu açıkça belirt.

Antetteki ölçek, gerçek geometri dönüşümünden alınır. Son raster JPEG boyutları veya JPEG içindeki taslak ölçek yazısı karar girdisi değildir.

## Sınama senaryoları

1. Kısa-geniş, uzun-dar ve yaklaşık kare görünüş paketleri: aynı algoritma ve sabit kamera ile çalışmalı.
2. Aynı geometriyi büyüt/küçült: ölçek uygun yönde değişmeli; yazı/ok fiziksel boyutu değişmemeli.
3. Aynı geometriyi farklı JPEG çözünürlüklerinde ver: fiziksel sayfa, ölçek ve paket konumları değişmemeli (raster yuvarlama toleransı hariç).
4. ± toleransı üst üste toleransa, kısa metni uzun metne çevir: artan gerçek yazı alanı taşma üretmemeli; gerekirse ölçek veya yerleşim değişmeli.
5. Antet/izometrik yakınında liderler: bölgelere taşmadan sığmalı.
6. Ölçü bağlantısı eksik: aynı hata ölçek küçülterek gizlenmemeli.
7. Aynı kaynakta +Z'nin sağ/sol ve yukarı/aşağı olması: ölçek seçimi kamerayı değiştirmemeli. Yön doğruluğu ayrı testte sınanmalı.
8. Taslak4.8 ve Taslak6.2 gerçek parçaları: geometri ve ölçü referansları sabit tutularak mevcut ölçekle ve yeni adaylarla karşılaştır; daha büyük aday reddediliyorsa kayıt gerekçesini sınayabil.
9. Seçilen ölçekten bir büyük adayın gerçekten uygulanamaz olduğunu doğrula; yalnızca seçilen adayın sığdığını test etmek yeterli değildir.

Bu belge 1:1 veya 2:1'in Taslak6.2'de mutlaka seçileceği iddiasında bulunmaz. Nihai karar, çözülmüş ölçüler ve gerçek paket yerleşimiyle verilir. Mevcut üretimde referansı çözülmemiş ölçüler bulunduğundan yalnız mevcut eksik JPEG'e bakarak tam yerleşim başarısı çıkarılamaz.
