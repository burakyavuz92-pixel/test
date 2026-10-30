# CAD v9 — prompt ve sözleşme taslağı

Durum: **yazılım entegrasyonu bekliyor**. Bu klasör tek başına dağıtıma alınmış bir özellik değildir. Aktif `src/CadRecipePrompt.cs`, v8 ayrıştırıcı/yürütücü ve API çağrı kodları değiştirilmedi. API testi yapılmadı; token/maliyet düşüşü ölçülmedi.

Model isteği hazırlanacağı zaman `prompt.txt` ve `contract.txt` birer kez, ardından mevcut ayrıştırılmış `tableInput` ve bir JPEG gönderilecek. Kullanıcı JPEG/Excel vermeye devam eder; koordinat hazırlamaz. Bu dosyalar yeni model talimatıdır; bu README modele gönderilmez.

## Kabul edilen değişiklikler

- Tek mevcut gövde üzerinde sıralı add/cut/fillet/chamfer. Model ayrı kesici/ara gövde/eskiz özellikleri ve bunların bağlantı grafiğini üretmez. Profil ve kesici işlem içinde yer alır; son gövde sonuçtur.
- Alanlarda doğrudan sayı veya `=A/2-3` gibi ifadeler. Tekrar serbest; yardımcı değişkenler yalnız kolaylık için isteğe bağlıdır. Yerel yorumlayıcı hesaplayacak, model bağımlılık grafiği yazmayacak.
- Aynı profil içinde doğru/yaylarla radyus tarif etme ve gerektiğinde sonradan fillet seçeneklerinin ikisi de korunur. Bu, dışarıdan gelen model tarifini elle düzeltme izni değildir.
- Nominal geometri ve kaynak toleranslar ayrıdır. Koordinat ve kesit seçimini AI yapar; sayısal uygulama yereldedir. Gerçek ölçüyü katıdan ölçüp Excel ile karşılaştırma bu sürüme alınmadı. Bu karar, model yanıtlarının hatasız olduğuna dair bir garanti değildir.

## Alınmayan genişlemeler

25 bin karakterlik dış sözleşme kopyalanmadı. Loft/sweep/shell, ayrıntılı antet hücre tarifi, expected/ölçülen değer karşılaştırması ve otomatik ek API/onarım çağrısı eklenmedi. Betik üretimi kullanılmaz. Genel parça desteğinin kapsamı tanımlı geometrik işlemlerle sınırlıdır; her parçayı ifade etme iddiası yoktur.

## Sonraki emirle yapılacak entegrasyon

V9 ifade dili, isteğe bağlı değişkenler, koşullar ve tek gövde işlem sırası için ayrıştırıcı/yürütücü uyarlanmalı. Özellik ID'leri ayrı gövdeler değil, sıralı işlemlerin kökenini belirtir; ölçü/kesit/kenar referansları buna göre çözümlenmeli. `featureTrace` profil içindeki bir deliğe ayrı ID vermiyorsa o deliğe referans kuramaz; kesitte adı gereken bir deliği ayrı cut işlemi yapmak mümkündür. Bu sürüm kesit izinin yerel algoritmasını düzeltmiş sayılmaz.

Önceden kalan taslak anteti, sayfa düzeni ve gerçek ölçü okları eksikleri bu metinler hazırlanarak giderilmiş sayılmaz. Raporlama/OCCT geçerlilik kontrolleri kaldırılmadı; yalnız yeni gerçek ölçü karşılaştırma sistemi eklenmedi.

Entegrasyona kadar bu sözleşmeyle modele çağrı yapılmamalı: mevcut uygulama v9 yanıtını yürütemez. Taslak3/4 vb. için özel geometrik ipuçları isteme eklenmedi.
