# Ortak görünüş ölçeği

`tools/adaptive_scale.py` ana görünüş ve kesit için aynı ölçeği seçer. Arama
ızgarasına 1:2,5, 1:3, 1:4, 1:6, 1:8 gibi ara oranlar eklendi; önceki 1/2/5
adımları da korunur. Bu oranlar onluk mertebelerde tekrarlanır, büyütme de mümkündür.
Büyükten küçüğe gidilir; geçerli yerleşim bulunan en büyük ölçek kullanılır.

Değişiklik yalnız aday ölçek listesindedir. Önceki kontroller korunmuştur:

- Ana görünüş ve kesitin gerçek en/boyu ayrı hesaplanır; yatay/dikey uzun kesitler
  ve kısa/geniş pleytler aynı yöntemle işlenir.
- Ölçü yazılarına ayrılan alan, panel boyutları, görünüşler arası aralık, kesitin
  solda olması, antet/izometri için ayrılmış bölgeler değiştirilmez.
- Ölçü yerleşimi gerçekten denenir; yazı/çizgi sığmıyorsa daha küçük ölçeğe geçilir.
- Yazı boyutu ile 3,5 mm başlangıç ve 1,5 mm bant aralıkları değiştirilmez.

Yerel ölçek testleri 160 ve 227 çaplarında ara ölçek seçimini, iki yönde uzun
kesit sığmasını, yeni ölçeklerde de çakışma reddini ve eski adayların korunmasını
kontrol eder. Sadece paket sığdırma testindeki 160 için 1:2,5 ve 227 için 1:4
sonuçları, gerçek yazı yerleşimi denenmeden nihai pafta ölçeği garantisi değildir.
Bu değişiklikte CAD üretimi, OCR veya API çağrıları yeniden çalıştırılmadı.
