# Taslak7.1 — uçtan uca çalışma

29 satırın tamamı Haiku 5.5 / high reasoning ile gönderildi. İki gerçek API çağrısı yapıldı. Excel, JPEG ve modelin geometri/ölçü kodları değiştirilmedi.

## Sonuç

- 26 üründe STEP, antetli JPEG ve mevcut görüntü tabanlı PDF üretildi. Bunlar inceleme çıktılarıdır.
- 733008, 733019 ve 733032-01: model "Sol yüzde pahlar çakışıyor" nedenini döndürdü. Ölçüler düzeltilmedi, bu üç üründe STEP üretilmedi. Modelin pah hesabında sol uçta kalan radyal et sırasıyla -0,2126 / -0,3922 / -0,3000 mm; ayrıntılar failure-review.json içinde.
- 26 STEP tek geçerli katı olarak yeniden okunabildi; C+M+5 eksenel boy kontrol edildi. @montaj etiketi gerçek düzlemde yazıldı ve yeniden okunarak doğrulandı. Bu kontroller tüm tasarım yorumunun doğrulandığı anlamına gelmez.
- Önceki taslakta L=20 / sabit Ø22 sebebiyle başarısız olan 733035 ve 733035-1, bu girdide N=16 verildiği için üretildi. Yazılım eski tutarsızlığı kendiliğinden düzeltmedi.
- M=0 ve D=0 satırları da modelin kendi dallarıyla işlendi. Nominal sıfır ölçüler mevcut genel kurala göre çizilmedi.

## Ölçülendirme incelemesi

- F ve L OCR'da doğru konumlarında bulundu. Model de L'yi L olarak döndürdü; önceki L/E karışıklığı bu çağrıda yok.
- M ve N yeni Excel ölçüleri olarak işlendi.
- Normal satırlarda 12 ölçünün 11'i yerleşti. Sabit [5] gerçek konumunda OCR ile eşleşmedi; G bölgesindeki farklı 5 okuması gerçek ölçünün yerine kullanılmadı. Bütün paftalarda bu etiket için inceleme durumu korunur.
- G=0 olan satırlarda G çizilmedi.
- 733001-03 için model B referansını "Sayaç derinliği sıfır" diyerek unresolved bıraktı. D=0 ölçüsü çizilmedi.
- 733032, 733034, 733034-01, 733099 için model B'yi "Sayaç derinliği sıfır", E'yi "Boyun yok (M=0)" diyerek unresolved bıraktı. D ve M sıfır olduğu için çizilmedi. Bu satırlarda eksik referanslar kontrol tablosunda görülebilir; başka bir yüzeye elle bağlanmadı.

## Yürütücü bağlantı düzeltmesi

Ölçü yanıtı, geometri kodunda tanımlı _dims() ve _f() yardımcılarını tekrar yazmadan çağırdı. İlk çalışmada ölçü kodu ayrı yüklendiği için _dims bulunamadı. Yürütücü, geometri tanımları ile ölçü tanımlarını aynı doğrulanan Python ortamına yükleyecek şekilde düzeltildi. Her iki kaynak aynı AST ve import denetiminden geçer; geometri fonksiyonu ölçü tanımlarını yüklerken çağrılmaz ve STEP'ler bu aşamada değiştirilmez.

Ölçü sözleşmesine yardımcıların kullanılabildiğini açıklayan tek cümle eklendi. Kayıtlı yanıtlarla yapılan yerel tekrarda yeni API çağrısı yapılmadı. İlk ve son geometri/ölçü kodlarının aynı olduğu ve 26 ürünün hacimlerinin değişmediği kontrol edildi. İlk deneme raporu ve nihai tekrar raporu ayrı korunuyor.

Doğrulama: 7 ürün hata testi (yardımcı kullanımı ve güvenlik dahil), 7 betik yükleyici testi, 5 pafta testi — toplam 19 test geçti.

## Token ve süre

| Çağrı | Giriş | Görünen çıktı | Reasoning | Toplam çıktı | Süre |
|---|---:|---:|---:|---:|---:|
| geometry | 26683 | 2984 | 49396 | 52380 | 227.8 sn |
| measurements | 28715 | 3662 | 25945 | 29607 | 125.8 sn |

API maliyet bildirimi: $0.0465333. İlk akış: 421.4 sn. Ek API çağrısı olmayan yerel tekrar: 129.7 sn.

Reasoning toplam çıktıya dahildir. Her çağrıda 65.536 çıktı tokenı ve 600 saniye sınırı ayrı uygulanır. Geometri çağrısı 52.380 token ile çıktı bütçesinin yaklaşık %80'ini kullandı; iki yanıt da stop ile tamamlandı. Ham reasoning metni ve API anahtarı yayımlanmadı.
