# Ayrıştırılmış Excel denemesi

Excel düzeni ve JPEG değiştirilmedi. `samples/group2/taslak2.xlsx` ile `samples/group2-updated/taslak2guncel.jpg` kullanıldı. Kaynak SHA256 özetleri run-report.json içinde.

## Yapılan düzenleme

- Nominal sayı ve toleranslar ortak yerel ayrıştırıcı ile ayrılır. Toleranslar işaretli üst/alt sapmalardır; geometri yalnızca nominal değer kullanır.
- Ham ölçü hücreleri API'ye gönderilmez. Harf eşleşmeleri korunur. Parça numarası metin, boş hücre blank, gerçek sıfır number/isZero olarak gider.
- 11-30-200 ve 11-30-92 E/F hücreleri blank kalır. 11-30-381 F değeri 0'dır, E çapı 14 mm'dir; yokluk anlamına dönüştürülmez.
- API'ye 4 satırın tamamı ve JPEG gönderilmek üzere tek istek yapıldı. Gerçek metin yükünün Excel bölümü model-input.json dosyasındadır.
- Mevcut v1 tek-ürün ve v2 grup API yolları aynı ayrıştırıcıyı kullanır. Desteklenmeyen ölçü gösterimi tahmin edilmez.

## Sonuç

47 çevrimdışı kontrol geçti. Ayrıca gerçek dört satırlık dosyada boş, sıfır, tolerans ve asimetrik B/G değerleri kontrol edildi. Ancak OpenRouter HTTP 401 Unauthorized döndürdü. Model yanıtı alınamadı: Claude'un yeni biçimi doğru anlayıp anlamadığı bu çalışmada ölçülemedi. Yeni JPEG yok. Sağlayıcı maliyet/usage verisi alınmadı; rapordaki 0 fatura teyidi değildir.

## İnsan müdahalesi

Kod, prompt, testler ve bu notlar asistan tarafından güncellendi. Excel/JPEG veya geometrik ilişkiler değiştirilmedi. Model yanıtı yok, elle tamamlanan plan yok. Kaydedilmiş ilk hata yeni configuration sınıflandırmasına göre yerelde yeniden raporlandı; bunu yapmak için yeni API isteği yapılmadı. Çalışan yazılımda kullanıcıya soru yönelten adım eklenmedi.

## Sonraki adım

Bulut ortamındaki API kimlik doğrulamasını düzeltip aynı verilerle tek analiz çağrısı çalıştırmak. Ardından modelin B/G ilişkisi, F yönü, boş/0 yorumu ve tolerans ayrımını önceki yanıtla karşılaştırmak. Yeni veri formatı mevcut koşullu özellik yürütücüsü ve kademeli kesit eksiklerini tamamlamaz; bu kodlar ayrıca geliştirilmelidir. Bu aşamada farklı modele geçilmedi, kademeli kesit düzleştirilmedi.
