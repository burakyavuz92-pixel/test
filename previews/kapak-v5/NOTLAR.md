# Genel CAD v5 tarifi — kapak analizi

Eski pleyte özgü tarif, prompt ve adaptörler aktif src projesinden çıkarıldı, archive/legacy-v4 altında tutuldu. Eski üretim komutları kaldırıldı; mevcut CLI artık v5 parametre/işlem tarifini kullanır. Tarihsel JPEG'ler korunuyor. Bu değişiklikle genel çizim motorunun tamamlandığı iddia edilmiyor: yeni native katı üretimi, semantik yüz eşlemesi ve teknik pafta yürütücüsü henüz uygulanmadı. Önceki 82 pleyt üretimini bu sürüm doğrudan tekrarlamaz.

## Yeni veri yolu

JPEG + yerelde ayrıştırılmış Excel -> sade teknik yorum/high -> tek recipe.json -> her satır için parametre ve işlem çözümlemesi.

Bir parametre kayıt defteri (Excel/sabit/türetilmiş), referans bazları, CAD operasyonları, bunlara bağlı ölçüler/kesitler/görünüşler var. Geometri kind=revolved-plate gibi aile seçmiyor. Kullanıcı koordinat hazırlamıyor. Closed arithmetic add/subtract/multiply/divide ve unit kontrolü; model kodu çalıştırılmıyor. Bağımlılık sıralaması/döngü, eksik ID, koşullu varlık, girdi sayısı ve temel işlem alanları denetleniyor. Yeşil sourceColor görünürlüğü yerelde kapatılıyor. Bu kontroller native katının doğru oluşacağını kanıtlamaz.

Tarif sözcük dağarcığı sketch/extrude/revolve/cylinder/cut/fuse/hole/circularPattern/linearPattern/fillet/chamfer. Bunlar tanınan tarif işlemleridir; hepsinin yeni OCCT yürütücüsünün hazır olduğu anlamına gelmez. Semantik hedefler henüz gerçek native yüzlere bağlanmadı. Bütün geometrik ilişkileri sayısal kısıt sistemi olarak çözme ve bütün pafta ölçülerini doğrulama da tamamlanmadı.

## Kapak testleri

Aynı kapaktaslak.jpg ve üç satırlık kapaktaslak.xlsx kullanıldı. Eski pleyt şemasına zorlanmadı. İlk API yanıtı 12.000 completion sınırında kesildi; eksik JSON kabul edilmedi ve tamir edilmedi. İkinci ayrı geliştirme denemesinde üst sınır 20.000 yapıldı ve kısa açıklama istendi. Otomatik yeniden değerlendirme döngüsü yok. İki çağrıda da high kullanıldı.

İkinci yanıt tam geldi: 21 parametre, 3 referans bazı, 14 işlem, 9 ölçü kaydı. Geometri tarifi:

1. A dış, D iç çaplı halka profili.
2. F kalınlığında levha oluşturma.
3. Delik çevresi yükselti silindiri ve B hatve çapında dört kopya.
4. Levha/yükseltileri birleştirme.
5. C çapındaki kesici silindiri dört kez çoğaltıp delikleri çıkarma.
6. İki yuvarlak uçlu çentik profilini kalınlık yönünde çıkarıp gövdeden kesme.

B delik daire çapı, C dört delik çapı, D merkez delik, F levha kalınlığı olarak tanındı. Düzlemsellik 0,5 ve yeşil 14/R7/16,5 bilgileri tarifte var. Yeşil kaynaklar yerelde gizleniyor.

## Kontrol gerektiren yorumlar

- Model E'yi levha üzerindeki ek yükselti yüksekliği kabul etti. Kesit uçları E'nin toplam yerel kalınlık olabileceğini gösteriyor; önceki görsel incelemede de bu konu açık bırakılmıştı. Excel E=F=5 iken bu yorum E+F=10 toplam yüksekliğe yol açıyor. Ölçü uçları kesinleştirilmeden doğru üretim tarifi kabul edilmemeli.
- Yükselti dış çapı 21,6 mm tahmin edilmiş, model bunu açık warning ile bildirmiş. Kenar geçişleri modellenmemiş.
- Çentik açıları 45/225°, ikinci çentiğin eş olması ve 16,5 derinliğinin referansı varsayım olarak bildirilmiş.
- Kesici çentik aracının dışarı taşması için kullanılan 10 mm, bir üretim ölçüsü değil modelleme aracına ait varsayım; bu ayrım native yorumlayıcıda açık olmalı.
- B Excel'de çap sembolsüz, JPEG'de ØB. Model bu farkı uyarı yapmış; tek başına yanlış Excel değildir.

Bu varsayımlar kullanıcıyla sohbet bekleyen sorulara dönüşmedi; rapor olarak saklandı. Modelin tanıma başarısı genel yapıda olumlu, bütün üretim ölçülerinde doğru olduğu söylenemez. recipe.json ham yanıtın JSON içeriğiyle aynı; asistan ölçü veya işlem planını elle değiştirmedi.

## Yerel doğrulama düzeltmesi

İkinci çağrıdan sonraki ilk kontrolde 45° eksenleri 0,7071/0,7071 olarak yuvarlandığı için 1e-6 katı birim uzunluk eşiği hata verdi. Kod, 1e-3 içinde birim/dik olan vektörleri normalize edip hesap kaydına basisNormalizationApplied ekleyecek şekilde düzeltildi. Paralel veya bozuk bazlar hâlâ reddediliyor. Aynı yanıt kaynak SHA256 bağıyla yeni API çağrısı yapılmadan tekrar incelendi; üç satır resolved JSON'a dönüştü. Ham model vektörleri değiştirilmedi. Bu yerel biçim/nümerik düzeltme, E yorumunu doğru ilan etmez.

19 güncel C# kontrolü geçti. Eski 77 pleyt testi ayrı arşivdedir; yeni motorun testleriyle toplanıp geçilmiş sayılmaz. Yeni çizim veya STEP üretilmedi. review-report durum recipe-analysis-only; NativeExecutionImplemented=false.

## Maliyet

İlk kesilen çağrı: 14.270 input, 12.000 completion (5.918 reasoning dâhil), 0,148540 USD.
Tam yanıt çağrısı: 14.324 input, 11.948 completion (6.281 reasoning dâhil), 0,148128 USD.
Toplam 0,296668 USD. Cache okuma/yazma 0. Reasoning completion'a dâhil; yeniden toplanmaz. 20.000 üst sınırdır, ikinci çağrı 11.948 kullandı. Geniş işlem tarifi önceki pleyt tarifinden uzundur; daha düşük token ve tutarlılık optimizasyonu için yeni ölçüm gerekir. Tek tarif üç satırda yerelde çözüldü; satır başına API çağrısı yok.

## Sonraki adım

Önce E/F uç ilişkisini ve ölçüsüz detayların kabul edilebilir temsilini netleştirip yeni sözleşmenin bu ölçüyü doğru bağlamasını sağlamalıyız. Ardından bu 14 operasyonun yerel katı oluşturma ve ölçü bağlama karşılıklarını yazıp native doğrulama yapabiliriz. Sonrasında eski pleytleri de aynı genel dil üzerinden yeniden sınamak gerekir. Mevcut aşama tarif çıkarma/çözümleme; genel CAD çizicinin tamamı değildir.
