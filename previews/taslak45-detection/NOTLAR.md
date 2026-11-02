# Taslak4.5 — yerel konum testi

Yeni JPEG ve zipteki Excel kullanıldı. Tanıma algoritması değiştirilmeden çalıştırıldı; tespitler elle eklenmedi. API çağrısı yapılmadı. Ürün resmi veya CAD üretilmedi.

## Sonuç

Parantezli 9 Excel etiketi bulundu: A/B/C/D/E/F/G/J/L. Ayrıca [3] ve [R2] bulundu: toplam 11 kayıt. K, Excel'de bulunmakla birlikte JPEG'de bilinçli parantezsiz bırakıldığı için tespit edilmedi; beklenen dışlamadır. Diğer parantezsiz R5/R8/R1,5 yazıları yerleşim etiketi yapılmadı. Çap simgesine dayalı normalizasyon uygulanmadı. Önceki revizyonda G/I/J kaçıyordu; bu örnekte G/J ve I yerine kullanılan L bulundu.

Önizlemede 11 konum görsel kontrol edildi. Ana görünüşte B/C/G/L; kesitte A/D/E/F/J, 3 ve R2. Bu yalnız bu örnekteki başarıdır; her taslak ve açı için hatasızlık garantisi değildir. G'nin OCR güveni yaklaşık 40 olduğundan yerel bir inceleme adayıdır; bütün kayıtlar needs-review durumundadır.

## Açı sınırı

OCR arama açısı yazının gerçek ölçülmüş yönü değildir. Örneğin hafif eğik L, 0 derece arama konumunda yüksek güvenle okunmuş. Konumu doğru bulunsa da yazı yönünün aynen korunması henüz tamamlanmış sayılmaz. Bu ayrımı görünür kılmak için JSON'daki alan ocrRotationDeg olarak adlandırıldı; gerçek metin yönü garantisi taşımıyor. Tanıma davranışı değiştirilmedi, yalnız yanıltıcı alan adı netleştirildi. İleride yönün çizgi/parantez geometrisinden ayrıca çıkarılması gerekiyor.

Ok ucu/uzatma çizgisi eşleştirmesi ve bulunan yerleşimin yeni parçaya aktarılması henüz yapılmadı. Mevcut üretim yerleşimi değiştirilmedi. Görünürlük Excel düzenine girilmedi.
