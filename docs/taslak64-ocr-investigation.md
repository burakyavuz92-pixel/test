# Taslak6.4 — kayıp OCR etiketlerinin incelenmesi

Kaynak: canlı çalışmanın her açı/variant için saklanan Tesseract TSV kayıtları, `detections.json` ve üretim kodu. Yeni API çağrısı yok. Dört sorunun tamamı aynı nedenden kaynaklanmıyor. Bu inceleme OCR kurallarını değiştirmez; aşağıdakiler çözüm önerileridir.

## E: aday seçimi hatası — doğrulandı

`ocr-front-270.json` ham çıktısında `[E]` güven 55.482857 ile mevcut. Tam görüntüde merkez [3236.5,2144]. Sonuç dosyasında aynı merkezde `[J]` var: 90° okumada güven 62.343613. Kod aynı konumdaki adaylardan ikisi de bilinen Excel etiketi olduğunda yüksek güvenliyi seçtiğinden E'yi kaybetmiş. Modelin E'yi görememesi veya Excel eşleşmesinin olmaması söz konusu değil.

Öneri: konumsal küme için farklı etiket okumalarını erken silme. OCR'de gerçekten görülmüş alternatifleri koru; modelin etiket/konum bilgisiyle tek gösterimi eşleştir, aynı fiziksel gösterimin iki kez kullanımını engelle. Aynı adayın farklı açıları farklı Excel harflerine dönüşebildiğinden yalnız güven puanı yeterli değildir. Bir J'nin varlığı diğer gerçek J gösterimlerini yasaklamamalı.

## C: kapanış parantezi okunmamış — doğrulandı

`ocr-section-0.json` temizlenmiş variantta `[C.` güven 59.979534 olarak var. Tam `[C]` koşulunu sağlamadığı için aday kabul edilmiyor. Çizgi temizleme/segmentasyonun etkisi olasıdır; yalnız bu kayıt, hangi görüntü işleminin fiziksel çizgiyi bozduğunu kesin kanıtlamaz.

Öneri: yazı/parantez bileşenlerini çizgi silmeden önce koruyan ön işleme; aynı ilk okuma akışında doğru kırpma/boşluk ve segmentasyon. `[C.` → `[C]` şeklinde koşulsuz metin değiştirme yapılmamalı; gerçek parantez geometrisi veya belirlenen etiket standardı doğrulanmalı.

## 2,8: kırpma sınırı — güçlü doğrudan kanıt

Kesit x=0.035…0.29, ön görünüş x=0.35…0.81 ile kırpılıyor. Etiket bu alan sınırını aşıyor. `ocr-front-0.json` içinde kırpmanın sol kenarında x=0 konumunda `8]` parçası var. Önceki bölüm bölge dışında kaldığı için içerik birleştirilemiyor.

Öneri: OCR'nin görünüş ataması için sabit ayrık bölgelere ihtiyacı yok. Çizim alanını bütün olarak veya etiketleri sınırdan kesmeyecek bindirmeli alanlarla ilk geçişte tara. Görünüşü daha sonra modelin referansı belirlesin. Bu ayrı bir başarısız etiket tekrar-okuma aşaması gerektirmez.

## Ø25 ±0,5: birden fazla karakter karışmış — doğrulandı

`ocr-front-315.json` ham variant: `[£25` ve `+0,5]`; temizlenmiş variant: `[G25` ve `40,5]`. Son reddedilmiş aday `[G2540,5]`. Ø, ± ve kapanış/parçalama sorunları bir arada. Yalnız karakter normalizasyonu ile 25±0,5'i varsaymak güvenilir olmaz.

Öneri: önce ilk-geçiş görüntü hazırlamasını/adayları düzelt. İsteğe bağlı olarak geometrik kimlikle sayısal gösterimi ayır: taslakta yalnız kısa kimlik, sayısal değer/Ø/tolerans Excel'de. Böylece OCR Ø/±/ondalık virgül okumak zorunda kalmaz.

## Gösterim standardı seçenekleri

1. **Mevcut [C], [E] biçimi korunur.** Önce kırpma ve alternatifleri silme hatalarını düzelt. Taslak hazırlama yükü değişmez. Sayısal karmaşık etiketler yine zorlayabilir.
2. **Bütün ölçülere harf kimliği verilir:** örneğin 25 için [L], 2,8 için [M]; değer ve toleransları Excel L/M sütunlarına girilir. K yine düz K olarak geometri bilgisi sağlayabilir, ama çizim etiketi sayılmaz. OCR yalnız kısa kimlik okur; parantez sorunu tek başına ortadan kalkmaz.
3. **Ayırt edici ASCII önek:** `DIM_C`, `DIM_E`, `DIM_L`, `DIM_M`. İki köşeli parantezi aynı anda okuma koşulu kalkar. Bu destek henüz yazılmadı; çizimde başka sıradan metinlerin ölçü sayılmaması için yalnız belirlenen önek kabul edilmelidir. @ öneki montaj yüzeyleriyle karışacağından tercih edilmez. Sadece çıplak harf kullanımı, sıradan yazıyla ayrımı kaybettirir.

Önerilen sıra: önce kesilmeyen ilk tarama ve OCR alternatiflerini koruma; kullanıcı formatı değişecekse yalnız kimlik kullanan biçimi değerlendirme. Yeni öneğin daha iyi olduğunu gerçek taslaklarda karşılaştırmalı ölçmeden garanti etmeyelim. Sentetik temiz yazıda başarılı olmak gerçek ölçü çizgileri içindeki başarıyı kanıtlamaz.

Ayrıca mevcut `sheets-produced` durumu atlanan ölçüleri tam başarıdan ayıramıyor. Modelin işaretlediği ama OCR'nin onaylamadığı ölçüler ayrı bir inceleme listesinde raporlanmalı; doğrudan çizilmemeli. K gibi kasıtlı parantezsiz girdiler bu eksik listesiyle karıştırılmamalı.
