# Pleyt — iki çağrıda ortak yön bilgisiyle yeniden deneme

Aynı bospleyt JPEG/Excel dosyaları yedi satırın tamamıyla Haiku 5.5 / high reasoning üzerinden yeniden gönderildi. İkinci çağrıya ilk çağrıdaki yön tanımı aynen eklendi: sol kesitte sayfanın solu +Z, o uç merkez başlangıç, gövde -Z; ana görünüşte sağ +X, yukarı +Y. Başka bir koordinat düzeltme kuralı eklenmedi.

## Sonuç

7 STEP ve 7 JPEG üretildi. PDF yok. Yedi üründe de A, D=R8, E=R5 ve sabit 3 bağlandı; toplam 28 ölçü çizildi. Önceki çalışmada 35 ölçü çözülememişken bu çalışmada yalnız 7 J ölçüsü kaldı. OCR'da teyitsiz etiket yok.

Bu koşuda model eksen ve noktaları dünya Z yönüyle uyumlu döndürdü. Yerel Y/global Z karışıklığı görülmedi. Ancak ilk geometri çağrısı da yeniden çalıştırıldığı için yeni bir geometri kodu üretildi; bu deneme aynı kod sabit tutularak yapılan yalıtılmış bir A/B testi değildir. Önceki ve yeni katıların hacimleri yedi üründe de eşleşti; karşılaştırma geometry-comparison.json içinde. Hacim eşitliği tek başına tüm geometriyi kanıtlamaz.

## J neden kaldı?

Model J için [0,0,0] ve [0,0,-J] noktalarını verdi. Eksen/yön ve nominal uzaklık doğru; ikinci nokta kabın açık ucunun boş merkezinde. Mevcut sözleşme ve yürütücü gerçek gövde sınır noktaları beklediği için "Measurement endpoint is not on final body" kaydı oluştu. Referanslar elle taşınmadı; J kontrol tablosuna alındı. Grup durumu sheets-produced-with-unresolved-measurements, çıkış kodu 2.

## Rekor ZIP

İstenen rekor paketi GitHub'daki previews/rekor-live/rekor-step-jpeg.zip dosyasıdır. Arşiv bütünlüğü kontrol edildi; 24 STEP ve 24 JPEG, rapor ve iki JSON içerir. PDF yok. Önceden doğrulanan montaj yüzeyleri bu STEP'lerde korunur.

## Token ve süre

| Çağrı | Giriş | Görünen çıktı | Reasoning | Toplam çıktı | Süre |
|---|---:|---:|---:|---:|---:|
| geometry | 7768 | 722 | 13647 | 14369 | 70.8 sn |
| measurements | 8805 | 1689 | 11646 | 13335 | 59.0 sn |

API çağrısı: 2. Toplam maliyet bildirimi: $0.0155093. Akış süresi 175.7 sn; aynı JPEG için OCR önbelleği kullanıldı. Model kodu ve ölçü referansları elle değiştirilmedi. Ham reasoning metni veya API anahtarı yayımlanmadı.
