# Taslak7 — uçtan uca çalışma

23 ürünün tamamı Haiku 5.5 / high reasoning ile gönderildi. İki gerçek API çağrısı yapıldı; yerel tekrar çalıştırmada yeni API çağrısı yok. Geometri kodu ve model etiketleri elle değiştirilmedi.

## Sonuç

- 21 üründe STEP, antetli JPEG ve mevcut görüntü tabanlı PDF üretildi. Bunlar inceleme çıktılarıdır; tüm ölçüler tamamlanmış değildir.
- 733035 ve 733035-1: L=20 mm ile taslaktaki sabit Ø22 uyuşmuyor. Model kısa hata nedeni döndürdü. Bu girdiler ve geometri değiştirilmedi, bu ürünler için dosya üretilmedi.
- 21 STEP yeniden okunabildi; tek geçerli katı ve C+2,8+5 toplam eksenel boy doğrulandı. @montaj etiketi gerçek düzlemde yazıldı ve yeniden okunarak kontrol edildi. Bunlar tüm tasarım ayrıntılarının doğrulandığı anlamına gelmez.
- 733001 STEP içinde Ø25 düz bant z=-39,8…-38,8 arasında 1 mm: bu kez geniş uçta. Önceki taslak6.6 yorum hatası burada oluşmadı.

## Açık kalan ölçülendirme sorunları

1. F ve L OCR tarafından yakalanmadı. Parantezsiz K'nin çizilmemesi beklenen davranış.
2. OCR'deki `5` adayı gerçek [5] konumunda değil; G bölgesindeki farklı bir okuma. Modelin doğru yerdeki 5 işaretiyle eşleşmedi. 5 ölçüsü paftaya alınmadı.
3. Model ana görünüşteki L'yi E olarak etiketledi ve E çapına referans verdi. Bu referans elle L'ye çevrilmedi; görsel kanıt bulunmadığı için çizilmedi. Geometri fonksiyonu L değerini kullanıyor.
4. Bu sebeplerle normal satırlarda 11 yerine 8 ölçü yerleşti. G=0 olan iki satırda 7; D=0 olan 733001-03'te 6 ölçü yerleşti.
5. 733001-03 için model B'yi "D sıfır, B çapı geometride yok" diyerek unresolved döndürdü. D=0 ölçüsü çizilmedi. Bu ürünün ölçü bağlaması ayrıca incelenmelidir.

## Çalışma sırasında giderilen yazılım sorunları

- 8 örnek satır sınırı mevcut uçtan uca komuttan kaldırıldı; 23 nominal satırın tamamının model-input.json içinde olduğu doğrulandı. Sunum metni ve toleranslar yine API girdisine dahil edilmedi.
- Modelin kısa nedenini oluşturmak için kullandığı saf Python format() fonksiyonu yürütücüde eksikti. Destek ve regresyon testi eklendi; nihai iki hata artık modelin Türkçe nedeni olarak gösteriliyor.
- Aynı Excel etiketi ikinci kez geldiğinde sayısal sabit sanılıp tüm pafta üretimi duruyordu. Her etiket oluşumuna bağımsız referans, aynı Excel değeri/toleransı/sunum metni sağlayan genel düzeltme eklendi. Bu düzeltme modelin L/E yorumunu değiştirmez.
- API çağrılarının gerçek süreleri ve toplam akış süresi kaydediliyor.

İlk denemenin ve düzeltme sonrası tekrarın raporları ayrı klasörlerde korunur. Tam reasoning metni ve API anahtarı bu çıktı paketine dahil değildir.

## Token ve süre

| Çağrı | Giriş | Görünen çıktı | Reasoning | Toplam çıktı | Süre |
|---|---:|---:|---:|---:|---:|
| geometry | 19796 | 2141 | 26710 | 28851 | 130.4 s |
| measurements | 21799 | 5369 | 27394 | 32763 | 135.0 s |

API toplam maliyet bildirimi: $0.0349665. İlk akış: 327.4 saniye. Yerel tekrar: 97.9 saniye. Çıktı sınırı her çağrı için ayrı 65.536 token; en büyük gerçek kullanım 32.763 token.

Reasoning toplam çıktı sayısına dahildir. Sonuçlar taslak6.6'ya göre giriş büyümesinin belirgin olduğunu, reasoning'in ise satır sayısıyla doğrusal büyümediğini gösterir; gelecekteki işler için garanti değildir.

Doğrulama: .NET derleme, 7 yürütücü testi, 5 ürün hata testi, 5 pafta testi ve 14 yerleşim testi.
