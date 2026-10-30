# v6 sözleşme risk incelemesi

Kullanıcı yaklaşımı: modelin teknik resim bilgisini kullanmasına izin vermek; az uyarı, gerekirse daha uzun fakat eksiksiz çıktı. Bu incelemede API çağrısı, çizim ve uygulama kodu değişikliği yok. Mevcut CadRecipePrompt, CadRecipe, CadRecipeWorkflow ve gerçek group2-v6 kayıtları incelendi.

## Öncelikli bulgular

### 1. Kaynak ölçünün geometrik hedefi yeterince kesin değil

`selectors:[{operation,role:string}]` kullanılıyor. role sözlüğü kapalı/değerlendirilen bir semantik sözlük değil. Son yanıtta `outerRim` ve iç/dış R8 yorumu değişmiş. Kod şu anda gerçek OCCT yüz/kenarı olmadığı için bu adın hangi yayı göstereceğini doğrulamıyor. Aynı sözcük ağız kenarı veya alt büküm için kullanılabilir. Yalnız R8 sayısının doğru dönmesi yetmez.

Çözüm önerisi: ölçü okunun ilişkilendiği profil yayı, yüzey veya özellik kendi mantıksal kimliğiyle tanımlansın; source view/ölçü ucu/hedef ve türetilen ölçü bağı korunarak native seçime aktarılsın. Bu bilgi model tarafından çıkarılır; kullanıcı koordinat hazırlamaz. Görsel noktalar kanıttır, tek başına doğru algılamayı garanti etmez.

### 2. Sözleşme geometrik açıklamayı eksik temsil ediyor

Sketch yalnız circle, polyline ve roundedSlot tanımlıyor; genel line+arc kapalı profili yok. Parametre türetme yalnız iki girdili dört işlem. Parametrik açısal referanslar, daha genel yüzeyler ve profil ilişkileri sınırlı. Model doğru anladığı kıvrılmış kesiti birebir anlatmak yerine silindir farkı + fillet yoluna zorlanabilir. Bu, yanlış yorumun kanıtlanmış tek nedeni değil; gerçek temsil sınırıdır.

Çözüm önerisi: çizgi/yay içeren profil dili, açık çerçeve dönüşümleri ve kontrollü geometrik bağıntılar. Her olası işlemi bir anda desteklemek veya modele serbest program kodu çalıştırmak gerekmiyor. Anlam katmanında bilinmeyen özellik kaydı korunmalı, uygulama desteği ayrı raporlanmalı.

### 3. Tolerans/kaynak bağlantısı çözülmüş tarifte korunmuyor

Gerçek 92 kaydı: input A = nominal286, üst sapma+1/alt sapma-1. Ham recipe parameters A -> column A/mm. Resolved parameters A -> 286; resolved dimension nominal286. Resolved JSON'da tolerans sapmaları ve kaynak sütun eşlemesi yok. Excel ve ham recipe hâlâ saklı olduğundan orijinal bilgi silinmiş değil; fakat yeni renderer yalnız resolved JSON'u kullanırsa eksik veri alır.

Çözüm önerisi: parametre çıktısı nominal, unit, source column, tolerance ve origin/evidence bağını birlikte korusun. Model toleransı yeniden hesaplamasın; yerel ayrıştırıcı bağlasın. Türetilmiş parametreye otomatik kaynak toleransı kopyalamak doğru değildir; türetilmiş geometrinin hangi açık ölçüyle gösterileceği ayrı bağ olmalı.

### 4. Biçim kontrolü doğruluk kontrolü değil

Resolve bağımlılık/alan/girdi sayısını kontrol ediyor; args şekilleri, pozitif uzunluklar, tüm semantik roller, ölçü tipleri, view yönleri veya native yüz karşılıkları kapsamlı biçimde doğrulanmıyor. Her sayısal Excel sütununun parametresi olması kontrol ediliyor; parametrenin bütün ölçülen ilişkileri geometride sağladığı kanıtlanmıyor. Bir parameter:286 kaydının olması geometrinin gerçekten Ø286 olduğu anlamına gelmez. İki girdi tipi/rol ayrımı da sınırlı.

Çözüm önerisi: JSON yapısı, geometrik hesap ve native doğrulama ayrı statüler taşımalı. Native tamamlanmadan planı üretilebilir gibi etiketlememek gerekir. Modelin yorumunu değiştirmeyen matematiksel kontroller yazılımda kalmalı.

### 5. Kesit ve görünüş tarifi üretim için eksik

Section şu anda kind + view + hedef ID listesinden oluşuyor. Bu liste genel bir kademeli kesitin düzlemlerini, yönünü ve geçişlerini tek başına tanımlamaz. Varsayılan pafta ve ölçü yerleşimini yeni yürütücü henüz uygulamıyor. Views/geometricTolerance biçim ve ilişki kontrolleri de sınırlı. Hedef listesi doğru olsa bile aynı çizim çıkmayabilir.

Çözüm önerisi: modelin kesit amacı, referansı ve gerekiyorsa yolu/plane ilişkileri kayıpsız tanımlansın. Yerleşim tercihleri ile üretim boyutları ayrılmalı. Sadece yeni delik sayısını saymak genel kesit çözümü değildir.

### 6. Kısa cevap talimatı gereksiz risk

"Description one short sentence" ve "evidence <=8 words" talimatları var. Bu gerçek sayısal alanları kesmiyor, ancak R8'in hangi yüzeye/yaya ait olduğunu anlatacak gerekçeyi aşırı sıkıştırabilir. Yanlış sonucu bu talimatın doğurduğu kanıtlanmadı; doğruluk önceliğiyle uyumlu olmayan gereksiz bir kısıt.

Öneri: kelime sınırı yerine yeterli açıklık ve gerekirse ayrıntı. Sıradan tekrarı azaltmak başka şey, gerekli tanımı kısaltmak başka şey. Daha uzun yanıtın kendisi de doğruluk kanıtı değildir.

### 7. Her sabit için parametre kaydı ve modelden derleme ayrıntısı

"two", "minusOne" gibi yardımcı sabitler bile ID ve ayrı derived düğümleriyle tanımlanıyor. Radyus, eksen, CAD operasyon sırası ve bütün gösterim kayıtları aynı çağrıda çıkarılıyor. Bu büyümeyi ve bağımlılık hatasını artırabilir. Modelin doğal teknik açıklaması ile bizim yürütme planımız aynı şey olmak zorunda değil.

Öneri: parça anlamını kayıpsız koruyan tek tanım; bunu native işlem sırasına çevirme yükünün uygun kısmı yerel derleyicide. Bu kullanıcıya CAD tarif ettirmek değildir. Ancak mevcut native yürütücünün henüz yazılmadığı unutulmamalı.

### 8. Katı yanıt şeması fiilen gönderilmiyor

response_format=json_object yalnız JSON biçimi ister, alanların doğruluğunu garanti etmez. Tür/kind gibi eski alan hatalarını engellemez. Operation alanları aynı nesnede target/tool/inputs/optionalInputs taşır; v6 kuralları önceki belirsizliği azalttı fakat model hâlâ yanlış kombinasyon verebilir.

Öneri: sağlayıcı desteği doğrulanarak işlem türüne göre JSON Schema/discriminated union. Şema alan adlarını kesinleştirsin; görsel yorumun doğru olduğunu garanti etmez. Bu da input token maliyetinin tamamen yok olacağı anlamına gelmez.

### 9. Varsayım politikası uygulamada yeterince ayrı değil

Kullanıcı ölçüsüz görsel ayrıntılarda makul temsil kabul ediyor. Şu anda model hem makul yaklaşık bilgileri hem açık ölçünün farklı yorumunu aynı issues/warning yapısında bildiriyor. Kapak boss çapının yaklaşık alınmasıyla R8'in açık hedefinin değişmesi aynı durum değildir.

Öneri: measured/inferred/approximate ayrımı ve kaynak bağı. Açık ölçülü alanlarda uygunluk kontrolü; ölçüsüz alanlarda kullanıcı kabul kapsamına göre temsil. Çok fazla genel uyarı yerine varsayımın nerede kullanıldığı ve etkisi. Kullanıcının bir gruptaki kabulü bütün gelecekteki ölçülü detayları otomatik değiştirme yetkisi değildir.

### 10. Token ve zaman sınırı

20.000 completion üst sınırına reasoning de dâhil. Yanıt uzadıkça kesilme riski ve üç dakikalık HTTP süresi sınırı sürüyor. Kullanıcı yeterli uzunluğa izin veriyor diye çıktı sonsuz olamaz. Mevcut kod eksik yanıtı reddediyor, özgün yanıtı saklıyor; bu korunmalı. Otomatik sınırsız yeniden çağrı gerekmiyor. Beklenen tarif büyüklüğü ve muhakeme için bütçe ayrılmalı, ücret kayıt altına alınmalı.

## Önerilen tasarım ilkesi

Az uyarı, kesin arayüz, kayıpsız tanım. Modelin resmi anlama aşamasını gereksiz üretim sınırlamalarıyla daraltmamak; tanınan bütün özellikleri ve ölçü bağlarını korumak. Yerel katmanda destek/birim/bağımlılık/katı/ölçü kontrolleri yapmak. Aynı nesnenin farklı yerlerde bağımsız yeniden yorumlanmasını azaltmak. Anlam ile uygulama arasındaki açıklık eksikliğini prompta yeni yasaklar ekleyerek kapatmamak.

Önce kaynak-ölçü-hedef bağını ve tolerans aktarımını tamamlamak; genel profil/yay ve kesit temsilini netleştirmek; sonra native yürütücüyü tamamlamak mantıklı. Mevcut sözleşmeyi kayıpsız ilan edip doğrudan native kodlamaya geçmek riskli. Bu bir inceleme/öneridir; burada değişiklik uygulanmadı.
