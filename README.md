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
- Sabit parametreler `precision=specified|estimated` ile ayırt edilir. Piksel oranından tahmin edilen detay belirtilmiş üretim ölçüsü sayılmaz. Açıklama/kanıt için kelime sınırı yok.
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
