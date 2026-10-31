# Yerel çizim ayarları — revize Excel

Bu düzen yuvarlak parça grupları için kullanıcı tarafından verilen kesit ve kamera ayarlarını API'den ayırır. Model geometrinin ne olduğunu anlamaya ve ölçü ilişkilerini tarif etmeye devam eder. Yeni API çağrısı henüz yapılmadığından anlama başarısı, token veya maliyet değişimi ölçülmedi.

## Excel sütunları

| Başlık | Biçim | Yerel anlamı |
|---|---|---|
| jpeg file name | Metin | Çıktı adı ve antette ürün kimliği |
| izometrik aci | ON_SAG | Ön, sağ ve üst yüzleri gösteren sabit ortografik kamera; derece değildir |
| kesit dogrultu | V / H | Üst görünüşte dikey / yatay kesit izi |
| kesit kacikligi | İşaretli mm | V: artı sağ, eksi sol. H: artı yukarı, eksi aşağı |
| kacik kesitin genisligi | Toleranssız mm | Merkezdeki kademenin toplam boyu; 30 → merkezden ±15 |
| A, B, C, … | Ölçü ve tolerans | API'ye ayrıştırılmış ölçü tablosu olarak gider |

Ondalık nokta ve virgül kabul edilir. Kaçıklık 0 ise düz merkez kesiti kullanılır; kademe boyu etkisizdir. Kaçıklık sıfır değilse kademe boyu pozitif olmalıdır. Yerel ayar sütunlarından biri mevcutsa dördü de doldurulmalıdır; geçersiz veri API çağrısından önce durdurulur. Türkçe harfli başlıklar da desteklenir.

Üst yüzeyin merkezi dünya orijinidir: +X sağ, +Y yukarı, +Z üst yüzeyin dışına doğru; gövde -Z yönüne uzanır. Bu konvansiyon modele iletilir. Yerel sütunların satır değerleri modele gönderilmez. Kesit izinin uçları etiket A veya delik sayısı varsayımıyla değil, oluşturulan gerçek OCCT gövdesinin sınırlarından belirlenir.

## Model ve yazılımın görevleri

- Yeni sütunlu Excel kullanıldığında prompt/sözleşme kamera, kesit veya görünürlük kararı istemez. Kayıtlı eski tariflerin yerel incelemesi korunur. Yeni API analizi yerel ayar sütunlarını gerektirir; bu sütunlar yoksa eski prompta dönülmez.
- Model ölçü anotasyonunun rengini `#000000` veya `#008000` olarak bildirir. Yazılım yeşili gizler; yeşil ölçü nominali geometriden çıkarılmaz. JPEG'deki renk sınıfını tanımak modelin görevi olmaya devam eder. Eski `black` / `green` yanıtları da okunur.
- Toleranslar geometriye karıştırılmaz. Boş ile sıfır korunur. Model ölçü ve toleransı yeniden hesaplamaz; yerel ayrıştırıcı kaynak hücreyi tutar.
- Yerel ayarlar `local-drawing-settings.json` dosyasına; native kesit çözümü `native-drawing.json` dosyasına kaydedilir. Ham model yanıtı değiştirilmez.
- JPEG çıkışı mevcut sabit 1754×1240 boyutunda ve kaynak DPI metadata'sı ile kalır. Bu tek başına fiziksel A4 veya gerçek baskı ölçeği garantisi değildir.

## Revize dosyanın kontrolü

`taslak4.2rev.xlsx`: 3 satır, her satırda 9 ölçü sütunu. Kaçıklıklar -73 / -44,5 / 0; kademe boyları 30 mm. İlk satırdaki Ø34 deliğin tamamı 30 mm kademe aralığına sığmaz. Yazılım kullanıcının 30 değerini değiştirmez; tüm deliğin o bantta görünmesi isteniyorsa giriş genişletilmelidir.

Derleme, gerçek Excel'in ayrıştırılması, promptta kamera/kesit ve görünürlük talebi bulunmaması, V/H ve işaret yönleri, sıfırda düz kesit, ±15 kademe uçları, renk gizleme ve gerçek OCCT üzerinde kesit üretimi test edildi. Bu kontrolde API çağrısı ve yeni ürün JPEG'i üretilmedi.

## Mevcut sınır

Genel v9 paftası hâlâ inceleme çıktısıdır: taslak anteti ve yerleşimi birebir kurulmaz; ölçüler tablo olarak gösterilir. Bu değişiklikler o eksikleri giderdiğini iddia etmez. Sonraki adım revize Excel + eşleşen taslak4.2 JPEG ile tek bir yeni API denemesinde geometri, kesit ve kullanım maliyetini değerlendirmektir.

## Sonnet ile devam ayarları

Etkin prompt ve sözleşme artık ayrı `local-prompt.txt` / `local-contract.txt` dosyalarından okunur; eski sözleşmeden metin parçaları silinerek türetilmez. Etkin model `config/openrouter.json` içinde Sonnet 5.5, high, 65536 token tavanı ve 600 saniye olarak kayıtlıdır. Anahtar ortamda kalır; eski model ortam değişkeni bu ayarı geçersiz kılamaz. Batch kodu kaldırıldı. Eski koordinat düzeninde hazırlanmış onaylı tarifler yeni yerel düzende sessizce yeniden kullanılmaz. Bu hazırlıkta API çağrısı yapılmadı; maliyet veya anlama başarısı henüz ölçülmedi.

Etkin prompt yeniden sadeleştirildi: font, antet, dosya adı talimatları ve yerel sunum açıklamaları çıkarıldı. Kesit/kamera alanları etkin sözleşmede bulunmaz; eksik ayar sütunuyla eski prompta geçiş kapatıldı. Geometri içindeki direction, axisOrigin, Frame ve path alanları kamera/kesit değil, katıyı oluşturmak için kullanılan geometridir.

## Profil sözleşmesi netleştirmesi

Yeni yanıtta çokgen `polyline` yalnız sıralı köşeleri taşır; ilk köşe tekrarlanmaz, yazılım son düz kenarı oluşturur. Doğru/yay zinciri `path` bir başlangıç ve sıralı segmentlerden oluşur. Segment yalnız `end`, yay ayrıca `mid` taşır; başlangıcı önceki segmentten devralınır. Son `end` profil başlangıcına eşit olmalıdır; otomatik kapanış yoktur. Yeni sözleşmede `closed` alanı istenmez.

Eski açık başlangıçlı segment kayıtları okunur, ancak kopuk veya kapanmayan profil derleme sırasında açık hata verir; eksik kenar uydurulmaz. Dış çevrim ve iç boşluklar aynı kurala tabidir. Ekstrüzyon from/to değerleri profil orijininden u cross v yönündeki işaretli mesafelerdir. Tekrarlamada count toplam örnek sayısıdır, ek örnek sayısı değildir; ilk örnek indeks 0'dır.

8 yeni profil testi, mevcut geometri testleri ve C# kontrolleri çalıştırıldı. Önceki model yanıtı değiştirilmedi. API çağrısı veya yeni ürün denemesi yapılmadı.
