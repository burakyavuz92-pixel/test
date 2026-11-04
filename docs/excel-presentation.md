# Excel: geometri ve gösterim

Her ölçü için ana sütun (`A`, `B` vb.) geometri değeridir. `Ø10,5` çap bilgisiyle 10,5 mm olarak korunur. Metnin ifade ettiği standart üzerinden nominal değer değiştirilmez.

| Sütun | Anlam | Örnek |
|---|---|---|
| B | Geometri | Ø10,5 |
| B_METIN | İsteğe bağlı, nominal gösterimin yerine aynen yazılacak metin | 1/4''-18 NPTF |
| B_TOLUST | İsteğe bağlı üst sapma | 0 |
| B_TOLALT | İsteğe bağlı alt sapma büyüklüğü | 0,1 |

Bu örnekte geometri Ø10,5 kalır, çizim metni `1/4''-18 NPTF (+0/-0,1)` olur. `_METIN` boşsa standart sayısal gösterim kullanılır. Metne otomatik Ø veya nominal değer eklenmez; gerekiyorsa kullanıcı metne dahil eder. Yazılım metni diş olarak sınıflandırmaz. Metin ve tolerans, geometri API tablosuna girmez. Ölçünün taslaktaki köşeli parantez etiketi ve geometrik referansı aynı ana sütun üzerinden bağlanır.

Alt tolerans pozitif büyüklük veya negatif sapma olarak girilebilir; `0,1` ve `-0,1` ikisi de −0,1 olur. Üst tolerans yazıldığı işaretle alınır. Boş kalan tolerans tarafı, diğer taraf doluysa sıfırdır. İki taraf boşsa tolerans yoktur. Virgül ve nokta kabul edilir. `_TOL_UST` / `_TOL_ALT` yazımları da desteklenir, fakat aynı alan iki farklı başlıkla verilmez.

Geometri sütunu olmayan sunum sütunu, boş geometriye bağlı dolu sunum alanı, sayısal olmayan tolerans ve hem ana hücrede hem ayrı sütunda tolerans verilmesi anlaşılır hatayla reddedilir. Eski `12(+0,5|-0)` toleransları korunur. Eski `Ø10,5(herhangi bir metin)` biçimindeki son ek, standart/diş yorumu yapılmadan serbest gösterim metni olarak okunur; yeni dosyalarda ayrı sütun tercih edilir.

OCR sütun okuması `_METIN`, `_TOLUST` ve `_TOLALT` alanlarını ölçü etiketi saymaz. Bu değişiklik, yatay kesitin görünüş tespiti veya pah/tolerans içeren sabit taslak etiketleri sorunlarını tek başına çözmez.

## Verilen dosyayla test

Depo kökünde, .NET ve OCCT Python ortamı hazırken:

```sh
dotnet run --project checks/ExcelPresentationChecks.csproj -- samples/taslak61/taslak6.1.xlsx output/taslak61-parser-check/normalized.json
/workspace/occt-venv/bin/python -m unittest discover -s tools -p test_excel_presentation.py
```

İlk komut gerçek Excel’i okuyup 77 kontrol yapar ve yerel normalize veriyi çıkarır. İkincisi bu verinin altı satırını ölçü bağlama, serbest metin, tolerans, köşeli parantez onayı ve gerçek silindirik yüzey üzerinde çap desteğiyle sınar. Test silindirleri ayrıştırma/bağlama doğrulaması içindir; taslak6 parçasının doğru üretildiği anlamına gelmez. Normalize veri üretilmemişse bu bütünleşme testi atlanır; bağımsız kontroller çalışır. API çağrısı gerekmez.

## Çap gösterimi standardı

`_METIN` boşsa ana ölçü hücresinde Ø verilmiş olması Ø gösterimini belirler; modelin çap referansı tek başına Ø eklemez. `_METIN` doluysa nominal sayının ve otomatik Ø/R önekinin yerine aynen yazılır. Örneğin `B=Ø10,5`, `B_METIN=M12x1.5-6H` için gösterim `M12x1.5-6H` olur. Ayrı tolerans alanları mevcut davranışla eklenir. Modelin çap referansı ile gösterim tercihi ayrı kararlardır.

## Tolerans görünümü

Üst ve alt sapmalar eşit büyüklükte zıt işaretliyse `±` kullanılır. Farklıysa üst sapma üstte, alt sapma altta, daha küçük yazıyla çizilir. Metin aşamasındaki `(+0/-0,1)` gösterimi renderer tarafından iki satıra dönüştürülür; JPEG üzerinde eğik çizgi basılmaz. Çok küçük farklı sapmalar sıfıra yakın oldukları için simetrik sayılmaz. `_METIN` doluysa nominal gösterim bastırılır; ayrı toleranslar eklenmeye devam eder.

## Ana ölçü hücresinde pah

`1x45°`, `1 X 45°`, `1×45°` ve virgüllü ondalık boy/açı desteklenir. Ana hücrede pah geometri verisidir: nominalMm boyu, chamferAngleDeg açıyı taşır. Açı 0 ile 90 derece arasında olmalıdır. Gösterim metni ana hücreden korunur; `_METIN` doluysa yine gösterimi bastırır.

CadQuery yürütücüsünde `p["F"]` boyu mm olarak, `p["F__angleDeg"]` açıyı derece olarak taşır. Ek anahtar otomatik üretilir; kullanıcı Excel'e bu adla sütun eklememelidir. Geometri ve ölçü kodları aynı parametre tablosuyla çalışır. Satırlar arasında açı değişimi kaybolmaz. K gibi parantezsiz etiketin Excel değeri de modele gönderilir; çizim onayı ayrıca OCR'deki köşeli paranteze bağlıdır.

Verilen taslak6.4.xlsx için `checks/ChamferInputChecks.csproj` tüm altı satırda F/G/J boy+açılarını ve K=9,5 bilgisini sınar. `test_chamfer_input_binding.py` gösterim bilgisinin korunmasını ve parantezsiz K'nin çizimden dışlanmasını sınar. Bu destek etkin CadQuery akışına uygulanmıştır; eski v9 geometri tarifine pah derleme desteği eklendiği iddia edilmez.
