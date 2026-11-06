# Civata2.1 — güncel build, Haiku/high

2026-11-06 tarihinde kullanıcının civata2.1.zip arşivindeki civata2.xlsx ve civata2.1.jpg verildi. Uygulama sürümü 0d878e4556d29e5b334245a0a59ee72a37dbea22; dal taslak47-cadquery-step. Release derlemesi kullanıldı. Model anthropic/claude-haiku-5.5, reasoning high; token tavanı 65.536, çağrı zaman aşımı 600 saniye. Uygulama kodu, prompt, girdiler ve dönen model kodları elle değiştirilmedi. Geometri yeniden kullanımı veya replay yok.

## Sonuç

Yedi ürünün tamamı STEP ve ölçülendirilmiş JPEG olarak üretildi: 730001, 730003, 730006, 730013, 730014, 730016, 730017. Her geometri bir geçerli katı; STEP yeniden okunma kontrolü başarılı. dis ve montaj yüzey isimleri her üründe korunarak doğrulandı. Kesitte dis silindirinden iki ince paralel çizgi ve iki kesikli uç sınırı üretildi; STEP'e diş geometrisi eklenmedi.

Her üründe A/B/C/D/E/L dahil altı ölçü yerleşti. Çözülemeyen ölçü ve doğrulanamayan görsel etiket listeleri boş. Nihai durum sheets-produced, çıkış kodu 0. Bu otomatik rapor sonucu, teknik resmin kullanıcı tarafından görsel onayı yerine geçmez. Örneğin modelin verdiği sabit geçiş boyu ve radyus yorumları insan değerlendirmesine açıktır. Geometri veya ölçü hatalarını gizlemek için elle düzeltme yapılmadı.

Bu buildin yayımladığı çıktı STEP ve JPEG'dir; bu denemede PDF üretilmedi. Program kaynaklarında değişiklik yapılmadı; bu kayıt yalnız deneme sonuçlarını ekler.

## Maliyet ve süre

İki API çağrısı yapıldı, ek değerlendirme veya tekrar çağrısı yok.

| Aşama | Input | Output toplam | Reasoning | USD | API süresi |
|---|---:|---:|---:|---:|---:|
| Geometri ve etiketler | 8.922 | 30.589 | 27.824 | 0,0161867 | 137,2 sn |
| Ölçülendirme | 11.049 | 21.182 | 19.259 | 0,0116959 | 92,5 sn |
| Toplam | 19.971 | 51.771 | 47.083 | 0,0278826 | 229,6 sn |

Output toplamı reasoning'i içerir; ayrıca üzerine eklenmemelidir. Reasoning dışı completion farkı toplam 4.688 token. İki çağrıda da cached_tokens=0. Toplam çalışma 491,8 saniye (yaklaşık 8 dakika 12 saniye); API dışındaki sürede CPU ile geometri, OCR, etiketleme ve pafta üretimi vardır. İlk OCR bu çalışma klasöründe yeniden yürütüldü. Ham API reasoning yayımlanmadı.

Dosyalar: yedi JPEG ve STEP, dönen part.py/face-tags.py/measurements.py, yapılandırılmış sonuç/ölçü raporları, usage-summary.json. Girdi hash'leri pipeline-source.json içinde. Ürün bazlı ölçek ve ölçü yerleşim kayıtları da eklenmiştir.
