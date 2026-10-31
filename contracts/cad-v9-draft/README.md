# CAD v9 — prompt ve sözleşme taslağı

Durum: **v9 yerel yürütücüye bağlandı; kapak grubu ile denendi**. `src/CadRecipePrompt.cs` bu klasördeki prompt ve sözleşmeyi birer kez okur. `CadRecipeV9` ve `tools/cad_v9_compiler.py` ifadeleri/koşulları çözer; sıralı işlemleri özel native yürütücü yapısına indirger. API sonucu ve sınırlar: `previews/kapak-v9/NOTLAR.md`. Bu sonuç tam üretim paftası veya bütün parça aileleri için doğrulama değildir.

Model isteği hazırlanacağı zaman `prompt.txt` ve `contract.txt` birer kez, ardından mevcut ayrıştırılmış `tableInput` ve bir JPEG gönderilecek. Kullanıcı JPEG/Excel vermeye devam eder; koordinat hazırlamaz. Bu dosyalar yeni model talimatıdır; bu README modele gönderilmez.

## Kabul edilen değişiklikler

- Tek mevcut gövde üzerinde sıralı add/cut/fillet/chamfer. Model ayrı kesici/ara gövde/eskiz özellikleri ve bunların bağlantı grafiğini üretmez. Profil ve kesici işlem içinde yer alır; son gövde sonuçtur.
- Alanlarda doğrudan sayı veya `=A/2-3` gibi ifadeler. Tekrar serbest; yardımcı değişkenler yalnız kolaylık için isteğe bağlıdır. Yerel yorumlayıcı hesaplayacak, model bağımlılık grafiği yazmayacak.
- Aynı profil içinde doğru/yaylarla radyus tarif etme ve gerektiğinde sonradan fillet seçeneklerinin ikisi de korunur. Bu, dışarıdan gelen model tarifini elle düzeltme izni değildir.
- Nominal geometri ve kaynak toleranslar ayrıdır. Koordinat ve kesit seçimini AI yapar; sayısal uygulama yereldedir. Gerçek ölçüyü katıdan ölçüp Excel ile karşılaştırma bu sürüme alınmadı. Bu karar, model yanıtlarının hatasız olduğuna dair bir garanti değildir.

## Alınmayan genişlemeler

25 bin karakterlik dış sözleşme kopyalanmadı. Loft/sweep/shell, ayrıntılı antet hücre tarifi, expected/ölçülen değer karşılaştırması ve otomatik ek API/onarım çağrısı eklenmedi. Betik üretimi kullanılmaz. Genel parça desteğinin kapsamı tanımlı geometrik işlemlerle sınırlıdır; her parçayı ifade etme iddiası yoktur.

## Entegrasyon ve kalan sınırlar

V9 ifade dili, isteğe bağlı değişkenler, koşullar ve tek gövde işlem sırası ayrıştırıcı/yürütücüye bağlandı. Özellik ID'leri ayrı gövdeler değil, sıralı işlemlerin kökenini belirtir; ölçü/kesit/kenar referansları buna göre çözümlenmeli. `featureTrace` profil içindeki bir deliğe ayrı ID vermiyorsa o deliğe referans kuramaz; kesitte adı gereken bir deliği ayrı cut işlemi yapmak mümkündür. Bu sürüm kesit izinin yerel algoritmasını düzeltmiş sayılmaz.

Önceden kalan taslak anteti, sayfa düzeni ve gerçek ölçü okları eksikleri bu metinler hazırlanarak giderilmiş sayılmaz. Raporlama/OCCT geçerlilik kontrolleri kaldırılmadı; yalnız yeni gerçek ölçü karşılaştırma sistemi eklenmedi.

API çağrısı ve native inceleme için: `dotnet run --project src/DrawingTool.csproj -- run-fresh-cad-group <xlsx> <jpeg> <empty-output>`. Kayıtlı yanıtı API çağrısı yapmadan tekrar yürütmek için `render-saved-group <xlsx> <jpeg> <saved-run> <empty-output>` kullanılır. Eski v7/v8 kayıtları desteklenir. Ayrı C++ köprü yazılmadı; mevcut yerel Python/OCP katmanı kullanılır. Taslak3/4 vb. için özel geometrik ipuçları isteme eklenmedi.

Kenar seçimi native yürütücüde near/direction ile yapılır; operation köken kapsamını bütün Boolean değişimlerinde kesin takip etme desteği tamamlanmış değildir. Kesit featureTrace algoritmasının önceki sınırlamaları sürer. Modelin kapak yanıtında fillet veya featureTrace yoktur; bu test o yolların başarısını kanıtlamaz.

## Güncel kapsam: detay görünüşü kaldırıldı

Aktif prompt ve sözleşme artık detay görünüşü istemez. V9 `drawing.details` alanı boşsa eski boş alan normalize edilerek kaldırılır; doluysa desteklenmeyen görünüş raporu verilir, otomatik onarım çağrısı yapılmaz. Native detay odaklama/kırpma/çizim ve sayfada detay için yer ayırma kodları kaldırıldı. Eski v7/v8 kayıtlarındaki detay meta verisi yeni çözülmüş çizime taşınmaz; doğrudan native yürütülen tarihsel çözülmüş dosyalarda da detay görünüşü üretilmez. Tarihsel ham yanıtlar ve örnekler değiştirilmedi.

Bu kapsam değişikliği parça geometrisindeki radyusları, boşaltmaları veya ana kesitleri kaldırmaz. Kullanıcının gerekli biçim ve ölçüleri ana görünüş/kesitte göstermesi beklenir; yazılım girdi JPEG'ini silme/kırpma işlemiyle değiştirmez. Bu değişiklikte model çağrısı yapılmadı. Yerel kontroller: 91 C#, 11 v9 Python ve 9 native Python kontrolü geçti; native kontrol geçici klasörde detay meta verisine rağmen yalnız ana görünüş/kesit/izometrik üretimini sınar.
