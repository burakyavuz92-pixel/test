# Boş pleyt — çalışma sonucu

Yedi satırın tamamı Haiku 5.5 / high reasoning ile gönderildi. Bu deneme ölçülendirme açısından başarılı değildir; STEP/JPEG dosyalarının oluşması tam bir çizim başarısı olarak değerlendirilmemelidir.

## Sonuç

- 7 STEP ve 7 antetli JPEG üretildi. PDF üretilmedi; Ana görünüş alt yazısı yok.
- STEP'lerde tek geçerli katı, Excel'deki A çapı ve J derinliği, R8 dış radyus, R5 iç radyus ve silindirler arasında 3 mm duvar geometrisi kontrol edildi. Geometri denetiminin kapsamı geometry-review.json içinde; bu, tüm tasarım yorumlarının onaylandığı anlamına gelmez.
- JPEG'de @montaj etiketi bulunmadığı için model yüzey etiketi listesi boş; uydurma montaj etiketi eklenmedi.
- OCR A, D, E, J ve sabit 3 işaretlerini gerçek konumlarında doğruladı. Eksik/teyitsiz model işareti yok.
- Buna rağmen 7 paftanın hiçbirinde ölçü çizgileri bağlanamadı: her üründe 5, toplam 35 çözülemeyen ölçü var. Değerler kontrol tablosunda gösterildi. Grup durumu sheets-produced-with-unresolved-measurements, çıkış kodu 2.

## Ölçü bağlamasının nedeni

Geometri gerçek STEP içinde Z ekseninde. Örneğin 11-20-107 sınırları X/Y=-53,5…53,5, Z=-34…0; dış silindir yarıçapı 53,5 ve ekseni Z. Ölçü yanıtında model A referansı için [0,1,0] ekseni ve [0,-21,0] merkezi döndürmüş. Yani referanslar Y eksenindeki bir katı için tarif edilmiş. D/E radyusları ile J ve 3 uç noktaları da aynı koordinat karışıklığını içeriyor.

Yazılım bu referansları gerçek yüzeylerle eşleştiremedi ve çizmedi. A için "No matching cylinder or full circular edge at the specified reference", diğer dört ölçü için "Measurement endpoint is not on final body" kaydı oluştu. Bu sorun OCR hatası veya R yazısının basılması değildir. Modelin ikinci yanıtındaki koordinat uyumsuzluğudur. Y→Z elle dönüşüm uygulanmadı, model kodu ve referanslar değiştirilmedi, düzeltme için ek API çağrısı yapılmadı.

## Girdi ayrıştırma desteği

İlk kontrol API çağrısından önce D=R8 hücresinde durdu; ayrıştırıcı R önekini henüz sayısal kabul etmiyordu. Radyus için genel R/r öneki desteği eklendi. R8/R5 sayısal 8/5 olarak ve radiusSymbol=true bilgisiyle modele aktarılıyor; Excel değiştirilmedi. Sunumda R korunuyor, METIN ile özel metin varsa mevcut bastırma davranışı korunuyor. Ondalık virgül, boşluk ve mevcut tolerans biçimleri destekleniyor. Bu destek belirli ürün/etiket adına bağlı değildir.

Kontroller: gerçek yedi satır üzerinden 52 radyus kontrolü; önceki çalışma kitabı üzerinde 77 Excel sunum kontrolü; 4 görünüş/sunum ve 5 pafta testi. Radyus bilgisi API girdisinde doğrulandı. İlk girdi hatası initial-input-check klasöründe korunur.

## Akış değerlendirmesi

Genel R ayrıştırma eksikliği giderildikten sonra standart komut iki API çağrısı, STEP üretimi, OCR ve paftaları tamamladı. Geometri kodu elle düzeltilmedi. Ölçü aşaması hatalı koordinatları yakaladı; bu örnek otomatik ölçülendirmenin henüz güvenilir biçimde tamamlanmadığını gösteriyor. Modelin geometri kodundaki özel çalışma düzlemini ikinci çağrıda global Y olarak yorumlaması ana bulgu. Gerçek STEP koordinat bilgisiyle ölçü yanıtını temellendirmek sonraki iyileştirme için değerlendirilmelidir.

## Token ve süre

| Çağrı | Giriş | Görünen çıktı | Reasoning | Toplam çıktı | Süre |
|---|---:|---:|---:|---:|---:|
| geometry | 7768 | 597 | 13684 | 14281 | 70.0 sn |
| measurements | 8670 | 1603 | 19213 | 20816 | 94.2 sn |

API çağrısı: 2. Maliyet bildirimi: $0.0191923. Standart akış süresi 665.2 sn. Bu incelemede ayrı bir ön OCR taraması da çalıştırıldı; ana akış OCR'a girdiğinde önbellek henüz hazır olmadığı için ana akış ayrıca kendi OCR taramasını yaptı. Token/süre sınırına takılınmadı. Reasoning toplam çıktıya dahildir. Ham reasoning metni ve API anahtarı yayımlanmadı.
