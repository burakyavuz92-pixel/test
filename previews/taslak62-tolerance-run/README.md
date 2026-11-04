# Taslak6.2 — tolerans ve Ø gösterimi denemesi

Altı STEP ve altı antetli JPEG içerir. **İnceleme çıktılarıdır; tüm ölçü bağlantıları çözülmüş değildir.**

Kayıtlı Haiku 5.5 / high geometri ve ölçü yanıtları yeniden çalıştırıldı; bu tekrar çalıştırmada yeni API çağrısı yapılmadı. Önceden API ile çıkarılmış görünüş çerçeveleri işaretlere eklendi. Dosyalar taslak6.2.xlsx/JPEG girdilerine dayanır; geometri kodu elle değiştirilmedi.

Eşit toleranslar ±, farklı toleranslar üst üste çizilir. `_METIN` doluysa nominal gösterimi bastırır; boşsa Ø yalnız ana ölçüde verilmişse gösterilir. E hücrelerinde Ø yoktur.

Yerleşen ölçüler çoğu satırda A/B/C/D'dir. E etiket çakışması, pahların tek oklu gösterimi ve 25 ölçüsünün silindir dışındaki çap desteği çözülmemiştir. 733001-03'te ayrıca B referansı bulunamamıştır. E'nin tablodaki gösterimi, parçaya bağlandığı anlamına gelmez. Ayrıntılar `tolerance-flow-check.json` ve `script-sheet-results.json` içindedir.

`taslak62-step-jpeg.zip`: altı STEP, altı JPEG ve tolerans renderer önizlemesi. Her parça kendi klasöründedir. Raw API yanıtları ve reasoning içerikleri paylaşılmamıştır.
