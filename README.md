# DrawingTool — genel CAD sözleşmesi v7

Girdi **bir JPEG + bir Excel**. Yazılım Excel'i yerelde ayrıştırır; OpenRouter'a **bir orijinal JPEG ve bir ayrıştırılmış örnek satır tablosu** gönderir. Kırmızı temizlenmiş ikinci görüntü ve nominal verilerin ikinci kopyası artık gönderilmez. Gruptaki bütün satırlar yerelde çözülür; büyük tablolarda modele en fazla sekiz temsilci satır gönderilir.

**Mevcut aşama:** genel parametrik tarif analizi ve satır başına çözümlenmiş JSON. Yeni genel OCCT katı/teknik pafta yürütücüsü henüz uygulanmadı. Analizin geçmesi, gerçek katının veya JPEG'in doğru üretildiği anlamına gelmez. Eski pleyt üretim yolu aktif komutlardan çağrılmaz.

## Kullanım

```bash
dotnet run --project src/DrawingTool.csproj -- analyze-cad-group input.xlsx template.jpg output/empty-run
```

OPENROUTER_API_KEY ve OPENROUTER_MODEL ortamdan okunur; anahtar/font repoya eklenmez. High akıl yürütme, tek çağrı, max_tokens=32768, beş dakika HTTP zaman aşımı. Otomatik yeniden değerlendirme yok. Soru beklemek yerine rapor üretir. Özgün yanıt, kaynak özetleri ve istek metni yerelde saklanır. Modelin özel akıl yürütme metni içerebilen ham API yanıtı yayımlanmaz.

## Geometri ve ölçülendirme ayrımı

- `geometry`: nominal parametreler, birimler/kaynaklar, koordinat bazları, özellikler ve son gövde. Tolerans sapmaları katı geometrisine katılmaz.
- `drawing`: aynı özelliklere bağlı ölçüler, görünüşler, kesitler ve geometrik toleranslar. Excel ölçüsü `valueSource={kind:"column",column:"A"}` ile bağlanır. Yazılım kaynak toleransını kendisi ekler; modelden tekrar yazması istenmez.
- Çözümlenen geometri nominal sayıları ve kaynak/birim metadatasını taşır. Ölçülendirme kendi `sourceMeasurement` kaydında nominal, tolerans, çap işareti ve sıfır/boş bilgilerini korur. Yeşil ölçülerin görünürlüğü yerelde kapatılır.
- Model özellikler için tek `uses` bağımlılık listesi döndürür. `cut` için [gövde, araç], gövde değiştiren işlemler için [gövde], diğerleri için geometrik girdiler. Yazılım `target/tool/inputs` ayrımını kendisi derler; atlanan koşullu özelliğin gövdesini ileri taşır.
- Model başarılı yanıtta yalnız geometry/drawing verisi döndürür; description/evidence/precision/issues istenmez. Verilmeyen geometrik detayları taslakla tutarlı tamamlar. Bu değerlerin nasıl seçildiği yanıttan ayırt edilemez; doğruluk insan kontrolüne tabidir. Tarif oluşturulamıyorsa yalnız `{"error":"Kısa Türkçe hata."}` döner. Yerel teknik kayıtlar model raporundan ayrıdır.
- Profil sözlüğünde daire, kapalı çokgen, yuvarlatılmış kanal ve doğru/üç noktalı yay segmentlerinden kapalı yol bulunur. Kenar seçimleri adın yanında geometrik yakın nokta ve yön içerir. Kesitler koordinat bazında kesme izi ve süpürme yönü taşır.

`CadRecipeV7` dış sözleşmeyi derler; mevcut test edilmiş `CadRecipe` bağımlılık/parametre çözücüsü özel iç temsil olarak kullanılır. Bu iç temsil API'ye gönderilmez. Tarihsel v6 JSON kayıtları yeni analiz komutunca otomatik dönüştürülmez. `review-cad-group` v7 yanıtını yeni API çağrısı olmadan, kaynak özetlerini kontrol ederek inceler.

Sınırlamalar: desteklenen özellik sözlüğü sonlu; genel cebirsel kısıt çözümü, native kenar/yüz eşlemesi ve genel pafta yürütücüsü tamamlanmadı. Doğrulama yapısal/aritmetik kontroller sağlar; görsel/geometrik doğruluğun tam kanıtı değildir. `run-cad-group` bu eksik yürütücüyü raporlar, eski pleyt motoruna sessizce dönmez.

## Kontroller

.NET SDK global.json ile sabitlenir; ClosedXML NuGet paketidir. Tek görüntülü analiz için Python ön işlemesi gerekmez.

```bash
dotnet build src/DrawingTool.csproj
dotnet run --project checks/LayoutPolicyChecks.csproj
```

Testler tolerans değişiminin geometriyi değiştirmediğini, ölçülendirmeye kayıpsız ulaştığını, kaynak/birimlerin korunduğunu, bağımlılık/boş-sıfır/yeşil davranışını ve yay profillerini denetler. Native çizim testi değildir.


## Yalnız veri promptu

High akıl yürütme ve tek JPEG/tek tablo korunur. Sıfır ve boş veriler değiştirilmeden, yorumları dayatılmadan iletilir. Özellik varlığı ve gizleme koşulları sözleşmenin seçenekleridir; prompt belirli bir sütuna özel sıfır senaryosu anlatmaz. quantity=1, visible=true, hideIf=never ve presence=always varsayılanlarını yazılım ekleyebilir. Eski v7 kayıtlarını inceleyebilmek için eski açıklama alanları okunabilir; yeni yanıtta istenmez. Belirsizliği açıklama üretme zorunluluğuna dönüştürmez. Geometri/ölçü ilişkileri ve işlem argümanlarının kesin anlamları korunur.

## Kesit sözleşmesi: düzlem ve görünüşte iz

Düz kesit: `{id,view,kind:"planar",frame,plane:{point:[x,y,z],normal:[nx,ny,nz]},targets:[]}`. Nokta ve normal belirtilen koordinat bazındadır. Yazılım dünya koordinatına dönüştürüp normali normalize eder; kesit görünüş yönüyle paralellik kontrol edilir. Model kesme yüzeyi için süpürme yönü veya çizgi uzunluğu hesaplamaz.

Kademeli kesit: `{id,view,kind:"stepped",sourceView,origin:[x,y,z],path:[[u,v],...],targets:[]}`. origin dünya koordinatıdır; u/v kaynak görünüşün ekrandaki sağ/yukarı yönlerinde mm değerleridir. Yazılım kaynak görünüş derinliğini ve iz noktalarının dünya koordinatlarını türetir. Her parça için modelden gelen yolu kullanır; belirli delik sayısına/ürüne özel kural yoktur. Çözümlenmiş kayıt `worldPath`, `sweepDirection` ve segment başına `cuttingPlanes` içerir. Planar kayıtta dünya koordinatlarında tek `cuttingPlanes` kaydı vardır.

Eski v7 path/extrusionDirection kesitleri yerel inceleme için okunabilir; yanlış yönleri sessizce onarılmaz. Önceki kapaktaki Y izi + X süpürmesi, X yönünden kesit görünüşü için artık doğrulamada reddedilir. Kaynak model tarifi değiştirilmez. Kesit yolu seçiminin teknik resim açısından doğru olması hâlâ model ve insan incelemesinin sorumluluğudur; bu kontrol mekanik tutarlılık sağlar.

Kesit verisi/çözümleme güncellendi; native OCCT katı ve kesit yürütücüsü bu değişiklikle tamamlanmış sayılmaz. 55 yerel kontrol geçti; bu değişiklikte ücretli API çağrısı veya çizim yapılmadı. Uzunluk/birim ve delme sözleşmeleri değiştirilmedi.

Parametre birimleri promptta açıkça tanımlıdır: uzunluk/pay mm, açı deg, adet count, oran/çarpan scalar. Sayısal işlem alanlarının birimi alan anlamından gelir; yön vektörleri boyutsuzdur. Türetilmiş hesaplarda birim kontrolü korunur. Son birim promptu revizyonu için yeni API çağrısı yapılmadı. Ek sözleşme verim önerileri previews/contract-optimization-review/NOTLAR.md içindedir; öneriler otomatik uygulanmış değildir.

## Özellik referanslı kesit ve kayıtlı grup tarifi (aktif)

Model artık kesit yolu koordinatları yerine `{id,view,sourceView,kind:"featureTrace",main:reference,through:[reference,...]}` verir. Referans `{feature,entity:"axis"|"frameOrigin",instance?:index}` biçimindedir. Eksen çözümü hole/cylinder/revolve, dairesel extrude ve circularPattern örneklerini destekler. Diğer geometriler için frameOrigin kullanılabilir; her keyfi yüzün ekseni otomatik tanınmaz. Özellik kimliği ve desen örneğini model seçer; yazılım görüntüden parça tanımaz.

Yazılım referans noktalarını kaynak görünüşe taşır, iz boyunca sıralar, kademe geçişlerini komşu referanslar arasında üretir. Mevcut olmayan özellik atlanır, sıfır sapma düz kesite dönüşür; boş değer sıfıra çevrilmez. Aynı iz seviyesinde farklı eksenler belirsizse raporlanır. İz uçları için muhafazakâr sunum uzanımı kullanılır; native BRep sınırlarıyla kırpma henüz uygulanmadı. Yerel birim/bağımlılık/geometri kontrolleri görsel doğruluk garantisi değildir.

Geçen analizde recipe-cache.json aday kaydı oluşur. Onay otomatik verilmez:

```bash
dotnet run --project src -- approve-cad-recipe output/accepted-analysis
dotnet run --project src -- analyze-cad-group new.xlsx same-template.jpg output/new-run
```

Onay komutu tarifi `.recipe-library/<image-sha256>` altına kaydeder (CAD_RECIPE_LIBRARY ile konumu değişir). Sonraki normal analiz aynı JPEG için onaylı tarifi otomatik bulur; API anahtarı veya çağrısı gerekmeden çözümleme yapar. JPEG/tarif özeti, sütunlar ve ayrıştırılmış boş/sıfır/değer örüntüsü kontrol edilir. Yeni örüntüde rapor verir, otomatik API'ye dönmez. Sayısal değerler/toleranslar değişebilir, her satır tekrar doğrulanır; yeni değerlerin fiziksel/üretim doğruluğu ayrıca kontrol edilmelidir.

`reuse-cad-group <xlsx> <jpeg> <saved-run> <output>` aday tarifi API'siz incelemeyi de sağlar; raporda aday/onaylı ayrılır. `analyze-fresh-cad-group` kayıtlı tarifi atlayıp açıkça yeni ücretli analiz yapar. Bu cache, provider token cache'i değildir. Genel native JPEG/STEP yürütücüsü hâlâ tamamlanmadı; run-cad-group kayıtlı tarif bulsa da yürütücü eksikliğini raporlar.

64 kontrol geçti; kapak denemesi previews/kapak-feature-trace/NOTLAR.md içindedir.
