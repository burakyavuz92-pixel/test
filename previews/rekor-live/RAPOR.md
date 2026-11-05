# Rekor — otomatik akış değerlendirmesi

## İstenen çıktı değişiklikleri

PDF üretimi kaldırıldı. Ürün dosyaları STEP ve JPEG; son çıktı ağacında PDF sayısı 0. "Ana görünüş" alt yazısı kaldırıldı, kesit adı korunuyor. Eski arşivlerdeki PDF'ler tarihsel çıktı olarak duruyor; yeniden üretilmedi.

## Sonuç

24 satırın tamamı Haiku 5.5 / high reasoning ile gönderildi. Son standart `run-cadquery-group` komutunda 24 ürünün STEP ve JPEG'i oluştu. Girdiler, modelin ürettiği geometri kodu ve ölçü referansları elle değiştirilmedi. JPEG/Excel özetleri iki denemede de aynı.

- 24 STEP yeniden okunabildi, her birinde tek geçerli katı ve C+M+5 eksenel boy doğrulandı. Montaj yüzeyi etiketleri gerçek yüzlerde yeniden okunarak kontrol edildi. Bu kontroller tüm tasarım yorumunun doğrulandığı anlamına gelmez.
- 23 paftada çözülemeyen ölçü yok. Bunların 20'sinde 12 ölçü; G=0 olan üç satırda 11 ölçü yerleşti. Sıfır ölçüler genel kurala göre çizilmedi.
- 733001-03'te D=0 için model B'yi "D=0 olduğundan B deliği yok" diyerek unresolved döndürdü. D çizilmedi, B kontrol tablosuna alındı; 10 ölçü yerleşti. Geometri ve JPEG yine üretildi. B elle başka bir silindire bağlanmadı.
- `[ 5 ]` yazımı OCR'da gerçek konumunda bulundu ve bütün paftalarda 5 ölçüsü yerleşti. Görsel kanıtla eşleşmeyen model etiketi kalmadı. OCR algoritmasına bu çalışma için özel düzeltme eklenmedi.
- "completed" ürün durumu dosyaların oluşturulduğunu ifade eder. Son grup durumu tek B referansı nedeniyle `sheets-produced-with-unresolved-measurements`, çıkış kodu 2.

## İlk deneme ve uyumluluk düzeltmesi

İlk otomatik çalışma başarılı olmadı. Model, hata nedenleri için `class _RowError(Exception): pass` üretti; yürütücü sınıf tanımlarını kabul etmediği için ortak geometri aşamasında durdu. Sorun JPEG/Excel veya OpenRouter erişimi değildi. İlk hata raporu first-attempt klasöründe korunuyor.

Yürütücüye yalnız boş Exception/ValueError/RuntimeError alt sınıfları ve str() desteği eklendi. Sınıf yöntemleri, çalışan sınıf gövdesi, özel metaclass ve doğrudan class-builder erişimi kabul edilmiyor. İlgili sözleşme cümlesi bu destekle tutarlı hale getirildi.

Genel düzeltme sonrası aynı girdiler yeniden standart komutla gönderildi. Bu son koşuda araya girip model kodu, koordinat veya referans düzeltilmedi. İlk modelin değiştirilmemiş kodu da yeni yükleyicide ayrı, API çağrısız doğrulama testinde 24/24 geçerli katı oluşturdu; original-script-compatibility-check.json bu sonucu içeriyor.

Testler: 9 pafta motoru testi, 10 betik yükleyici testi, 7 ürün hata testi — toplam 26 test geçti. Son canlı çalışmada 24 STEP/JPEG çifti, sıfır PDF ve alt yazının kalktığı ayrıca kontrol edildi.

## Müdahalesiz kullanım değerlendirmesi

İlk sürüm bu denemeyi tek seferde geçemedi; bu nedenle ilk denemeye "müdahalesiz başarılı" denmiyor. Genel uyumluluk düzeltmesinden sonraki sürümde dosya üretimi tek komutla tamamlandı ve inceleme gerektiren B ölçüsü otomatik raporlandı. Bu örnek otomatik üretim hattını doğruluyor; D=0 için B'nin gösterim anlamı açık kalan model yorumu. Tüm yeni taslaklarda bütün geometrinin koşulsuz doğru çıkacağı doğrulanmış değildir.

## Token ve süre

| Çağrı | Giriş | Görünen çıktı | Reasoning | Toplam çıktı | Süre |
|---|---:|---:|---:|---:|---:|
| İlk deneme: geometri | 23080 | 1972 | 31279 | 33251 | 149.5 sn |
| Son koşu: geometri | 23104 | 1786 | 27655 | 29441 | 130.5 sn |
| Son koşu: ölçüler | 24914 | 3245 | 31458 | 34703 | 145.6 sn |

Toplam API çağrısı: 3 (ilk başarısız denemede 1, son koşuda 2). Toplam maliyet bildirimi: $0.0558073; yalnız son koşu: $0.0368738. Son koşu toplam süresi 394.4 sn. Reasoning toplam çıktı sayısına dahildir. Ham reasoning metni ve API anahtarı yayımlanmıyor.
