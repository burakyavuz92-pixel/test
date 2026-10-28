# Kısa talimatlar ve ölçü yazısı çakışma kontrolü

Ham girdiler aynı taslak2guncel.xlsx ve taslak2guncel.jpg. Geometri/annotation Excel yükleri ayrı kaldı; nominal/tolerans ayrımı ve kaynak veriler değiştirilmedi.

## Kod değişikliği

Tekrarlanan talimatlar CadAnalysisPrompt içinde birleştirildi. Modelin açıklamalarına kısa kanıt önerisi getirildi; gerçek sorunların açıklamaları korunuyor. Aynı bağlantıyı üç bölümde veren mevcut şema bu görevde yeniden tasarlanmadı. Orijin, renk ve boş/sıfır sözleşmeleri korundu.

Arial glyph'lerinin gerçek ink sınırları ölçülüyor. Nominal, çap, parantez ve üst/alt tolerans birlikte, döndürülmüş bir zarfla temsil ediliyor. Bütün görünüş kenarları, eksen/ölçü çizgileri, sabit yazılar ve önce yerleşen etiketlere karşı kontrol yapılıyor. Yazı çevresinde 3 pafta-birimi boşluk bırakılıyor. Lider için farklı açılar, uzunluklar ve normal uzaklıklar; diğer ölçü yazıları için çizgiye dik alternatifler deneniyor. Yerleşim bulunamazsa hata raporlanıyor; yazı küçültülmüyor, değer değiştirilmiyor. Asimetrik tolerans parantez genişliği de gerçek metin genişliğinden hesaplanıyor.

Bu yöntem ürüne özel 381 koordinatı içermez. Ancak pafta bölgeleri önceki yerleşim profilinden geliyor; genel şablon tanıma değildir. Ayrıca açgözlü aday seçimi yapıyor, bütün lider çizgilerinin birbirini kesmesini küresel olarak optimize etmiyor. Liderin başka bir ölçü çizgisini kesmesi mümkün; yazı zarfının çizgilerle çakışması engelleniyor. Ölçü etiketleri için kontrol var; bütün pafta metinlerini yeniden yerleştiren genel bir motor değil.

## Denemeler ve müdahaleler

İlk geliştirme çağrısında model geometri ilişkilerini doğru döndürdü fakat kısaltılmış şemadaki hideIf:condition belirsizliği nedeniyle kind yerine type alanı yazdı. Bu yanıt değiştirilmedi, reddedildi. Promptun JSON örneği açık kind alanıyla düzeltildi. Ayrıca body merkezi ile origin açıkça aynı nokta beyan edildiğinde bunları farklı kaynak uçları sayan doğrulayıcı yanlış alarmı düzeltildi. Bu eşdeğerlik yalnızca açık sıfır ankrajlı body-axis origin için geçerli; başka datum otomatik eşitlenmiyor. İki değişiklik de geneldir, B/F/G için doğru cevap yazılmaz.

Sonra ikinci, ayrı bir geliştirme çağrısı yapıldı. Uygulamaya otomatik yeniden değerlendirme eklenmedi. Son çalışma bir API çağrısında model yanıtını değiştirmeden dört JPEG üretti. Kod güncellemeleri iki çalışma arasında asistan tarafından yapıldı; bunu bütün geliştirme boyunca müdahalesiz başarı diye adlandırmıyoruz. Son run-report.json içindeki AssistantAnswersUsed=false, o çalışmada planın değiştirilmediğini ifade ediyor.

Önceki kayıtlı 381 isteğiyle yerel yerleşim denemesi de yapıldı; API çağrısı yoktu. Yayımlanan dört JPEG son yeni API çalışmasının çıktılarıdır.

## Çıktılar

- [11-30-381](11-30-381.jpeg): orta delik Ø14 ve toleransı 70 ölçü çizgisinden uzaklaştırıldı.
- [11-30-212](11-30-212.jpeg)
- [11-30-200](11-30-200.jpeg)
- [11-30-92](11-30-92.jpeg)

Dört pafta açılıp incelendi. Delik konumları, katı BRep/tek katı/hacim/STEP kontrolleri geçti. Ölçü yerleşim adayları drawing-checks.json içinde. Kullanıcı teknik kullanım onayı hâlâ gerekiyor.

71 C# kontrolü, 10 OCCT geometri/kesit testi ve 5 çakışma algoritması testi geçti. 381 ve 212'de orta/yan deliğin etiketi alternatif adayla yerleştirildi. Genel çakışma çözümü her türlü taslakta başarı garantisi değildir.

## Token, maliyet ve cache

| Çalışma | Girdi token | Çıktı token | Maliyet USD | Cache okunan token |
|---|---:|---:|---:|---:|
| Önceki başarılı | 16407 | 2551 | 0,058324 | 0 |
| İlk geliştirme (reddedildi) | 15172 | 2006 | 0,050404 | 0 |
| Yeni başarılı | 15234 | 1892 | 0,049388 | 0 |

Yeni başarılı çağrı, önceki başarılı çağrıya göre girdide yaklaşık %7,1, çıktıda %25,8 ve maliyette %15,3 azalma gösterdi. Toplam prompt metni 16.378 karakterden 12.723 karaktere indi; iki tam görüntü ve iki ayrı Excel yükü korundu. Görsel token payı sağlayıcı tarafından ayrı güvenilir biçimde verilmedi. Çıktı uzunluğu model cevabına göre değişir; bu oranlar her çağrı için garanti değildir.

Bu görevdeki iki geliştirme çağrısının toplam maliyeti 0,099792 USD. Son normal üretim çağrısı 0,049388 USD. Yerel yeniden çizim ücretli API çağrısı değildir.

Sağlayıcı kimi koşullarda prompt cache indirimi uygulayabilir. Gözlenen bu üç kayıtta cached_tokens ve cache_write_tokens sıfır: fiyat farkı gözlenen cache indiriminden kaynaklanmıyor. Gelecekte cache olduğunda faturadaki gerçek maliyet doğru kalır; bunu her yeni grubun indirimsiz maliyeti sanmak bütçe tahminini düşük gösterebilir. Bu nedenle tokenlar ve cache bilgisiyle birlikte karşılaştırılmalı. Sağlayıcının otomatik cache davranışı veya gelecekteki fiyatları bu denemede garanti edilmez.
