# Açık orijin/referans sözleşmesi denemesi

Girdiler taslak2guncel.xlsx (dört satır) ve taslak2guncel.jpg. Dosyalar değiştirilmedi; kaynak SHA256 özetleri run-report.json içindedir. Yazılım ayrıştırılmış Excel'i ve çift görüntüyü tek API isteğinde gönderdi. Yeni veri şeması v4. Çizim istenmedi ve üretilmedi.

## Ne değişti?

Model artık referans görünüşü, orijinin dayandığı geometrik özelliği, tam JPEG'de yaklaşık orijin noktasını, eksenleri ve gövdenin bu referanstaki ankrajını açıkça döndürüyor. Kullanıcıdan koordinat istenmedi. Çözücü, delikleri ve ölçü orijinini aynı ötelemeyle yerel OCCT gövde merkezine taşıyabiliyor. Başka bir referans beyanını sessizce gövde merkezi saymıyor. Orijin gövde ekseni diye tanımlanmışken ankrajın sıfırdan farklı verilmesi, görünüş dışı nokta, döngü veya bulunmayan orijin özelliği reddediliyor.

Prompta B-G/-G/-F doğru cevapları veya bu gruba ait harf-konum eşlemesi eklenmedi. Ana eksen/datum tanımı genel özellik ilişkileri üzerinden açıklaştırıldı. Diğer değişkenler büyük ölçüde sabit tutuldu: aynı model, low reasoning, çift tam görüntü, nominal/tolerans ayrımı, tek çağrı. Önceki eksik JSON örneği de coordinateFrame/measurementSources/colorPolicyVersion alanlarını açıkça içerecek şekilde tamamlandı. Tek deneme, iyileşmenin yalnızca bir cümleden kaynaklandığının kanıtı değildir.

## Model ne döndürdü?

- Orijin: ön görünüşte gövdenin ana eksenleri ile ön yüzün kesişimi; yaklaşık tam-görüntü noktası (0,513; 0,408). E deliği orijin seçilmedi. Görsel işaret milimetre hesabında kullanılmaz; inceleme kanıtıdır.
- Gövde ankrajı: X=0/Y=0. Eksenler sağ/yukarı/izleyiciye doğru.
- Üst delik X=0, Y=alt delik Y+B; alt delik X=0, Y=-G.
- Üçüncü delik X=-F/Y=0. E boşsa yok; F=0 ise var ve merkezde.
- B üst-alt merkez mesafesi, F üçüncü deliğin yatay kaçıklığı, G alt deliğin ana eksene uzaklığı.
- F=0 ve G=B/2 koşulları yalnızca annotations bölümünde. Yeşil R8/33/3 geometride korunmuş, gösterimleri kapalı.
- Kesit hedeflerinde üç delik var; olmayan isteğe bağlı hedefler satırda kaldırılır.

Ham API içeriği ile kaydedilen model-plan.json karşılaştırıldı: eşit. Plan elle düzeltilmedi. Model iki açıklayıcı warning döndürdü (isteğe bağlı delik ve bağımsız B/G); bunlar eksik girdi bildirimi veya soru değil. Yerel doğrulama hatası yok, durum analysis-only.

## Dört satırın sayısal kontrolü

| Ürün | Üst delik Y | Alt delik Y | Üçüncü delik | F gösterimi | G gösterimi |
|---|---:|---:|---|---|---|
| 11-30-212 | 44,45 | -44,45 | (-44,5; 0) | Var | Yok |
| 11-30-200 | 44,5 | -44,5 | Yok | Yok | Yok |
| 11-30-92 | 86,7 | -78,7 | Yok | Yok | Var |
| 11-30-381 | 35 | -35 | (0; 0) | Yok | Yok |

Bu tablo model ilişkilerinin yerel, bağımsız sayısal değerlendirmesidir. Native çizim çalıştırıldığı anlamına gelmez. Ayrıntılar evaluated-summary.json içinde.

## Kontroller ve maliyet

68 C# kontrolü ve 10 OCCT kesit/geometri testi geçti. Gövde merkezi dışındaki bir datumdan tüm özelliklerin ve ölçü orijininin birlikte taşınması test edildi. Ürün JPEG'i üretilmedi. API çağrısı 1, sağlayıcının bildirdiği maliyet 0,055944 USD. İkinci değerlendirme çağrısı veya asistan plan müdahalesi yok.

## Sınırlar ve sonraki adım

Bu veri setindeki orijin, ölçü eşleşmeleri ve görünürlük koşulları doğru döndü. Bu sonuç bütün yeni taslaklarda doğruluk garantisi veya teknik resim üretim onayı değildir. Modelin işaretlediği pikselin gerçek eksen kesişimi olduğu bağımsız görüntü algılamayla doğrulanmıyor. Yalnızca X sağ/Y yukarı/Z izleyiciye doğru baz destekleniyor; başka baz dönüşümü raporlanır. Yerel geometri oluşturucu hâlâ desteklenen döndürülmüş dairesel pleyt ailesiyle sınırlı. İlişkiler geometry/annotations/source içinde hâlâ tekrarlanıyor; tek kaynaktan türetme sonraki ayrı geliştirmedir.

Sonraki adım, kullanıcı isterse bu dokunulmamış planla yeni API çağrısı yapmadan çizim almak. Genel dayanıklılık için daha sonra farklı bir taslakta aynı referans sözleşmesini değerlendirmek gerekir.
