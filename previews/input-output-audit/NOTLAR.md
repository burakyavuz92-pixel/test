# Girdi, özgün yanıt ve kod incelemesi

Yeni API çağrısı, yeni çizim veya uygulama kodu değişikliği yapılmadı. Son renk denemesinin yerel kayıtları, özgün API yanıtı ve mevcut gönderim/dönüştürme kodu incelendi. Makineyle yapılan karşılaştırmalar checks.json dosyasında.

## Doğrulanmış bulgular

1. **XY orijin sözleşmesi eksik.** CadGroupWorkflow.cs promptu X sağ/Y yukarı, ön yüz Z=0 der; ancak XY orijininin gövdenin ana ekseninde olduğunu açıkça söylemez. `kind:origin` koordinatı sıfır olarak tanımlarken sıfırın gövdede hangi noktaya bağlı olduğunu belirtmez. "Choose the reference hole" ifadesi de delik referansını öne çıkarır. Native worker gövdeyi gp_Pnt(0,0,0) çevresinde döndürerek oluşturur; modelin gövde merkezini başka bir yere koyacağı alan yoktur. Özgün yanıt E deliğini XY=0 kabul eder. Aynı koordinat çerçevesi karşılıklı tanımlanmadığı için gerçek bir arayüz eksikliğidir. Ancak tek başına B/G'nin yanlış uçlardan okunmasını bütünüyle açıklamaz.

2. **Excel nominal verisi bu örnekte bozulmamış.** Yeni Excel'in XML hücreleri doğrudan okunup gönderilen geometry-input.json ile karşılaştırıldı: 4 satır × 7 sütunun tamamı eşleşiyor. Boş E/F null; gerçek F=0 sıfır; B=165,4 ve G=78,7 doğru gidiyor. Nominal ve tolerans alanları ayrılmış. Kaynak SHA256 özetleri son çalışmayla aynı.

3. **Yanlış bağlantı özgün API yanıtında var.** api-response.json içindeki content JSON'u kaydedilmiş analysis-plan.json ile yapısal olarak aynı. E orijin, C/D'nin F ile sağa konması, B'nin yanlış referansı ve G'nin C'den ölçülmesi sonradan çözücü tarafından eklenmiş değil. Yanıt normal stop ile bitmiş; max_tokens=6000 sınırına çarpıp kesilmemiş.

4. **Tek analizde çok sayıda birbirini tekrarlayan karar isteniyor.** Gönderilen prompt 14.619 karakter; geometri/annotation Excel tabloları da buna dâhil. Model görüntüyü okumayı, özellik adlandırmayı, koordinat bağımlılıklarını, görünürlüğü, kesiti, kamerayı ve raporu aynı çıktıda çözüyor. Aynı ölçü bağlantısı geometry, annotations ve measurementSources içinde tekrarlanıyor. B/F/G için bu alanların çeliştiği özgün yanıtta görülebiliyor. Tek kaynaktan türetilmek yerine yeniden tarif edilmeleri sözleşme tasarımı sorunu.

5. **Renk ayrımı gerçek bilgi izolasyonu değil.** Kırmızı çıkarılmış görüntü ile özgün renkli görüntü aynı çağrıda gönderiliyor. Model her ikisini de görüyor. Renk ön işleme konumları değiştirmiyor; yakın incelemede siyah ana eksen ve ölçü çizgileri duruyor. Çok açık kırmızı yazı kalıntıları kalmış. "Geometri kırmızıdan kesin etkilenmez" garantisi yok.

6. **Doğrulama bağımsız resim okuması değil.** Ölçünün bağlantısını model seçiyor; sayı kontrolü yine bu seçime göre yapılıyor. Yanlış fakat kendi içinde tutarlı plan geçebilir. Yeni uç-tutarlılığı kontrolü çelişen beyanları yakalar, JPEG'deki gerçek uçları bağımsız doğrulamaz. horizontalOffset/verticalOffset mutlak değer karşılaştırır; yanlış taraf tek başına bu sayısal kontrolden anlaşılmaz. Bir satır çözülemeyen özelliğe bağlanınca satırın kalan kontrolü atlanır; rapor bütün hataları tek seferde göstermeyebilir.

## Güçlü fakat henüz deneyle kanıtlanmamış olası etkenler

- İki tam 7016×4961 pafta gönderiliyor; görünüşlere/ölçü uçlarına ait yakın görüntüler yok. image_url.detail açıkça belirtilmiyor. Gönderilen yüksek piksel sayısının sağlayıcı/model içinde aynı ayrıntıyla işlendiğini bilmiyoruz; sağlayıcının gerçek küçültme politikasını bu kayıttan kanıtlayamayız.
- reasoning.effort=low gönderiliyor. Sağlayıcı yanıtı reasoning_tokens=0 bildiriyor. Bunun modelin hiç akıl yürütmediğini kanıtlamadığı gibi, hatanın kesin nedeni olduğunu da söyleyemeyiz. Ancak bu zor görev için düşük bütçe seçimi kontrollü karşılaştırmada ele alınmalı.
- Promptun son JSON örneğinde measurementSources ve colorPolicyVersion yok; bunlar yalnızca önceki metinde isteniyor. Model bu denemede alanları döndürmüş, dolayısıyla mevcut hatanın doğrudan nedeni değil; yine de şema tutarsızlığı.
- centerDistance uygulaması Öklid uzaklığı hesaplıyor; teknik resimdeki yatay/dikey izdüşüm mesafesi her zaman bununla aynı değildir. Bu örnekte üst/alt delikler aynı X üzerinde olmalı; farklı taslaklarda ayrım açıkça modellenmeli.

## İnceleme sınırları

Tarihsel HTTP gövdesinin tamamı saklanmamış. Gönderim yapısı kod, saklanan prompt, ayrıştırılmış tablolar ve görüntülerden incelendi; ağ üstündeki baytların bağımsız kaydı yok. Sağlayıcı model ve provider adları yanıtın bildirdiği bilgilerdir. Reasoning_tokens=0 veya image_tokens=0 tek başına görselin kullanılmadığını kanıtlamaz. OCCT'ye hiç gitmeyen son analizdeki yanlış B/F/G bağlantıları OCCT çiziminden kaynaklanamaz.

## Önerilen sıra

1. Gövde/datum ile orijin arasındaki sözleşmeyi açıklaştırmak. Mevcut dairesel ailede ana eksen–ön yüz kesişimi; gelecekte modelin tanımladığı datumla motorun kullandığı datum aynı olmalı. Kullanıcıdan tek tek koordinat girişi istemek gerekmiyor.
2. Modelden ölçü uçlarını ve gözlenen ilişkileri bir kez almak; geometri bağımlılıklarını ve annotation bağlarını aynı kayıttan türetmek. B/G'ye özel doğru cevabı prompta gömmemek.
3. Genel pafta görünümüyle birlikte ölçü uçlarının okunabileceği ayrıntı görüntüleri sunmak. Siyah ana eksen ve ölçü çizgileri korunmalı.
4. Bu düzen sabitken görsel ayrıntı/akıl yürütme ayarı veya model karşılaştırmasını tek değişkenle yapmak. Önce ölçü uçlarının doğru okunup okunmadığına bakmak; çizim üretmeden değerlendirmek.

Sonuç: Kullanıcının parçayı koordinatlarla yeniden tarif etmesine geçmeden düzeltilecek gerçek arayüz ve sunum eksikleri var. Hata yalnızca tolerans, kırmızı not veya "model uygun değil" diye açıklanamaz. Orijin düzeltmesinin bütün sorunları çözeceği de mevcut kanıtla söylenemez.
