# İkinci çağrı sözleşmesi — bütünlüklü düzenleme ve karşılaştırma

Mevcut geometri, OCR, ölçü bağlama ve yerleşim kodu değiştirilmedi. İkinci çağrı sözleşmesi tek parça düzenlendi. Görünüş bilgisinin her ölçüde tekrarı korundu. İlk çağrıdaki yön tarifi korundu; bununla çelişebilen yatay/dikey kesit cümlesi kaldırıldı. Doğrusal ölçülerin gerçek yüzey/kenar noktalarından seçilmesi ve ölçü yönündeki izdüşüm uzaklığının nominal olması açıklandı. Pah yalnız chamfer olarak tarif ediliyor. Kimlik/marker bağlantıları ve bilinmeyen referans davranışı aynı tanımda toplandı.

## Yerel kontroller

5 pafta testi ve 7 ürün hata testi geçti. Bu testler metnin doğruluğunu tek başına garanti etmez. Çalıştırıcının Python izin listesi bu turda değiştirilmedi; incelemede bulunan all() gibi ayrı yürütücü kapsam eksikleri bu değişiklikle çözülmüş sayılmaz.

## İlk iki denemede yakalanan eksiklik

İlk metin görünüş kutusunun eleman sırasını yeterince açık söylemedi; iki model de [x,y,width,height] biçimini kullandı, yürütücü [left,top,right,bottom] beklediği için pafta aşaması durdu. Bu düzenlemedeki eksiklik açıkça kaydediliyor. Alan minX,minY,maxX,maxY olarak netleştirildi ve aynı girdiler yeniden standart komutlarla gönderildi. Yanıtlar elle çevrilmedi.

## Son koşular

- Pleyt: 7 STEP/JPEG çifti, her üründe 5/5 ölçü; J dahil toplam 35 ölçü yerleşti. Çözülemeyen veya OCR'da teyitsiz ölçü yok. Model J için gerçek gövde yüzeyinde uç noktası seçti.
- Rekor: 24 STEP/JPEG çifti. 23 paftada çözülemeyen ölçü yok. 733001-03'te B, modelin "Derinlik sıfır; B için ayrı cep yok" yorumu nedeniyle unresolved kaldı. D=0 ve G=0 ölçüleri önceki kuralla çizilmedi. Yeni OCR belirsizliği yok.
- Modelin geometri kodları, ölçü yanıtları ve girdiler elle değiştirilmedi. Düzlem referansı veya parçaya özel bağlama kuralı eklenmedi. PDF üretilmedi.

## Çağrılar ve maliyet

Toplam 8 gerçek API çağrısı yapıldı: ilk iki denemede 4, son iki koşuda 4. İlk başarısız denemeler ayrı klasörlerde korunur; buradaki JPEG'ler pafta aşaması başarısız olduğundan geometri önizlemesi olabilir. Kullanılacak son dosyalar -final klasörlerindedir.

| Koşu | Çağrı | Giriş | Görünen çıktı | Reasoning |
|---|---|---:|---:|---:|
| pleyt-contract-review | geometry | 7768 | 896 | 16801 |
| pleyt-contract-review | measurements | 9114 | 1524 | 16659 |
| rekor-contract-review | geometry | 26272 | 1692 | 28743 |
| rekor-contract-review | measurements | 28180 | 3362 | 26953 |
| pleyt-contract-final | geometry | 7768 | 1003 | 17050 |
| pleyt-contract-final | measurements | 9250 | 1637 | 16335 |
| rekor-contract-final | geometry | 26272 | 1722 | 26129 |
| rekor-contract-final | measurements | 28303 | 4430 | 33333 |

Tüm denemelerin toplam maliyet bildirimi: $0.1134272. Ham reasoning metinleri ve API anahtarı pakete dahil değildir. Tek başarılı koşu gelecek bütün taslaklar için garanti değildir; bu karşılaştırma mevcut pleyt ve rekor örneklerini kapsar.
