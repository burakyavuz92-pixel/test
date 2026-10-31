# Etkin CAD v9 sözleşmesi — anlam ve yürütücü denetimi

İncelenen kaynaklar: contracts/cad-v9-draft/local-contract.txt, local-prompt.txt, tools/cad_v9_compiler.py, tools/profile_contract.py, tools/cad_recipe_executor.py. Yeni API çağrısı veya üretim kodu değişikliği yapılmadı. Bulgular modelin iç düşüncesine ilişkin kanıt değildir.

## 1. Kenar referansı: operation — doğrulanmış uygulama çelişkisi

Sözleşme operation alanının kenarın yapım kaynağını daralttığını söylüyor. Derleyici alan yoksa önceki güncel gövdenin ID'sini ekliyor; native seçici alanı hiç okumuyor. Özelliğin kendi sınırı, işlem sonrası bütün gövde ve bugünkü gövdede o işlemden kalmış kenarlar aynı şey değildir. Bunlardan hangisinin kastedildiği de açıklanmamış.

Yerel deney: basit silindir fillet seçicisine operation=DOES_NOT_EXIST verildi; hem derleme hem OCCT üretimi geçti. Bu gerçek sözleşme/uygulama uyumsuzluğudur. Öneri: gerçek topolojik köken takibi uygulanana kadar yeni sözleşmeden operation alanını kaldırmak. R2'de zaten yanlış near koordinatı var; bu değişiklik tek başına R2'yi taşımaz.

## 2. near — belirsiz ad, gizli hassasiyet gereksinimi

near kelimesi yaklaşık bir konum izlenimi veriyor. Kodun kabul eşiği kenara 0,001 mm; model fiilen kenarın üzerinde bir nokta hesaplamak zorunda. Sözleşme bu hassasiyeti ve bütün near koordinatlarının dünya koordinatı olduğunu açık söylemiyor. axis/tangent seçiminin yön işaretinin kodda önemsenmediği (abs dot), hizalama eşiğinin >0,9 olduğu da belirtilmiyor.

Öneri: alanı pointOnEdge olarak açık anlamla tanımlamak, dünya koordinatı olduğunu bir kez belirtmek. Eşdeğer adaylarda hata verme kuralını yerelde tutmak; yaklaşık nokta desteklenecekse bunu ayrı, gerçek bir algoritma olarak tasarlamak. İsim değişikliği tek başına yürütücü davranışı değiştirmemeli.

## 3. Radyus: doğru büyüklük, yanlış fiziksel geçiş — kanıtlanmış tarif hatası

Fillet size'ın radyus olduğu açıkça yazılmamış; chamfer size'ın iki eşit mesafe olduğu ise yazıyor. Daha önemlisi near+axis, iç/dış veya hangi iki yüzün birleşiminin hedeflendiğini ifade etmiyor. Doğru bir geometrik kenarı seçmek, taslaktaki oku doğru anlamış olmak değildir.

Sonnet high ve Haiku high aynı dış arka köşeyi tarif etti; native sonuç bunu doğruluyor. Taslak R2 deliğin iç geçişine yöneliyor. Bunun sebebinin kesinlikle sözleşme olduğu söylenemez. Sözleşme seçimi ifade edebiliyor, fakat yanlış yorumu yakalamıyor. Önce temel geometri kurulumu ve taslaktaki geçiş eşleştirmesi düzelmeli. Desteklenmeyen serbest metin inner/outer alanı eklemek çözüm sayılmaz. Gerekirse iki komşu yüzün makinece çözülebilen tanımı tasarlanıp yürütücüde gerçekten uygulanmalı; mevcut profil yayı seçeneği de geçerli.

## 4. Koordinat kapsamı — olası model belirsizliği

P2 ve P3 yalnız boyut olarak tanımlanmış. Profil P2 noktaları yereldir; Frame.origin/u/v dünya uzayındadır; revolve axisOrigin/axisDirection dünya uzayındadır ve derleyici bunları profil bazına dönüştürür. Cylinder origin/direction, linear step ve EdgeSelector.near dünya uzayındadır. Sözleşme bunu tek bir kapsam kuralıyla açık söylemiyor. Model ekseni profil koordinatında verirse iki kez dönüşmüş gibi yanlış sonuç oluşabilir; bu R2 örneğinde kanıtlanan sebep değil, genelleşme riskidir.

Öneri: bir satırlık kapsam tablosu. P2=profil yerel koordinatı; açıkça aksi belirtilmedikçe P3=dünya koordinatı. Ekstrüzyon from/to profil normaline göre istisnadır. Dönme pozitif açısı sağ el; kısmi dönüşte başlangıç profili başlangıç açısını belirler.

## 5. Ölçü referansları — görünürde daha güçlü bir sözleşme

role serbest metin; kod geometrik anlamını çözmüyor. targets yalnız işlem varlığı/instance ve uygulanmışlık açısından kontrol ediliyor. Örneğin rastgele role kabul ediliyor. Dönen nominal Excel'den alınır; bu değerin oluşturulan katıdaki gerçek uzunluk olduğu doğrulanmaz. E boyundaki low hatasının raporsuz kalabilmesi bunun örneği.

Bu eksiklik mevcut ölçü tablosu tasarımının sınırıdır; kullanıcı daha önce ölçülerin yeniden ölçülmesini istememiştir. Bu denetimde böyle bir kontrol eklenmedi. Öneri: bu sürümde targets/role'u geometrik doğrulama garantisi gibi sunmamak. Gerçek ölçü oku üretimi hedeflenecekse serbest metin yerine ölçü tipine göre somut nokta/eksen/yüz referansları ve bunların yürütülmesi ayrı tasarlanmalı.

## 6. Açı birimi — doğrulanmış uygulama hatası

Sözleşme angle ölçüsüne ve Excel kolonundan valueSource kullanımına izin veriyor. Derleyici kolonlu ölçülerde unit değerini koşulsuz mm varsayıyor. Yerel deneyde type=angle ve column A=45, unit=mm üretti. Tablo da genel mm başlığı taşıyor. Bu mevcut R2 hatasını açıklamıyor, farklı parçalarda açık sorun çıkarır. Öneri: açı tipi için deg, uzunluk tipleri için mm; başlık/format da uyumlu olmalı. Ham nominalMm adı açı için yanıltıcıdır; açı giriş desteği veri ayrıştırıcısıyla birlikte ele alınmalı.

## 7. Yüz merkezi ve -Z kuralı — sınırlı kapsam

Round part top-face center ifadesi küresel veya çok kademeli/çok yüzlü parçalarda tek başına kesin bir referans olmayabilir. The body extends towards -Z ifadesi üst yüzde hiç çıkıntı olamayacağı şeklinde de okunabilir. Mevcut yuvarlak grup varsayımıdır, bütün kaynak içermeyen parçaları kapsamaz. Öneri: ana referans yüzeyi merkezini ve kalınlık yönünü tanımlamak; bütün katıyı -Z yarı uzayına zorlayan genel bir yasak gibi sunmamak. Kapsam genişletilecekse referans yüz seçiminin nasıl belirlendiği kararlaştırılmalı.

## 8. İkincil eksikler

- when boolean veya expression deniyor; karşılaştırmanın '=A>0' biçiminde olması gerektiği daha doğrudan örneklenebilir. Kod özelliklerde boolean kontrol ediyor, ölçülerde aynı katılık yok.
- Profile holes iç çevrimlerin dış çevrim içinde olması ve birbirini kesmemesi net tanımlanmamış; üç noktalı yayın üç farklı ve doğrusal olmayan nokta gerektirdiği de yazmıyor. Bunlar kısa veri tanımları ve yerel doğrulamalarla ele alınmalı.
- geometricTolerances.value ile hedef rolünün hangi birim/ilişkiyi ifade ettiği belirsiz; tam GD&T sözleşmesi değil.
- Kod count için 1..1000 sınırı uyguluyor; sözleşmede bu sınır yok. Bu anlam çelişkisinden çok eksik sınır tanımıdır.
- Profil kapanışı, from/to işareti ve tekrar count anlamı önceki revizyonda netleştirilmiş. Bunları tekrar genişletmek gerekmiyor.

## Öncelik sırası

1. Desteklenmeyen operation daraltmasını kaldırmak veya gerçek davranışını uygulamak.
2. Geometrik koordinat kapsamını, fillet size ve pointOnEdge anlamını kısa ve kesin tanımlamak.
3. Birim ve veri doğrulamalarını yürütücüyle eşleştirmek.
4. R2 için doğru iç geçiş geometrisini ve kenar seçimini yerel testle ayırt etmek; sabit ürün koordinatı eklememek.
5. Ölçü hedeflerinin bu sürümde neyi doğrulamadığını açık tutmak; gelecekteki üretim paftası referans tasarımını ayrı ele almak.

Çok sayıda uyarı eklemek yerine desteklenen alanları daraltmak, her alanı tek anlamlı tanımlamak ve karşılığını gerçekten çalıştırmak gerekir. Bu düzenlemeler R2 yorumunun otomatik düzeleceğine ilişkin garanti değildir.
