# Taslak4.2 — Haiku high / 65536 token

anthropic/claude-haiku-5.5, high; sağlayıcı Claude Platform on AWS. Önceden hazırlanan 65536 toplam completion sınırı ve 600 saniye API zaman aşımıyla çalıştırıldı. Aynı orijinal JPEG, Excel, tam metin girdisi ve v9 sözleşmesi; görsel küçültülmedi. Tek API çağrısı. Bu çalışma sırasında yazılım/prompt veya ham model tarifi değiştirilmedi; ek onarım çağrısı yok.

## Bütçe ve sonuç

| Ölçüm | Eski high / 32768 | Yeni high / 65536 |
|---|---:|---:|
| Input | 9825 | 9825 |
| Reasoning | 31559 | 43503 |
| Görünür completion | 1209 | 2503 |
| Toplam completion | 32768 | 46006 |
| USD | 0,0173665 | 0,0239855 |
| finish_reason | length | stop |

Cache 0. Yeni yanıt dosyasına kadar yaklaşık 213 saniye; önceki 161 saniyeydi. Süreler salt reasoning süresi değildir. Yeni yanıt 65536 sınırının tamamını tüketmedi; JSON tamamlandı. Yazılım üç geçerli tek katı, STEP geri okuma ve üç JPEG inceleme önizlemesi üretti. İlave yerel düzeltme gerekmedi.

## Geometri hataları — tamamlanan yanıt doğru sayılmadı

- Döndürülmüş rev profilinin içine J çaplı bir merkez deliği ve J+6 dış çaplı, R2 köklü bölgeyi ana z ekseninde yerleştirmiş. Kaynaktaki şekillendirilmiş bölge ise B kadar kaçık delikle aynı eksende olmalı.
- Ayrıca x=B'de ayrı boss/add ve boreL/cut var. B sıfır olmayan 11-24-13 ve 11-24-216 ürünlerinde bu, kaynakta olmayan ek merkez deliğine ve iki ayrı bölgeye yol açıyor. B=0 satırında eksenler çakışıyor; bu satırın görünüşü diğerlerinin doğruluğunu kanıtlamaz.
- F yine dış çıkıntı: D çaplı boss/add z=-F'den başlıyor. İçeri malzeme çıkarma işlemi değil. Sonuç elle düzeltilmedi.
- R2 bu kez hem profil yayı hem anotasyon olarak var; fakat yanlış merkezdeki bölgeye ait. Sadece R2'nin bulunması yeterli değil.
- A/C/D/E/F/J siyah; B/G/I ve sabit 33/3/R8/R1,5 yeşil olarak dönmüş. Gövde profili genel kap biçimini koruyor; bu kısmi doğrular nihai parçanın doğruluğunu sağlamıyor.
- Ana görünüşte nonzero-B ürünler için fazladan merkez deliği görünüyor. İzometrik bakış da taslak açısıyla aynı değil. Geometri BRep bakımından geçerli, taslak bakımından yanlış.
- Yerel antet, ölçü okları, eksenler ve kesit/yerleşim sınırlamaları sürer. JPEG'ler üretim paftası değildir.

Artırılmış token bütçesi bu denemede yarım yanıt problemini aşmaya yetti; doğru geometri sonucuna ulaşılmadı. Daha fazla reasoning'in tek başına doğruluğu garanti etmediği görülüyor. Bu tek örnekten bütün model görevleri hakkında genelleme yapılmadı; kullanıcı adına başka çağrı başlatılmadı.
