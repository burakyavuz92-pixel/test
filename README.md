# Teknik resim aracı — ilk teknik deneme

C# / .NET 8 konsol prototipi. Genel amaçlı ürün henüz değildir. İlk adaptör yalnızca merkezde simetrik iki delikli dairesel parçayı destekler. Excel her satırda aynı yapıda bir parçayı tarif eder. Farklı aileler için geometri adaptörleri daha sonra eklenecek.

## Çalıştırma

.NET 8 SDK ile VS Code terminalinde depo kökünden:

```bash
dotnet restore src/DrawingTool.csproj
dotnet run --project src/DrawingTool.csproj -- preview samples/taslak1.xlsx samples/plate.json output
```

`output/preview.jpeg` ve manifest oluşturulur. Görseli kontrol ettikten sonra komutun verdiği özeti kullanın:

```bash
dotnet run --project src/DrawingTool.csproj -- batch samples/taslak1.xlsx samples/plate.json output --approve HASH
```

Excel veya şablon değişince eski onay geçersizleşir. Mevcut ürün çıktıları üzerine yazılmaz. `jpeg file name` benzersiz olmalı; bu sürüm harf, rakam, tire ve alt çizgi kabul eder. Ölçüler mm; ondalık virgül/nokta, Ø, ± ve `(+0,1|-0,0)` desteklenir. Asimetrik toleranslar alt/üst yazılır. Nominal değer geometriye uygulanır.

## OpenRouter analizi (ayrı adım)

`OPENROUTER_API_KEY` ve `OPENROUTER_MODEL` değişkenlerini terminal ortamında tanımlayın. Anahtarı repoya yazmayın. Görüntü girdisi ve JSON yanıtı destekleyen bir model seçin.

```bash
dotnet run --project src/DrawingTool.csproj -- analyze /path/reference.jpeg samples/taslak1.xlsx 11-30-10 recipe.json samples/user-context.json
```

Bu komut ücretli API çağrısı yapar ve görseli + referans satırı OpenRouter'a gönderir. Modelden yürütülebilir kod alınmaz. Cevap veridir; desteklenmeyen aile ve eksik et kalınlığı çizim aşamasında reddedilir. Bilinmeyen sabitleri kullanıcı gözden geçirir. Örnekteki 3 mm kullanıcı tarafından doğrulanmıştır; JPEG etiketinde yoksa API'nin bunu bilmesi beklenmez.

## Sınırlar — mutlaka okuyun

- Ön görünüş nominal çap ve delik konumlarını kullanır.
- Kesit ve eğik görünüş aynı parametreleri kullanır ancak **şematiktir**. Eğik görünüş gerçek CAD izometrik izdüşümü değildir; görünürlük/örtülme hesabı yoktur.
- Derinlik bilinmediğinden örnek şablonda null bırakılır; yalnızca görsel yerleşim için çapın %14'ü kullanılır. Kıvrım/kenar geometrisi kesin değildir. Üretim belgesi olarak kullanmayın.
- Özgün antet ve JPEG arka planı bu denemede aktarılmaz. Yazı tipi DejaVu Sans'tır; özgün font eşleşmesi henüz yapılmadı.
- Çıktı 2400×1600 JPEG; fiziksel baskı ölçeği tanımlı değildir. Tüm görünüşler sayfa düzenine göre şematiktir; 1:1 iddiası yoktur.
- Onay özeti bu sürümde Excel ve tarif dosyasını bağlar. Kaynak JPEG'in arşivlenmesi ve onay kaydına bağlanması sonraki aşamadır.
- OpenRouter görsel analiz çağrısı anthropic/claude-sonnet-5.5 ile gerçek JPEG üzerinde doğrulandı. Bu test aileyi ve A–E eşlemesini önceden açıklayan istem kullanır; genel geometriyi yönlendirmesiz çıkarabildiğini kanıtlamaz. Otomatik model seçimi, yeniden deneme ve maliyet raporu yoktur.

Sonraki karar noktası: ön görünüş ve Excel akışı onaylandıktan sonra gerçek kesit/izometrik geometri ve antet korunması üzerinde çalışmak.

## Gerçek görsel analizi sonucu

`reference-upload.jpeg` ZIP içinden alınan kaynaktır. `user-context.json` kullanıcı tarafından doğrulanan sabitleri içerir; modelin tahmini değildir. `openrouter-analysis.json` API sonucudur. `output/api-preview/preview.jpeg` bu sonuçtan üretilen şematik önizlemedir. Model derinliği bilinmiyor bıraktı; çizim motorundaki yaklaşık derinlik kuralı devam eder. Yanıtta Markdown JSON çiti bulunması güvenli şekilde temizlenir; kalan içerik JSON olarak ayrıştırılır.

## Yönlendirmesiz analiz denemesi

```bash
dotnet run --project src/DrawingTool.csproj -- analyze-free samples/reference-upload.jpeg samples/taslak1.xlsx 11-30-10 samples/independent-analysis.json
```

Bu ayrı modda parça ailesi, delik sayısı, harflerin anlamı veya simetri önceden söylenmez. Yalnızca genel görev, görsel ve referans satırındaki veriler gönderilir. İsteğe bağlı son argüman kullanıcı tarafından doğrulanan sabitleri içeren context JSON dosyası olabilir; ilk bağımsız denemede kullanılmaz. Çıktı, çizim tarifinden ayrıdır ve otomatik olarak çizim motoruna uygulanmaz. Kaynak görsel özeti, model ve API kullanım metadatası ayrı `.meta.json` dosyasında tutulur. Modelin kendi confidence beyanı doğruluk garantisi değildir. Bu komut hâlâ ilk prototipin Excel okuyucusunu kullanır; A–E dışındaki değişkenleri okuma henüz genelleştirilmedi.

Bağımsız test sonucu: `samples/independent-review.json`. A–E eşleşmeleri, nominal değerler ve toleranslar bu örnekte doğru. Model delik simetrisi hakkında yanlış bir çıkarım yaptı. Bu nedenle analiz otomatik çizim tarifine çevrilmedi. Kullanıcının doğruladığı 3 mm ve simetri bilgileri bağımsız denemeye kasıtlı olarak gönderilmedi; bunlar üretim akışında korunmalı ve model çıkarımlarına göre değiştirilmemeli. Tek görsel sonucu genel doğruluk oranı değildir. API'nin bildirdiği bu çağrı maliyeti 0,029738 USD.

Son net JPEG denemesi: `samples/clear-reference.jpg`, model sonucu `samples/clear-analysis.json`, değerlendirme `samples/clear-review.md`. Model 3 mm, 33,5 mm ve B/2 notunu okudu; fakat E'yi açıklamada görmesine rağmen yapılandırılmış eşleşmelere eklemedi. Bu sonuç tamamlanmış çizim tarifi olarak kabul edilmedi.

## Analiz veri kontrolü

```bash
dotnet run --project src/DrawingTool.csproj -- validate-analysis samples/taslak1.xlsx 11-30-10 samples/clear-analysis.json output/validation.json
```

Komut raporu JSON olarak yazar; eksik E içeren eski analiz için beklenen çıkış kodu 1'dir. Kontrol referans satırındaki tüm dolu başlıkları dinamik okur: eksik/tekrarlı/bilinmeyen etiket, nominal değer, tolerans sapmaları ve metin alanlarının valueText değerini denetler. Düşük güven ve engelleyici sorular reddedilir; orta güven uyarıdır. Ondalık nokta/virgül ve tolerans ayırıcıları normalleştirilir. Part numarası gibi metinler nominal ölçüye dönüştürülmez. Kullanıcı onayı yerine geçmez; geometri anlamı ve üç görünüş tutarlılığı bu kontrollerle kanıtlanmaz.

`analyze-free` artık her çağrıda bu kontrolü otomatik çalıştırır; rapor `<analysis>.validation.json` olarak yazılır. Red cevabı inceleme için saklanır ama başarılı sayılmaz. Eksik alanlar program tarafından sessizce doldurulmaz. İstek modelden bütün sütunları ve metin değerlerini açıkça ister. Yeniden deneme otomatik ve sınırsız değildir.

Çevrimdışı regresyon kontrolü (önce build): `python checks/validate_analysis.py`. Özel dotnet konumu için DOTNET_EXECUTABLE ortam değişkenini ayarlayın. Kontroller sentetik mutasyonları kullanır; gerçek model yanıtı olarak sunulmaz.

## Kaynak anteti koruyan pafta önizlemesi

```bash
dotnet run --project src/DrawingTool.csproj -- preview-sheet samples/taslak1.xlsx 11-30-10 samples/validated-analysis.json samples/clear-reference.jpg output/sheet-preview.jpeg plate-clear-v1
```

İsteğe bağlı son argüman başka ürün satırıdır (ör. `11-30-505`); analiz referansı yine `11-30-10` kalır. Her hedef satırın Excel değerleri doğrudan kullanılır. Mevcut çıktı üzerine yazılmaz. Analizin kaynak SHA256 kaydı seçilen JPEG ile eşleşmek zorundadır. Eşleştirme kontrolü geçmeden önizleme yapılmaz. Yanındaki `.jpeg.json` dosyası kaynak/analiz özetlerini ve kullanılan sabitleri kaydeder, HumanApproved=false yazar.

Bu ilk aile adaptörünün sınırları:

- `plate-clear-v1` yerleşimi bu 1487×1044 JPEG üzerinde **elle kalibre edilmiştir**. Genel yerleşim tanıma henüz yoktur. Kod herhangi bir yeni paftayı otomatik çözüyor iddiasında değildir.
- Sabit 3 mm kalınlık, 33,5 mm derinlik ve yaklaşık 4 mm büküm yarıçapı `samples/plate-sheet.json` dosyasındadır. Yarıçap ölçülmüş değer değildir. Bu grubun cidarları önizlemede aynı kalınlıkla yaklaştırılır.
- Ön/ kesit nominal geometriye göre yeniden çizilir; tarama, delik kesintileri, ölçüler ve toleranslar oluşturulur. B/2 açıklaması konum kuralı olarak uygulanır; yardımcı ölçü ve kırmızı açıklama nihai görünüş alanında gösterilmez.
- İzometrik, örneklenmiş dairelerin ortografik 3B izdüşümüdür. CAD katı model çekirdeği veya tam görünürlük hesabı kullanılmaz; kıvrımlar ve izometrik yüzey ayrıntıları basitleştirilmiştir.
- Ana görünüş ve kesit aynı piksel/mm ölçeğini kullanır; izometrik bunun 0,43 katıdır. Sayfaya sığdırma büyük parçalarda ölçeği azaltır. Fiziksel baskı ölçeği yoktur; antetteki 1/1 yerine SIĞDIR yazılır.
- Kaynak antet/çerçeve raster olarak korunur; parça numarası ve ölçek hücreleri kontrollü değiştirilir. Özgün JPEG'in yazıları vektöre çevrilmez; 2× çıktı bunları daha detaylı hale getirmez. Yeni çizgiler ve yazılar 2× çözünürlükte oluşturulur.
- Yazı tipi DejaVu Sans; özgün teknik yazı tipiyle tam eşleşme yoktur. İnsan onayı henüz alınmadı; bu komut toplu üretim onayı değildir.

### A4 düzeltmesi (v2)

Yeni `preview-sheet` çıktıları A4 yatay 3508×2480, JFIF 300 DPI'dır. Görsel en-boy oranını bozmadan ortalanır. Ana/kesit görünüş için sayfaya uyan 1:1, 1:2, 1:5… ölçek seçilir; referans ürün için 1:2'dir. İzometrik ayrı 1:5 ölçekle etiketlenir. Antetteki A2 yazısı A4, SIĞDIR yazısı gerçek ana ölçek ile değiştirilir. Ölçek ve fiziksel boyutlar `.jpeg.print.json` dosyasındadır. %100/gerçek boyutta basılmalıdır; yazıcı sayfaya sığdırma yaparsa fiziksel ölçek değişir. Yuvarlanmış piksel boyutları yaklaşık 297,01×209,97 mm verir.

Deliklerin kesit bölgesindeki iki sınır çizgisi korunur, sadece tarama kaldırılır. Delik eksenleri eklenir ve tüm eksenlerin kaynak rengi siyahtır (ince çizgiler ekranda kenar yumuşatma nedeniyle açık görünebilir). İzometrikte kapalı ön yüzden görünmemesi gereken iç çeper halkası kaldırıldı. Köşe yarıçapları hâlâ yaklaşık; radyuslu izometrik yüzey henüz uygulanmadı. Önceki ölçek yok açıklamaları eski çıktılar içindir.

### Yüksek çözünürlüklü kaynak ve R8 (v3)

`highres-reference.jpg` (7016×4961) yeni kaynak; `highres-analysis.json` bu dosyanın gerçek API analizidir. Model R8, 3 ve 33,5 sabitlerini okudu, veri kontrolü geçti. Kaynak çözünürlüğü pafta koordinatlarına dönüştürülür; bu ikinci kaynak için antet sınırları elle yeniden kalibre edildi. A4 çıktı hâlâ 3508×2480/300 DPI.

`plate-sheet.json` içindeki OuterBendRadiusMm=8 dış radyustur. Kesitte gerçek çeyrek daire yayları kullanılır. Aynı 3 mm cidar kabulüyle iç yarıçap 5 mm alınır; bu kabulün kullanıcı önizlemesiyle doğrulanması gerekir. İzometrik R8 yüzey geçişi 48 örnekleme bandıyla gösterilir; tam CAD yüzey/görünürlük motoru değildir. Ön görünüşteki iç kontur dış radyusun teğet sınırına göre konumlanır.

Ölçü fontu Liberation Sans Regular; kaynakta kesin font metadatası olmadığından birebir font iddiası yoktur. Nominal metin 12,5 pafta koordinat birimi, asimetrik toleranslar 8,5 birimdir. Üst delik liderindeki yazının açısı lider yönüne uyarlandı. Antetteki değişken hücrelerin yazısı da aynı ailede yeniden çizilir. Nihai görsel uyum insan kontrolüne tabidir.

### Yarı çözünürlüklü grup denemesi (v4)

Güncel çıktı 1754×1240, 150 DPI; A4 fiziksel boyut ve gerçek baskı ölçekleri korunur. Önceki 3508×2480/300 DPI bilgileri v2–v3 arşiv çıktıları içindir. `output/group-v4` altında altı Excel satırı üretildi; GitHub'da `previews/group-v4` altında JPEG'ler ve yalnızca bu altı JPEG'i içeren ZIP bulunur. Kaynak grup sabitleri 3 mm, 33,5 mm, dış R8 olarak uygulanır. 259 ve 286 mm çaplı ürünlerde standart ölçek seçimi 1:5, diğerlerinde 1:2; izometrik 1:5. Bu denemede yeni API çağrısı yapılmadı; mevcut doğrulanmış analiz ve Excel kullanıldı.

v5: ana görünüş ve kesit için bu grubun altı ürününde ortak 1:2,5 ölçek kullanıldı. Delik lider yazıları çizgi açısına paralel ve metin genişliğine göre ortalı; düşey ölçüler orta noktaya hizalı. Kesitte arka kenarın görünür sınırı eklendi. Bu, aileye özel adaptördür; bileşenli kaynaklı parçalar henüz desteklenmez.

### Altı ürün kontrolü (v6)

Ölçek ve lider yerleşim kuralları `LayoutPolicy.cs` içine ayrıldı. Bu sınıf parça türü veya A–E anlamı bilmez; geometrik adaptörün verdiği genişlik/yükseklik zarfını ve ayrılan alanı kullanır. Referans açıklık, tercih edilen ölçek ve küçük parça oranı `plate-sheet.json / ScalePolicy` içindedir. Bu grup: referans 286 mm, tercih 1:2,5; referansın %70'inden küçük zarf için daha büyük görünüş tercih edilir. 136 mm ürün 1:2, diğer beşi 1:2,5. Tam bir otomatik grup kümeleme/çakışma çözücüsü değildir.

Lider yazıları dış uçta, çizgiye paralel ve uç çevresinde ortalıdır. Sabit derinlik yazısı artık ayarlardaki değer ve ölçü çizgisinin orta noktasını kullanır. Ana kaynak rasterinin küçültülmesine filtre eklendi; üst numara satırını silen temizleme alanı daraltıldı. Ölçek metni antet hücresine sığacak şekilde boyutlanır.

Altı çıktı birlikte görsel olarak incelendi; büyük/küçük örnekler tam çözünürlükte ayrıca incelendi. 150 DPI ve boyut/ölçek metadatası altı dosyada kontrol edildi. `dotnet run --project checks/LayoutPolicyChecks.csproj` ile küçük/büyük ve dairesel olmayan zarf, iki eksende sığma, hatalı girdi ve lider yerleşimi kontrolleri çalışır.

Sınırlamalar: `SheetPreview` halen tek parçalı dairesel aile ve iki kaynak paftaya elle uyarlanmış çizim adaptörüdür. Kaynaklı manşon/rekor bileşen grafı, genel çakışma çözümü, otomatik geometrik anlam doğrulaması ve tam CAD görünürlük hesabı uygulanmadı. Kesin üretim geometrisi onayı verilmedi. Yeni aile eklerken önce farklı bir gerçek örnekle ortak yerleşim katmanı sınanmalıdır.

### İkinci grup — isteğe bağlı üçüncü delik (deneysel)

`preview-group2 <xlsx> <product> <jpeg> <output>` ikinci grubun kontrol önizlemesini üretir. E/F birlikte boşsa delik yoktur; E dolu ve F=0 ise merkezde vardır. Tek taraflı eksik E/F reddedilir. G alt konumu, B-G üst konumu belirler. F=0 ve G=B/2 yardımcı konum ölçülerini gizler, fiziksel delikleri gizlemez. H parça numarasıdır. Birinci grubun düzlemsellik işareti bu gruba taşınmaz. Kademeli kesit izi üçüncü deliğin yatay ofsetini kapsar. Derinlik bu grupta 33 mm'dir (önceki 33,5 değil).

Sabitlerin ve harf eşleşmelerinin bu ikinci adaptörde açıkça kodlanması geçici bir teknik denemedir; model çıktısından genel geometri üretimi tamamlanmış değildir. Kesit/izometrik yine örneklemeli ve yaklaşık yüzeylidir. Geometrik çarpışma ve tüm tolerans kombinasyonları henüz denetlenmiyor. Dört çıktıda boyut/DPI kontrolü, görsel inceleme ve model koordinatlarının satır bazında karşılaştırması yapıldı. Yeni API çağrısı çizim aşamasında yapılmadı.

### Arial font gereksinimi

Yeni çizimlerde yalnızca gerçek Arial Regular kabul edilir. Sisteme Arial kurulmuşsa otomatik bulunur; aksi halde DRAWING_FONT_PATH lisanslı arial.ttf dosyasını göstermelidir. Anahtar/gizli değer değildir. Windows'ta genellikle C:\Windows\Fonts\arial.ttf bulunur. Font dosyası repoya eklenmez. Arial yoksa veya farklı aile/bold/italic verilirse açık hata alınır; sessiz Liberation Sans geçişi yapılmaz. Eski yayımlanmış JPEG'ler önceki fontla kalır. Bulut ortamında Arial henüz kurulu değil; gerçek Arial ile yeniden render henüz doğrulanmadı. Derleme ve eksik font halinde durma kontrolü geçti.

Arial dosyası kullanıcı ZIP'inden /workspace/fonts/arial/arial.ttf konumuna çıkarıldı; repoya eklenmedi. DRAWING_FONT_PATH önceliklidir, bulut dosyası varsayılan konumda da bulunabilir. Gerçek Arial ile 11-30-381 önizlemesi başarıyla üretildi. Font ailesi taslaktan analiz edilmez. Tırnaklı harflerden otomatik yazı boyutu çıkarma henüz uygulanmadı; mevcut 12,5 pafta-birimi ölçü yazısı boyutu kullanılmaya devam ediyor. Bu özellik font seçimi değil, görüntüdeki harf yüksekliği/yönü ölçümü olarak ayrıca geliştirilecek.

### Yeşil ölçüler, kaynak DPI ve parantezli tolerans denemesi

`tools/analyze_updated_group.py` tüm Excel satırları ve güncel JPEG ile gerçek API çağrısını yapar; raw-response.json ve model-plan.json saklanır. REVIEW_RETRY=1 aritmetik uyuşmazlık geri bildirimiyle ayrı yanıt/plan kaydeder. Bu denemede geri bildirim metni asistan tarafından hazırlandı; uçtan uca özerk analiz/düzeltme döngüsü değildir.

`preview-group2` son isteğe bağlı argüman olarak model planını alır. Planın her hedef satırdaki delik konumlarını, çaplarını ve sayısını mevcut adaptörün Excel ilişkileriyle karşılaştırır; uyumsuzsa resim üretmez. Sabitler ve gizleme bayrakları planın renderSettings alanından alınır. Yeşil R8/3/33 bu örnekte geometride kullanılır, ölçü okları/yazıları/liderleri çizilmez. Bu üç bayrak genel renk-semantik motoru değildir; diğer ailelerde yeni geometrik tarif gereklidir.

DPI artık JPEG JFIF kaydından okunur; kayıtsız veya eşit olmayan X/Y DPI için açık hata alınır (EXIF-only yoğunluk henüz desteklenmez). Piksel boyutu 1754×1240 kalır. Kaynak 300 DPI olduğunda fiziksel çıktı 148,505×104,987 mm'dir, A4 değildir; antette ÖZEL yazılır. Baskı ölçeği buna göre hesaplanır, izometrik alan da bağımsız sığma kontrolünden geçer. Tolerans sapmaları parantez içinde, asimetrikler üst/alt düzenindedir. Bu gösterim kullanıcı tercihidir; tüm teknik resim standartları için genel uygunluk iddiası yoktur.

Bu denemede insan müdahaleleri: renk kuralını ve DPI/tolerans davranışını kodlamak; modelin yanlış konumu için doğrulama geri bildirimini hazırlayıp çağrıyı başlatmak; F uzatma çizgisiyle C lider yazısının çakışmasını görsel incelemede fark edip C liderini sağa almak. Modelden açık sorular geldi, kullanıcıdan yeni geometrik bilgi istenmedi; ikinci çağrıda sorular boşaldı. İlk model konumu reddedildi; değerler sessizce değiştirilmedi.

80+ satır öncesi güncel kod değerlendirmesi: docs/review-2026-10-28.md. Ölçü yazıları varsayılan %10 büyütüldü (DimensionTextScale=1,10). Mevcut JPEG'ler yeniden üretilmedi; yeni veriyle görsel kontrol gerekiyor. Bu inceleme sırasında API çağrısı yapılmadı.

## Tek komutla ikinci grup akışı

```bash
dotnet run --project src/DrawingTool.csproj -- run-group2 samples/group2/taslak2.xlsx samples/group2-updated/taslak2guncel.jpg output/new-run
```

Çıktı klasörü boş olmalıdır. Varsayılan olarak yalnızca ilk önizlemeyi üretir. Açık toplu üretim talebinde sonuna `--all` eklenir. Komut yeni xlsx/JPEG yollarını alır; eski deney betiğindeki sabit ürün hata mesajını kullanmaz. Her satırın hücrelerini, isteğe bağlı delik varlığını, pozitif çapları, delik çakışmalarını ve dış/büküm bölgesi sınırını kontrol eder. Modelden satır koordinatları yerine bir kez sembolik ilişki ister. En fazla sekiz yapısal/boyut örneği gönderir, toplam iki API çağrısından sonra durur. JSON, formül ve açık soru kontrolü başarısızsa çizim üretmez. Ölçü ihlallerine ilişkin geri bildirim satırlardan otomatik hesaplanır. Açık soruların model tarafından kaldırılması, bağımsız doğruluk kanıtı değildir; desteklenen formül sözleşmesi ve geometrik kontroller ayrıca uygulanır.

Kaynak/Excel SHA256, API cevapları, kabul edilmiş plan, maliyet ve satır sonuçları çıktı klasöründe kaydedilir. `run-report.json` HumanApproved=false ile kalır. Desteklenen profil bilerek ikinci gruptur; yeni aileyi zorla kabul etmez. İç halka bu karşılaştırma akışında açıkça ShowInnerRimLine=true ayarlanır; diğer çizim yollarında varsayılan false kalır. Bu ayar tam görünürlük düzeltmesi değildir.

Çalışma notları ve karşılaştırma JPEG'leri `previews/group2-rim-restored` klasöründe. İlk başarısız deneme ve son başarılı çalışma raporları bulutta ayrı klasörlerde korunmuştur. Test komutu: `dotnet run --project checks/LayoutPolicyChecks.csproj` (21 çevrimdışı kontrol). Yeni model/HTTP hataları sınırlı çağrıyla durur; para cinsinden sert bir sağlayıcı bütçe limiti uygulanmış değildir. Genel yazı çakışma çözümü, dinamik pafta bölgesi tanıma, yeni aile geometrileri ve tam CAD görünürlük hesabı bu değişikliğin kapsamında tamamlanmadı.

## Optional OCCT trial

See `experiments/occt/README.md`. `occt-demo <parameters.json> <empty-output-folder>` is an isolated C#-to-local-OCCT experiment. Existing sheet generation does not use it and remains unchanged. The first validated example generates real analytic STEP geometry plus an offscreen rendered JPEG without API calls. OCCT can be discarded without changing existing data/commands. Windows packaging and integration into technical sheets are still pending.

## Aktif OCCT izometrik entegrasyonu

Sağ üst görünüşün eski el çizimi (konveks zarf, halka/bant boyama) kodu ve ilk prototipin eski `Draw`/`preview`/`batch` yolu kaldırıldı. Ön görünüş/kesit ve ölçüler hâlâ C#/Skia ile oluşturulur. `run-group2` artık doğrulanmış API sabitleri/ilişkileri ve JPEG'den tahmin edilen kamera ile her satır için OCCT oluşturur; sonuç PNG'sini paftaya ekler. Sessiz eski motor dönüşü yoktur. OCCT/Python yoksa API çağrısından önce durur. Linux süreçte LIBGL_ALWAYS_SOFTWARE=1 ile CPU görüntüleme seçilir. Native worker'a OpenRouter değişkenleri aktarılmaz.

API kamera alanı: direction (hedef merkezden kameraya), up, projection=orthographic, confidence=high/medium. Kamera matrisi ve geometri isteği `.cad-request.json` dosyasına, STEP/STL ve BRep/hacim/STEP doğrulamaları `.cad/result.json` altına kaydedilir. Kamera düşük güvenli veya açık soru varsa plan kabul edilmez. Paftanın sağ üst referansı bilinen profil alanından otomatik kırpılarak modele tam JPEG ile birlikte gönderilir. Bu kırpma elle kalibre edilmiş profil alanıdır; genel otomatik pafta bölgesi bulma değildir. Kamera API tahminidir; görüntü işleme ile piksel düzeyinde kamera kalibrasyonu uygulanmadı.

İzometrik görünüş paftadaki kutuya oranı korunarak yerleştirilir ve **ölçeksiz** olarak etiketlenir; ana görünüşün fiziksel baskı ölçeği ayrıdır. CAD çıktısında görünürlük mesh derinlik testiyle, yüzeyler gerçek analitik modelin 0,08 mm ağından elde edilir. Örnek model, OCCT tarafından üretilebilse de kullanıcı tarafından geometri/açı onayı verilmiş sayılmaz.

`preview-group2` artık kabul edilmiş yeni planı ve `accepted-plan.binding.json` kaynak özeti dosyasını zorunlu ister. Eski kamera içermeyen planlar reddedilir. Şimdilik toplu otomasyon ikinci A–H grubunun desteklenen sözleşmesiyle sınırlıdır; genelleştirilmiş her-parça CAD çözümü değildir. Birinci grubun `preview-sheet` yolu da açık kamera verisi gerektirir; eski planlarla sessiz varsayılan açı kullanılmaz. Hazır Windows paketi henüz yoktur.

Kamera güveni için yeni ayrım: geometrik belirsizlik her zaman durdurur. Yalnızca kamerayla ilgili düşük güven/soru, tek önizlemede açık uyarıyla kabul edilebilir; toplu `--all` üretimde kabul edilmez. Önizleme kullanıcı onayı değildir. `resume-group2-preview <xlsx> <jpeg> <saved-run-folder> <empty-output>` başarısız çalışmadaki son tamamlanmış API yanıtını, aynı kaynakların SHA256 bağını ve tüm geometri kontrollerini yeniden doğrular; yeni API çağrısı yapmadan sadece ilk ürünü üretir. Plan değerleri elle düzeltilmez. İlk düşük güvenli kamera tahmini bu yolla mevcut kaynaktan üretilmiştir. Tam piksel-kamera eşleştirmesi hâlâ uygulanmadı.

API uyarılarında yalnızca açıkça kamera yönü/tilt ile ilgili ve delik/ölçü/radyus/konum terimleri içermeyen sorular önizleme uyarısına düşürülür; diğerleri engelleyicidir. Bu muhafazakâr sınıflandırma bilinmeyen ifadelerde durabilir. Kamera sorusunu kaldırmak, kamera doğruluğunun bağımsız kanıtı değildir.

## OCCT tabanlı tam görünüş yolu (güncel)

```bash
dotnet run --project src/DrawingTool.csproj -- run-cad samples/taslak1.xlsx samples/highres-reference.jpg 11-30-121 output/new-cad-run
```

Bu komut gerçek API çağrısı yapar. Yeni `schemaVersion=1` CAD planı, Excel sütununa bağlı ifadelerle parametreler/delikler, kamera, kesit düzlemi, ölçü bağlantıları, sabit ve geometrik tolerans gösterimlerini tarif eder. Kod sadece sınırlı ifadeleri değerlendirir; modelden kod çalıştırmaz. Geometriye ait açık sorular reddedilir; yaklaşık kamera açısı kabul edilir. En çok iki API denemesi vardır. Yerel çizim hatası API yeniden denemesi başlatmaz.

Eski SkiaSharp paketleri, `SheetPreview` ve eski görünüş/ölçülendirme adaptörleri kaldırıldı. `run-group2`, `preview-group2`, eski `preview-sheet` ve eski analiz komutları bu yeni yolda desteklenmez. Tarihsel notlar eski sürümlere aittir. Excel/ölçü doğrulama yardımcıları ve testleri korunur. Güncel komutlar `run-cad`, `render-cad-plan`, `occt-demo`, `validate-analysis`.

- Ön görünüş: OCCT HLRBRep görünür ve seçilmiş teğet kenarları.
- Kesit: gerçek katının BRepAlgoAPI_Section X=0 düzlemi ile kesişimi; tarama, OCCT kesitinin kapalı telleriyle sınırlanır. Arka görünür kenarlar, yarısı çıkarılmış katının HLR sonucundan gelir.
- İzometrik: aynı katı modelin VTK CPU görüntüsü.
- Ölçülendirme: OCCT geometri koordinatlarına bağlı yeni SVG katmanı; değerler Excel'den alınır, ilgili model çapı/merkez uzaklığına karşı doğrulanır. Arial glyph'leri fontTools ile vektör yola çevrilir, CairoSVG ile JPEG'e aktarılır. OCCT'nin otomatik tamamlanmış teknik resim/ölçü yerleşimi oluşturduğu iddia edilmez.

`render-cad-plan <xlsx> <jpeg> <product> <saved-run> <new-output>` kaynak SHA256 bağını doğrulayarak kaydedilmiş planı tekrar çizer; API çağırmaz. Sayısal plan elle değiştirilmez. İlk 11-30-121 denemesinde JSON veri ömrü hatası bu yolla giderilip model yanıtı yeniden kullanıldı; buna yönelik regresyon testi eklendi.

Sınırlar: yeni tam görünüş yolu yalnızca yuvarlatılmış kesiti döndürülmüş dairesel pleyti, tabandaki delikleri ve gerçek X=0 düzlem kesitini destekler. Kademeli kesit, kaynaklı montajlar, genel ölçü çakışma çözümü ve otomatik pafta bölgesi tanıma tamamlanmadı. 7016×4961 kaynak yerleşimi elle kalibre edilmiş profildir. Yazı boyutu henüz görüntüden otomatik ölçülmez. Yeni API planı bunlar dışındaki geometriyi ifade ederse durmalıdır. Kamera bir tahmindir; piksel düzeyinde eşleşme garantisi yoktur. Windows dağıtımı ve Cairo/OCCT yerel bağımlılıkları henüz paketlenmedi.

## Soru sormayan grup raporu (şema v2)

`run-cad-group <xlsx> <jpeg> <empty-output>` Excel'i bir defa okur; sekiz satıra kadar tamamını, büyük dosyalarda sınırlı örnekleri tek API çağrısında gönderir. Henüz v2 çizim yürütücüsü değildir: desteklenmeyen kesit/koşullu özelliklerde görüntü üretmez, RAPOR.md ve run-report.json döndürür. Raporda input, software, model, protocol ve camera sınıfları ayrıdır. Origin=model yorumları kendi başına kesin girdi kusuru değildir. Model bir soru döndürürse protokol sorunu olarak raporlanır; hiçbir request-user-input veya sohbet bekleme adımı yoktur. Girdinin yanlışlığı ile yazılım desteğinin eksikliği karıştırılmamalıdır.

`review-cad-group <xlsx> <jpeg> <saved-run> <new-output>` kaynak özetini kontrol ederek aynı yanıtı tekrar yerel doğrular; yeni API çağrısı yapmaz. Engellenmiş çalışmanın çıkış kodu 2, beklenmeyen hata 1; başarılı analiz 0'dır. Mevcut örnekte beklenen durum blocked-with-report, yeni JPEG sayısı 0'dır. Son çalışma notları previews/group2-diagnostic/NOTLAR.md altında. Bu aşama bağımsız rapor üretimidir; henüz bu yeni şemada otomatik çizim başarısı iddiası değildir. V1 run-cad de belirsizliklerde issues raporuna geçmiştir.

## Excel'in API öncesinde ayrıştırılması

`run-cad-group` ve `run-cad`, ölçü hücrelerini artık ham metin olarak göndermez. Ortak `ExcelModelInput` ayrıştırıcısı nominal mm değerini, çap sembolünü ve işaretli üst/alt tolerans sapmalarını ayırır. Boş hücre `state=blank`, gerçek sıfır `state=number, nominalMm=0, isZero=true`, parça kodu `state=text` olur. Üçüncü deliğin varlığı gibi geometrik anlamlar JPEG/plan eşlemesinin sorumluluğundadır; ayrıştırıcı harflere sabit anlam yüklemez. Geometri yalnızca nominali kullanır; toleranslar gösterim verisidir. Özgün hücre metinleri yerelde korunur.

Desteklenen biçimler: `Ø227±1`, `157,5±0,5`, `Ø21 (+0,1|-0,0)`, toleranssız pozitif sayı ve sıfır. Noktalı ondalık ve `⌀` da kabul edilir. Desteklenmeyen ölçü gösterimi sessizce dönüştürülmez. Uzun sayısal tanımlayıcılar ve başka tolerans söz dizimleri için açık tür desteği ileride gerekebilir. Bütün satırlar yerelde ayrıştırılır; büyük tablolarda API örneklemesi hâlâ en fazla sekiz satırdır.

Çıktıdaki `normalized-excel.json` tüm ayrıştırılmış satırları, `model-input.json` gerçekten gönderilen örnekleri, `request-prompt.txt` metin talimatını saklar; bu dosyalarda API anahtarı yoktur ancak ürün verisi bulunur. Sıfır/boş ayrımı delik varlığı veya ölçünün görünürlüğü kararını tek başına vermez. HTTP 401/403 grup raporunda configuration/API_AUTHENTICATION olarak işaretlenir; bu durumda model değerlendirmesi alınmış sayılmaz.

## Koşullu paralel kademeli kesit ve v2 yürütme

`run-cad-group` artık geçerli v2 planını yerel OCCT yürütücüsünde bütün satırlara uygular. Model kesiti `section:{mode:"through-features",featureIds:[...]}` ile tanımlar. Yazılım mevcut delikleri seçer: aynı X=0 düzlemindeki eksenler düz kesit, kaçık ara delik ekseni ise paralel kademeli kesit oluşturur. Excel/JPEG anlamları modele aittir; sabit A–H geometrik konum eşlemesi yürütücüye gömülmez. `hideWhen=half:B` şema kuralı hâlâ B sütununa bağlıdır; her türlü görünürlük bağıntısı henüz desteklenmez.

Yerel motor Y boyunca ayrık bantları OCCT ile keser, kesit yüzlerini ortak düzleme taşır ve birleştirir. Aynı düzlemdeki yüzler sadeleştirilerek yapay kademe çizgileri kaldırılır. Y/depth korunur; izometrik ve ön görünüş aynı değişmeyen katıdan gelir. Kesit geometrisi başka bir parça değildir. Kesit başlangıç/bitiş hedefleri ana X=0 düzleminde olmalı; hedef deliklerin Y aralıkları arasında güvenli geçiş bulunmalıdır. Döndürülmüş, eğik veya genel serbest kesit yolları desteklenmez. Gerideki çeper görünür çizgileri ana düzlemin yarım-katı HLR hesabından alınır; genel kademeli kesit arka-kenar görünürlüğü çözümü değildir.

Boş isteğe bağlı delik kaldırılır, bağlı ölçüler çizilmez; sıfır konumundaki delik kalır. Gizleme yalnızca ölçünün görünürlüğüne uygulanır. Satırlar yürütmeden önce çözülür; native geometri doğrulaması her satırda ayrıca yapılır. Başarısızlık rapora gider, model planı asistan tarafından tamamlanmaz. Çıktılar insan incelemesi bekler.

Güncel grup yolu en fazla iki API çağrısı yapar; ikinci çağrı yalnızca yerel doğrulama hatalarını modelin kendisinin incelemesi içindir. Kullanıcıya soru sormaz. `render-cad-group <xlsx> <jpeg> <saved-run> <new-output>` kaynak SHA256 özetini doğrulayıp kayıtlı planı yeni API çağrısı olmadan yürütür. Bu ailede modelin negatif Z kamera bileşeni pozitif tarafa yansıtılır; kaynak kamera planda korunur, çözülen kamerada `frontFacePolicyAdjusted` bulunur. Geometri etkilenmez; görsel açı yaklaşımıdır. Sonuçlar previews/group2-conditional-section/NOTLAR.md altında.

## Tek çıktı kimliği ve modelin seçtiği kamera

Yeni çalışma sözleşmesinde Excel'in fiziksel A sütunu `output jpeg name` başlığını taşır (eski `jpeg file name` başlığı da kabul edilir). Değer, uzantısız çıktı kimliğidir; antetteki parça numarası da buradan gelir. Çizimdeki `'A'` ölçüsü ise A başlıklı ölçü sütununa bağlıdır; Excel'deki fiziksel sütun harfiyle karıştırılmaz. Antetteki `'H'` yer tutucusu için H hücresinden kimlik okunmaz. Eski dosyalarda çıktı kimliğini aynen tekrarlayan hücreler modelin ölçü yükünden çıkarılır. Kalan hücreler ölçü veya boş hücre olmalıdır; desteklenmeyen metinler raporlanır. H başlıklı sayısal bir ölçü sütunu varsa ölçü olarak korunur, kimlik sayılmaz.

İzometrik yönü artık model seçer; negatif Z bileşenini pozitife yansıtma kaldırılmıştır. Sayısal kamera geçerliliği, sıfır olmayan vektörler, yukarı-yön çakışması ve ortografik projeksiyon denetlenir. Bu değişiklik eski yayımlanmış JPEG'leri değiştirmez. Genel geometri desteği eklemez: mevcut katı oluşturucu hâlâ döndürülmüş dairesel pleyt ailesiyle sınırlıdır. Yeni flanş geometrisi için model tanısa bile yerel özellik desteği ayrıca gerekir.

## Güncel sözleşme: şema v3, tek API çağrısı

Bu bölüm önceki v2/iki-deneme notlarının yerini alır. `run-cad-group` artık tek API çağrısında `geometry`, `annotations`, `section` ve `camera` bölümlerini ister. `geometry.holes[].position` her koordinatı ana eksene veya başka bir özelliğe göre işaretli sütun mesafesiyle tanımlar. Koordinatlar yerelde bağımlılık çözümüyle hesaplanır; döngüler ve olmayan özellik bağımlılıkları reddedilir. Modelden cebirsel formül alınmaz. `annotations.dimensions[].hideIf` ayrı gösterim koşuludur: never, zero veya equalsScaledColumn. Geometriyi değiştirmez. B/G harfleri çözücüye gömülü değildir. Her sayısal Excel sütununun bir ölçü eşleşmesi olması kontrol edilir. Eski v2 kaydedilmiş planlar yeniden çizilebilir; yeni analiz v3 üretir. V1 tek-ürün yolu da artık otomatik ikinci çağrı yapmaz.

Kesit amacı, etiketi ve hedef özellikleri modele aittir. Satırda olmayan hedefler kaldırılır; hedeflerin konumları aynı düzlemdeyse kademeler birleşir. Native motor yalnızca Y boyunca paralel kesit bantlarını, ana düzlemdeki uç hedefleri ve hedef Y aralıklarında güvenli geçişleri destekler. Bu, bütün kesit türlerini destekleyen bir motor değildir. Her bandın görünür arka kenarları ayrı HLR ile çıkarılır; yalnızca yapay bant sınır kenarları elenir. Delik üst/alt görünür kenarlarının korunması regresyon testiyle kontrol edilir. Kesit etiketi plandan alınabilir. Modelin kesit hedeflerini resimden doğru okuduğu bağımsız olarak garanti edilmez.

Bu denemede kullanıcı, model hatasını bir defaya mahsus asistanın düzeltmesine izin verdi. Özgün API planı korunarak ayrı assisted-plan oluşturuldu. Runtime'a kullanıcıya özel B/G düzeltmesi gömülmedi. Bu istisna otomatik düzeltme modu değildir. Kayıtlı kaynakta AssistantAnswersUsed=true varsa yeniden çizim raporunda korunur. Yeni normal çalışma tek çağrıdan sonra başarısız planı raporla durdurur. Ayrıntılar previews/group2-v3/NOTLAR.md içinde.

## Renk sözleşmesi ve çizimsiz analiz

`analyze-cad-group <xlsx> <jpeg> <empty-output>` yeni grup analiziyle aynı tek API çağrısını yapar; sonuç geçerli olsa da OCCT yürütücüsünü çağırmaz, JPEG çizimi üretmez. Girdi ön işleme görünümü bir ürün çizimi değildir. Yeni renk yolu `run-cad-group` ve `analyze-cad-group` için geçerlidir; tarihsel v1 `run-cad` aynı çift-görüntü protokolüne geçirilmedi.

Yerel `tools/color_views.py`, kırmızı baskın pikselleri beyaz yaparak geometri görünümünü oluşturur; özgün JPEG değişmez. Siyah/yeşil korunur. Model görüntü 1'den geometri/kesit, görüntü 2'den renk ve gösterim kurallarını okur. Geometri Excel yükü nominal/sıfır/boş/çap bilgisi içerir; toleranslar yalnızca ayrı annotationInput yükündedir. Tek çağrıda iki görünüm sunmak, birbirinden bağımsız iki analiz değildir: model her ikisini görebilir. Renk eşiği soluk kırmızı kalıntılarını kaçırabilir; renk sözleşmesi hâlâ model yorumuna bağlıdır.

İstenen ek çıktı `colorPolicyVersion:1`, `measurementSources` (sütun, siyah/yeşil, eksen, ölçü uçları, kanıt), sabit ölçülerde `sourceColor` alanlarıdır. Yeşil görünürlük ve kırmızı geometri kaynağı tutarsızlıkları denetlenir. Bu kontroller modelin kendi kaynak iddialarına dayanır; bağımsız görüntü doğrulaması değildir. Geometrik ilişkiler, ölçü koşulları, isteğe bağlı varlık ve kesit hedefleri ayrı kalır. Tolerans aralıklarının çakışması gizleme/eşitlik koşulunun sağlandığı anlamına gelmez; karşılaştırmalar nominalde yapılır.

Son renk denemesi: previews/group2-color-analysis/NOTLAR.md. Modelin bildirdiği ölçü uçları ile ölçülendirme türünün gerektirdiği uçlar da karşılaştırılır; sayısal tesadüfler doğru eşleşme sayılmaz. Bu, kaynak JPEG'deki gerçek ölçü uçlarını bağımsız algılayan bir yöntem değildir.

## Açık referans sistemi: şema v4

Yeni grup analizi şema v4 ister. Model `coordinateFrame` içinde referans görünüşü (tam JPEG'de normalize bbox), orijini (tam JPEG'de normalize nokta, geometrik özellik ve kanıt), eksenleri ve gövdenin bu referanstaki ankrajını (`bodyAnchor`) tanımlar. Kullanıcı koordinat hazırlamaz. Görsel nokta milimetreye veya üretim ölçüsüne çevrilmez; kanıt/inceleme içindir. Model noktalarının gerçek eksen kesişimi olduğu bağımsız görüntü analiziyle doğrulanmış sayılmaz.

Parça özellikleri ve gövde ankrajı aynı ilişkilerle çözülür. Yerel gövde oluşturucu kendi merkezini sıfırda kullandığından, tüm delik merkezlerinden gövde ankrajı çıkarılır. Kaynak orijin de aynı dönüşümle taşınır; ölçü hesapları bu taşınmış orijini kullanır. Yalnız gövdeyi veya yalnız delikleri kaydırmak yasaktır. Kamera doğrultusu bu ortak ötelemeden etkilenmez. Gövde ana ekseni–ön yüz kesişimi orijin olarak beyan edilmişse gövde ankrajı sıfır olmalıdır. Var olmayan/opsiyonel özelliğe bağlı orijin, döngü ve geçersiz görsel alan reddedilir.

Bu sürümde yalnızca X sağ/Y yukarı/Z izleyiciye doğru bazı desteklenir; başka baz sessizce yansıtılmaz. Diğer bazların dönüşümü yazılana kadar raporlanır. Orijin referansının genel tanımı, bütün parça türleri için geometri oluşturucu eklendiği anlamına gelmez. V3 geçmiş planlar geriye uyumlu okunur. Analiz komutu çizim üretmez; orijin sözleşmesi değişikliğini görmek için diğer API ayarları (low reasoning ve çift tam görüntü) değiştirilmedi.

Şema v4'ün ilk gerçek API denemesi ve değiştirilmemiş planı: previews/group2-reference-frame/NOTLAR.md. Dört satırın geometri/ölçü bağlantıları yerel doğrulamadan geçti; çizim üretilmedi. Bu sonuç bütün parça aileleri için garanti değildir.

## Ölçü yazısı çakışma kontrolü ve kısa prompt

Talimatlar CadAnalysisPrompt içinde birleştirilmiştir; iki Excel veri bölümü korunmuştur. Kaynak şeması ve gerçek hata raporları korunurken normal açıklamalar kısaltılır. Yerel yazı yerleşimi gerçek Arial glyph sınırlarını, asimetrik tolerans genişliğini, dönüş açısını ve 3 birim boşluğu kullanır. Önce bütün çizgi/sabit metin engelleri kaydedilir, sonra ölçü etiketleri sonlu adaylardan seçilir; temiz aday yoksa raporla durur. Bu bir genel pafta/ lider kesişim optimizasyonu değildir. Tests: `python experiments/occt/test_label_layout.py`. Son çalışma previews/group2-compact-layout/NOTLAR.md içinde; API cache ve gerçek maliyet kullanım kayıtlarından karşılaştırılmıştır.

## Yeşil gösterimin yerel otoritesi

Yeni grup yolunda (`CadPlanV3`, v3/v4) `ColorVisibilityPolicy` modelin `measurementSources.color` ve sabit ölçülerin `sourceColor` kayıtlarını kullanır. Yeşil dimension/fixedAnnotation için etkin visible=false kodda hesaplanır; kaynak model yanıtı ve nominal geometri değişmez. Worker visible=false için yazı, ok ve uzatma çizgilerini üretmez. Modelin visible=true demesi artık GREEN_* hatasıyla üretimi durdurmaz: COLOR_VISIBILITY_APPLIED uyarısı, yerel kuralın uygulandığını kaydeder. Siyah ölçülerin kendi görünürlük/gizleme koşulları korunur. Kaynak rengi eksik/geçersiz ya da uç eşleşmesi tutarsızsa mevcut kontroller devam eder.

Normal grup promptundan yeşilin gösterimini kapatma görevi çıkarıldı; model yalnızca kaynak rengini tanır ve renk dışındaki gösterim koşullarını tarif eder. Görsel renk algısını tamamen kaldırmak doğru değildir: yerel kod hangi ölçünün yeşil olduğunu bu kayıttan öğrenir. Bu işlem bağımsız renk-algılama doğrulaması değildir. Tarihsel v1 tek-ürün yolu bu yeni politikanın kapsamında değildir.

Kayıtlı veri3 yanıtı yerelde review-cad-group ile yeniden değerlendirildi: 82 satırdaki ilişki kontrollerinde bloklama kalmadı. Bu doğrulama yeni API veya çizim üretmez; 82 native çizimin başarı garantisi değildir. 75 C# kontrolü geçti. Regresyonlar yeşil sabit/ölçü görünürlüğünü, ham yanıt ve geometrinin korunmasını, siyah ölçülerin etkilenmemesini kapsar.

## Teknik resim jargonuyla sade yorumlama denemesi

`analyze-cad-group <xlsx> <jpeg> <empty-output> --technical-jargon` genel yorumlama talimatlı taslak promptunu seçer. Normal analiz/üretim son başarılı üretim talimatlarını kullanmaya devam eder. Sade taslak, kırmızı notsuz dört satır analizinde üst delikleri simetrik kabul ederek asimetrik 92'de 8 mm hata verdi; bu nedenle varsayılan yapılmadı. Geçersiz sonuç çizilmedi ve elle tamamlanmadı. Deneme kaydı previews/group2-jargon-no-notes/NOTLAR.md altında.
