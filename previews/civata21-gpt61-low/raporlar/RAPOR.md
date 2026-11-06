# GPT-6.1-sol / low — Cıvata2.1

Aynı Excel ve JPEG ile model karşılaştırması. Kodlama dili değişmedi.

## Gönderim ve yerel düzeltmeler

1. Orijinal 7016×4961 JPEG sağlayıcıda 34320 patch ile 30000 sınırını aştı;
   ilk HTTP isteği 400 ile reddedildi, geometri yanıtı yok. Ücret bilgisi bildirilmedi.
2. Oran korunarak 6400×4525 (28400 patch) JPEG kopyasıyla geometri çağrısı yapıldı.
   Model standart any/TypeError/KeyError kullanmış; yürütücü izin listesinde eksikti.
   Genel destek eklendi ve 13 yürütücü testi geçti. Model kodu değiştirilmedi.
3. Kaydedilmiş geometri yanıtı yeni continue-cadquery-group komutuyla tekrar
   kullanıldı; sadece ölçü çağrısı gönderildi. JPEG/Excel SHA256 eşleşmesi zorunlu.
4. Model antetteki H için nominal=null, unresolved açıklaması ve markerId olmadan
   geometrik olmayan kayıt döndürdü. Yazılım bunu ölçü gibi ayrıştırıp durdu.
   Excel ölçüsü, sayısal sabit veya görsel marker olmayan bu tür açıklamalar artık
   ignoredNonmeasurementReferences raporuna ayrılıyor. Gerçek ölçüler gizlenmiyor.
   1 testte 5 senaryo doğrulandı. Aynı yanıtlarla API'siz replay yapıldı.

Toplam 3 HTTP isteği: 1 görsel reddi ve 2 başarılı model yanıtı. Sonraki replay
sıfır API çağrısı kullandı. Otomatik tekrar eklenmedi; müdahaleler açıkça yapıldı.
Son durumda varsayılan Haiku/high ayarına geri dönüldü.

## Sonuç

- 7 STEP ve 7 JPEG üretildi; 7/7 geçerli katı ve yüzey etiketleri kontrolü geçti.
- Bağımsız nominal/R5/1 mm kontrolü 7/7 geçti; geometri önceki hatalı Haiku
  profilindeki geri dönüşlü geçişi içermiyor. Bu bütün tasarım ayrıntılarının tam
  doğruluk kanıtı değildir; konik geçişin belirtilmeyen boyu model tamamlamasıdır.
- dis gösterimi 7 paftada da 2 paralel çizgi ve 2 kesikli uç sınırıyla çizildi.
- Yalnız D ve L ölçüleri yazıldı: her paftada 2 ölçü, toplam 14.
- A/B/C/E model marker konumları OCR ile eşleşmedi; bu ölçüler çizilmedi.
- OCR missingExcelLabels boş: A/B/C/D/E/L harflerinin tamamı okunmuş.
  X konumları yakınken modelin Y konumları sistematik olarak yaklaşık %12 yukarıda.
  Örnek A model y=0,383; OCR y=0,43503. B model 0,273; OCR 0,30961.
  Yazılımda konumlar elle kaydırılmadı veya eşleşme eşiği gevşetilmedi.
- H geometrik olmayan başlık kaydı olarak rapora ayrıldı; çizilmedi.
- Durum sheets-produced-with-unconfirmed-labels, çıkış kodu 2. Bu çıktılar
  eksiksiz ölçülendirme onayı değildir.

## Başarılı iki yanıtın kullanımı

| Çağrı | Input | Görünür output | Reasoning | USD |
|---|---:|---:|---:|---:|
| Geometri | 36.651 | 711 | 219 | 0,100926 |
| Ölçü | 37.549 | 1.060 | 301 | 0,107481 |
| Toplam | 74.200 | 1.771 | 520 | 0,208407 |

Görünür output completion-reasoning farkıdır. İlk reddin kullanım/ücreti yok olarak
varsayılmadı; API bildirmedi. Daha yüksek görsel token kullanımını model/sağlayıcı
hesaplıyor. Ham reasoning metni yayımlanmadı.

geometry-run-report.json ilk başarılı geometri çağrısını; run-report.json son API'siz
replay'i gösterir. usage.json toplam başarılı çağrıları birleştirir. submitted-image.jpg
kullanılan küçültülmüş görseldir. Model yanıtları elle değiştirilmedi.
