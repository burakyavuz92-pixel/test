# Ortalanmış ölçü yazıları ve 3,5 mm başlangıç boşluğu

- Dar ölçüde yazıyı uca kaydırma kaldırıldı. Yazı ölçülen aralığın ortasında kalır; dar açıklıkta oklar dışarı bakabilir.
- İlk doğrusal ölçü çizgisi görünüş sınırından 3,5 mm ötede başlar. Çakışma varsa daha dış konum denenebilir; sonraki sıralar eskisi gibi dışarı ilerler. Mesafe parça ölçeğiyle değişmez.
- Çap gösterimleri önce, pah/radyus liderleri sonra yerleştirilir. Aynı görünüşte yerleşmiş yazıların x/y hizaları aday alınır. Yer yoksa ölçü düşürülmez, ölçek/yerleşim araması devam eder. Başka ölçü olmayan görünüşte standart dış lider konumu kullanılır.
- Geometri referansları, kamera ve STEP değişmedi. Kayıtlı Taslak6.6 model kodu/ölçü verileriyle yeniden çizildi; yeni API çağrısı 0.

Altı parçada 11/11 gösterim yerleşti; geometrik veya görsel eksik raporu yok. Beş parça 1:1, 733001-03 2:1. Modelin kaynak taslağı anlaması için yeni bir API denemesi değildir.

Testler: dar ölçünün ortası, ilk boşluğun 3,5 mm olması, pah ve radyusların mevcut ölçülere hizalanması; mevcut şerit/yerleşim/ölçek regresyonları. Çıktı font boyutu ve ölçü değerleri korunmuştur.
