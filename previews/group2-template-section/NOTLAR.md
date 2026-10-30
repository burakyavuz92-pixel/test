# Taslaktaki kesiti esas alan kısa prompt — deneme

Merkezden düz kesit zorunluluğu kaldırıldı. Kesit talimatı: taslakta gösterilen kesiti üret, izini parça özellikleri/satır ölçüleriyle ilişkilendir. Sözleşmede kısa planar nokta-normal ve stepped kaynak görünüş/iki boyutlu iz formatları bulunuyor. Yeni kesit seçme algoritması veya ürüne özel kural eklenmedi. Mevcut yerel okuyucu iki biçimi de destekliyor.

55 kontrol geçti. Aynı notsuz yerel JPEG ve taslak2guncel.xlsx dosyaları yazılıma verildi. Önceki merkezi kesit denemesiyle run-report Source özetleri aynı. Kullanıcının son mesajındaki iki JPEG ifadesi önceki akışa göre JPEG+Excel olarak yorumlandı ve önceden açıklandı. Tek görüntü/tek tablo, high, tek API çağrısı. Çizim/STEP yok. Asistan geometri eklemedi veya gelen tarifi değiştirmedi. Ham özel akıl yürütme yayımlanmadı.

## Sonuç

Yanıt tamamlandı ve yalnız veri döndü. Birim ve ana geometri bağımlılık kontrolleri geçti; kesit çözümlemesi nedeniyle çalışma `blocked-with-report` durumunda durdu. Grup geçmediği için satır JSON dosyaları dışa aktarılmadı. Model yanıtı recipe.json içinde korunuyor.

- Geometri: üst delik y=B−G, alt delik y=−G, üçüncü delik x=−F. E boşsa geometri deliği atlıyor. F=0 ve E dolu ise geometri deliği korunuyor. Dünya +Z ana görünüşünden bakılıyor, böylece −F ekranda sola düşüyor. Sac3, derinlik33, dışR8 ve yaklaşık içR5 profili Z ekseni etrafında döndürülüyor. Geometrinin native üretimi yapılmadı.
- Kesit: kaynak görünüş front, kamera+Z; iz ana eksenden başlayıp y=+20'de x=−F'ye kademeleniyor, y=−20'de ana eksene dönüp çıkıyor. Üst/alt sınırlar A/2+10. Yolu yazılım görünüş derinliği Z boyunca süpürüyor. Kesit görünüşü +X.
- **11-30-212:** F44.5 olduğundan iz üçüncü delik merkezinden geçiyor. Geçişler ±20'de; üst/alt delikler ±44.45'te olduğundan bu üç delik kesitte yer alabilir. Bu satır kesit çözümlemesinde hata vermedi.
- **11-30-200 ve11-30-92:** E/F boş. Geometride delik atlanıyor ama kesit yolu xE=−F boş parametresini hâlâ kullanıyor. Yazılım bunu sıfıra dönüştürmüyor, doğru biçimde boş parametre hatasıyla duruyor.
- **11-30-381:** E dolu, F0. Kesit yolunda yan yana aynı iki nokta oluşuyor. Sıfır uzunluklu segmentin çapraz çarpımı sıfır olduğundan normal hesaplanamıyor; yerel doğrulayıcı reddediyor. Bu, gerçek deliğin kaybolması değil, kesit yolunun sadeleşmemesi sorunu.

## Kullanım

|Metrik|Merkezden düz kesit|Taslak kesiti|
|---|---:|---:|
|Giriş|9392|9543|
|Akıl yürütme|4667|7628|
|Görünür çıktı|2951|3347|
|Toplam çıktı|7618|10975|
|Maliyet USD|0.094964|0.128836|

Cache0. Tek deneme nedensel kanıt değil. Genel taslak kesitine dönünce bu denemede akıl yürütme yaklaşık%63 arttı; yalnız düz kesit denemesindeki ucuzluğun bütün parçalara aktarılacağı söylenemez. Kesite ait tokenlar ayrı ölçülemiyor.

## Sonraki değerlendirme

Sıfırla üst üste gelen iz noktalarını geometrik olarak normalleştirmek genel bir yazılım işlemi olabilir. Boş parametreleri otomatik0 yapmak uygun değil. Boş özelliğe bağlı kesit yolunu ifade etmek için isteğe bağlı özellik referansları veya koşullu kesit alternatifleri gibi genel bir sözleşme çözümü gerekir; mevcut kesit biçiminde bu açıkça tanımlı değil. Bu ayrımı sırf modelin parçayı anlayamaması olarak değerlendirmemeliyiz. Bu denemede yeni uyarı/döngü, manuel tarif tamiri veya ikinci API çağrısı yapılmadı.
