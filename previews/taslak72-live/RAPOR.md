# Taslak7.2 Excel + Taslak7.1 JPEG — çalışma sonucu

Güncel Excel, kullanıcının istediği önceki JPEG ile gönderildi. JPEG SHA-256 önceki çalışmayla aynı; 29 nominal satırın tamamı API girdisine dahil. Haiku 5.5 / high reasoning ile iki yeni API çağrısı yapıldı. Girdiler, promptlar, yazılım ve modelin ürettiği kodlar elle değiştirilmedi.

## Sonuç

- 24 ürünün STEP, antetli JPEG ve mevcut görüntü tabanlı PDF dosyaları üretildi. STEP'ler tek geçerli katı, beklenen C+M+5 eksenel boy ve montaj yüzeyi etiketi yeniden okuma kontrollerinden geçti. Bunlar tam tasarım doğruluğu garantisi değildir.
- Düzeltilen J açılarıyla 733008 ve 733019 artık üretildi.
- 733032, 733032-01, 733034, 733034-01, 733099 için model: "Koni uç çapı sıfır, geçerli koni oluşmuyor" nedeni döndürdü. Bu ürünler için dosya üretilmedi.
- Model N=0'ı ölçü görünürlüğü olarak yorumlamadı; N'yi A'ya eşitlemedi. Geometri fonksiyonunda N<=0 kontrolü kısa hata döndürüyor. Bu kayıtta modelin davranışı raporlanıyor; sıfırın farklı bir tasarım anlamına geldiğini varsayan kural yazılıma eklenmedi.

## Ölçülendirme

- Normal satırlarda 12 ölçünün 11'i yerleşti. Aynı JPEG kullanıldığı için önceki OCR önbelleği tekrar kullanıldı. F ve L yakalanıyor; sabit 5 için gerçek konumda OCR eşleşmesi hâlâ yok. Yanlış konumdaki 5 okuması kullanılmadı. Bütün paftalar bu sebeple inceleme durumundadır.
- G=0 ölçüleri çizilmedi; bu üç satırda 10 ölçü yerleşti.
- 733001-03'te model B'yi "D=0 olduğundan karşı delik yok" gerekçesiyle unresolved döndürdü. D=0 çizilmedi; 9 ölçü yerleşti ve B kontrol tablosuna alındı. B başka bir yüzeye elle bağlanmadı.
- Önceki yardımcı fonksiyon paylaşımı düzeltmesi bu çağrıda çalıştı. Ölçü kodu _params ve build_part gibi geometri fonksiyonlarını kullanabildi. Ölçü fonksiyonu katıyı bellekte tekrar oluşturuyor; kayıtlı STEP'i değiştirmiyor.

## Excel değişiklikleri

Önceki Excel'e göre sekiz geometri parametresi değişti: 733008 J açısı 55→35, 733019 J açısı 55→35, 733032-01 F bacağı 2→1,5; son beş ürünün N değeri 20→0. Ayrıntılar input-changes.json içinde.

## Token ve süre

| Çağrı | Giriş | Görünen çıktı | Reasoning | Toplam çıktı | Süre |
|---|---:|---:|---:|---:|---:|
| geometry | 26687 | 3339 | 31632 | 34971 | 152.6 sn |
| measurements | 28821 | 3954 | 35783 | 39737 | 159.2 sn |

Toplam akış: 410.3 sn. API maliyet bildirimi: $0.0429048. Her iki yanıt stop ile tamamlandı. Reasoning toplam çıktıya dahildir; çağrı başına 65.536 token ve 600 saniye sınırına takılınmadı. Yeni API çağrısı sayısı 2; otomatik/manuel tekrar çağrısı yapılmadı. Ham reasoning metni ve API anahtarı pakete dahil değildir.
