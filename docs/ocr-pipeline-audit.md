# OCR süreci incelemesi — 4 Kasım 2026

Salt inceleme: OCR kodu veya ayarları değiştirilmedi; yeni API çağrısı yapılmadı. Bulgular mevcut kod ve Taslak6.4/6.5 ham TSV kayıtlarından çıkarıldı. Bu belge düzeltmelerin uygulandığı anlamına gelmez.

## Etkin süreç

CadQueryPipeline geometri ve ölçü çağrılarını yapar. Pafta aşamasında cad_script_sheet → template_layout.prepare → inspect_bracket_layout.inspect çalışır. inspect_template_dimensions içinden bu akışa yalnız REGIONS sabiti alınır; o dosyanın ayrı inspect fonksiyonu etkin parantez OCR işlemi değildir.

1. JPEG RGB okunur; Excel etiketleri ve Ø bilgisi sözlük olur.
2. Kesit/ön/izometrik için sabit normalize bölgeler kırpılır.
3. Her bölge 15° adımlarla 24 yönde döndürülür.
4. Ham görüntü ve çizgileri temizlenmiş görüntü PSM 11 ile okunur; bazı açılarda sabit boyutlu yerel kırpmalar PSM 7 ile eklenir. Üç görünüş için en az 144 Tesseract çağrısı ve ilave yerel çağrılar vardır. Bu, tek bir salt JPEG okuması değildir; mevcut ilk tarama akışının çoklu varyantlarıdır.
5. Aynı TSV satırındaki en fazla 12 kelime birleştirilip parantez söz dizimi aranır; sınırlı karakter düzeltmeleri ve güven filtresi uygulanır.
6. Yakın konumlar birleştirilir; tek aday tutulur. Sonra Excel etiketi/sabit ölçü sınıflandırması yapılır.
7. Sonuç önbelleğe alınabilir. Model işaretleri OCR adaylarına metin ve konumla bağlanır. OCR onayı olmadan model yeni çizilebilir etiket oluşturamaz.
8. Eşleşmeyen ölçüler omitted olur; çözülemeyen geometrik referanslar unresolved olur. Genel başarı kararı yalnız unresolved listesine bakar.

## Öncelikli, kayıtlarda görülmüş bulgular

### 1. Sabit kırpma bölgeleri metni kesiyor

Kod: tools/inspect_template_dimensions.py REGIONS; tools/inspect_bracket_layout.py:77–78.

Kesit x=.035… .29; ön görünüş x=.35… .81. Arada hiç taranmayan şerit var. Bir etiketin görünüşün dışında bulunması normal; bu kırpmalar ölçü metninin hangi görünüşe ait olduğunu belirleyemez. Taslak6.4'te 2,8 için ön kırpmanın x=0 kenarında `8]` parçası görülüyor. Tam etiketin kırpma dışında kalan kısmını OCR geri getiremez.

Taslak6.5'te C tam sayfa ham okumada `[C]`, fakat kesit kırpmasının ham okumasında `[C.`. Bölge/segmentasyon seçiminin etkisi doğrudan görülüyor; yalnız kaynağı suçlayamayız. Bunun hangi Tesseract segmentasyon ayrıntısından doğduğunu henüz ayrı kontrollü deneyle belirlemedik.

Öneri: görünüşlerden bağımsız tam çizim alanı veya sınırda kelime kesmeyen bindirmeli alanlar; sonradan model referansıyla görünüş ataması. Kırpılmış etiketin kalanını tahmin etme.

### 2. Doğru okuma erkenden siliniyor

Kod: inspect_bracket_layout.py candidate_rank ve :131–135.

Aynı konumda bilinen Excel etiketi öncelikli; sonra güven puanı yüksek olan kazanıyor. Farklı açılardaki güven puanları doğruluk olasılığı gibi karşılaştırılıyor.

- 6.4: E, 270° okumada 55.48 güvenle doğru. Aynı konumdaki J, 90° okumada 62.34 ile E'yi eziyor.
- 6.5: 5, yerel kırpmada 34.35 ile doğru. Ham bölge 93.06 güvenle 9 okuyor; yanlış 9 tutuluyor.

Öneri: konumsal gösterim kümesi altında ham alternatifleri, açı/variant ve sınır kutularını koru. Güven tek başına karar olmasın. Model yalnız gerçekten OCR'de görülmüş, mekânsal olarak uyumlu alternatifler arasındaki eşleşmeye yardımcı olabilir. Yeni parantez icat etmesine gerek yok.

### 3. Eksik ölçüler başarı durumunda kaybolabiliyor

Kod: template_layout.py:64; src/CadQueryPipeline.cs son pafta değerlendirmesi.

OCR eşleşmesi olmayan ölçü omitted olur. Genel sonuç yalnız unresolvedDimensions sayısını denetler. Bu nedenle 6.4'te C/E/2,8/25 eksikken sheets-produced üretildi. K'nin kasıtlı dışlanmasıyla gerçek etiket kaybı aynı genel gerekçeye düşüyor.

Öneri: kasıtlı parantezsiz/geometri-only veri, onaylanmış etiket, modelin işaretlediği ama OCR'nin doğrulamadığı etiket ve geometrik referans hatası ayrı raporlansın. OCR doğrulamadı diye doğrudan çizme; ama tam başarı da deme. Excel'deki her sütunun çizilmesini istemek doğru çözüm değil: K bunun karşı örneği.

### 4. Simgeler bozulabiliyor; metin aynı ölçüyle eşleşmeyebiliyor

Kod: parse_token, normalize_label, visible_plus_minus; visual_measurements.canonical.

6.4 Ø25 ±0,5 parçaları `[£25`/`+0,5]`, temiz görüntüde `[G25`/`40,5]`. 6.5'te 25±0,5 oluştu, Ø kayboldu. Kaybolan simgeyi sadece ölçü değerinden geri üretmek kullanıcının Ø tercihini bozabilir.

Basit sayılarda virgül/nokta normalleşiyor, karmaşık ifadeler aynı kapsama sahip değil: Ø25±0,5 ile 25±0,5, 25±0.5 ile 25±0,5 aynı davranışta ele alınmıyor. Kimlik, nominal, çap işareti ve tolerans metninin tek karşılaştırma anahtarında tutulması kırılgan.

Öneri: ham metni koruyup kimlik ve gösterim niteliklerini ayrı işle. Ø/± kararını sayı değerinden uydurma. Simge belirsizliğini raporla.

## Kodda görülen, etkisi ayrıca ölçülmesi gereken riskler

### 5. Sabit piksel eşikleri ve dar yerel kutular

180 parlaklık eşiği; 65/120 piksel çizgi çekirdekleri; karakter için 35–110 piksel yükseklik; 260×130 yerel kırpma; 40 piksel yakınlık tabanı. DPI ve yazı boyutu değişirse yerel aday seçimi/temizleme/birleştirme davranışı değişir. Uzun Ø/tolerans metni 260 piksele sığmayabilir. Ham PSM 11 yolu kaldığından bu eşikler bütün OCR yollarını tamamen kapatmaz, ama yerel desteği etkiler.

Öneri: görülen yazı ölçeğinden türetilmiş eşikler ve metin grubuna göre kutu; özgün görüntüyü koruma. Aynı çizimi farklı çözünürlüklerle test et.

### 6. Çizgi temizleme yazıyı etkileyebilir

Morfolojik çizgi maskesi metinle çakışırsa parantez veya simge parçasını silebilir. Yerel ROI'ye alınma da temizlenmiş bağlı bileşenlerden türetiliyor; özgün metin daha OCR yapılmadan aday dışı kalabilir. Etrafına oval çizmek fazladan çizgiler ekler; mutlaka iyileştireceği varsayılmamalı. C'de temizlenmiş okuma yanlış, ancak 6.5 kırpılmış ham okuma da yanlış olduğundan C'nin tek nedeni çizgi temizleme değildir.

Öneri: metin/parantez bölgelerini koruyan çizgi temizleme; ham/temiz varyantların hiçbirini erken silmeme. Doğru sonucu hangi varyantın getirdiğini raporla.

### 7. Döndürme ve segmentasyon seçimi

PIL rotate'da resample açıkça seçilmiyor; varsayılan nearest yöntemi eğik açılarda kenarları tırtıklayabilir. Açı 15° basamaklı. Bazı açılarda yerel okuma var, diğerlerinde yok; 90°/180° yerel PSM 7 kümesine dahil değil. Geniş alan PSM 11, yerel tek satır PSM 7; çerçeve veya lider karakterleri satır gruplamasını değiştirebilir. `eng` tanıma verisi teknik simgelerin doğruluğunu garanti etmez.

Öneri: aynı ilk tarama içinde metnin yönünü/kutusunu uygun çözünürlükte ele al; enterpolasyon/PSM seçeneklerini gerçek veriler üzerinde karşılaştır. Daha fazla döndürmenin otomatik olarak daha doğru olduğu varsayılmamalı.

### 8. Parantez, kelime grubu ve karakter kurtarma kuralları

Yalnız aynı TSV satırında ve en çok 12 kelime içinde birleştirme var. Parantezler farklı satır/bloklara ayrılırsa içerik kaybolur. Genel söz dizimi `[9]` gibi yanlış ama geçerli sayıları da kabul eder. `[Al` → A kurtarma, A Excel'deyse kapanış l'yi parantez varsayar; iki gerçek köşeli parantezi piksel olarak kanıtlamaz. Ø/O ile başlayan harf etiketleri için prefix kaldırma meşru çok harfli kimliklerle çakışabilir.

Öneri: metin kutularının mekânsal gruplaması, kimlik sözlüğü ve gösterimin parantez kanıtını ayrı tut. Kurtarmanın uygulandığı adayları ham doğrulanmış adayla eşit sayma. İki yan çizgi barı, özellikle oval çerçevelerde, tek başına köşeli parantez kanıtı değildir.

### 9. Yakınlık birleştirmesi yalnız merkez uzaklığına bakıyor

Aday kutularının örtüşmesi veya gerçek gösterim sınırı yerine merkez ve piksel eşiği kullanılıyor. Yakın iki ayrı etiket birleşebilir; aynı etiket kırpılmış/uzun varyantıyla ayrı kalabilir. İlk bulunan yakın aday seçiliyor; bu greedy karar işlem sırasından etkilenebilir. Mevcut konum yakınlığı tek başına aynı fiziksel yazı olduğunu ispatlamaz.

Öneri: sınır kutusu, ölçek ve metin alternatifleriyle gösterim kümeleri; aynı değerdeki farklı fiziksel gösterimler korunmalı.

### 10. Model–OCR eşleştirmesinde uzaklık sınırı yok

visual_measurements.merge, aynı etikette en yakın adayı alıyor; ne kadar uzak olduğuna dair üst eşik yok. Aynı yazı farklı yerlerdeyse yanlış gösterime bağlanabilir. Eşleme marker sırasıyla greedy; uygun boş aday yerine daha önce kullanılan en yakın adaya denk gelirse hata verir. Bu kısım yakın okumaları yanlış yüzeye bağlama riskidir; OCR harf tanımasından ayrı aşamadır.

Öneri: normalize konum/kutu ve görünüş kanıtıyla sınırlı, bire bir eşleme; başarısız eşleşme açık raporlanmalı. Modelden gelen kutu sayısal olarak geçerli diye görsel olarak doğru kabul edilmemeli.

### 11. Önbellek kod ve araç sürümünü otomatik izlemiyor

prepare anahtarı: VERSION + JPEG hash + Excel etiket/çap sözlüğü. OCR kodu, REGIONS, eşikler, Tesseract sürümü/ayarları değişip VERSION unutulursa eski sonuç kullanılır. Önbellek isabetinde o çalışmanın ham OCR kayıtları klasörde oluşmayabilir.

Öneri: gerçek OCR yapılandırması/kod/araç sürümü özeti ve cache hit/miss kaydı. Yalnız manuel sürüm etiketine güvenme.

### 12. Kaynak görünüş çerçevesi bulma varsayımları

source_frames halen kesiti upright varsayan uzun dikey çizgi aramasını kullanıyor. Sayfa bölgesindeki çember araması da sabit sınırlar içinde. Modelin sağladığı çerçeveler bunu aşabiliyor; eksik geldiklerinde çerçeve bulunamayabilir. Bu harf okuma hatası değil, bulunan etiketi çizime bağlama hatasıdır. İki aşamanın hata raporu ayrılmalı.

## Öncelik önerisi

1. OCR kaybını görünür kılan doğru rapor; K gibi kasıtlı istisnaları koru.
2. Etiketi kesmeyen çizim alanı taraması ve alternatifleri silmeden tutma.
3. Model–OCR arasında sınırlı bire bir eşleme.
4. Ölçeğe uyarlanmış ön işleme ve metin gruplama.
5. Gösterim standardı deneyleri: [C] gibi yalnız kimlikler veya DIM_C gibi ayırt edici ASCII önek. 25/2,8 değerleri ve toleranslar Excel'de tutulabilir. @ yüzey etiketleriyle karıştırılmamalı. Yeni formatın üstünlüğü gerçek taslaklarda ölçülmeden garanti edilmez.

Başarı ölçütü yalnız bulunan aday sayısı olmamalı: gerçek gösterim başına doğru etiket, yanlış kabul, eksik okuma, Ø/± gibi nitelik kaybı, yanlış konum eşleşmesi ayrı sayılmalı. Sabit bir referans veri kümesiyle 6.2–6.5 ve farklı çözünürlük/yön/boşluk varyantları karşılaştırılmalı. Aynı yeni örneğe göre kural ayarlamak genelleme kanıtı değildir.
