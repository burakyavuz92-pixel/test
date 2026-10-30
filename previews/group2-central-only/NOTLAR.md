# Merkezden düz kesit karşılaştırması

Aynı taslak2guncel.xlsx ve taslak2guncel-notesiz.jpg, aynı high/model/çıktı sınırı; tek çağrı. Ayrıntılı kesit ve kademeli yol tanımı yerine merkezden düz kesit isteyen tek satır veri formatı kullanıldı. Dosya SHA256 değerleri iki run-report kaydında karşılaştırılabilir. Sohbetteki görselle birebir dosya özdeşliği iddia edilmiyor; önceki çağrının aynı yerel nüshası kullanıldı.

|Metrik|Önceki|Merkezi düz kesit|
|---|---:|---:|
|Giriş|9559|9392|
|Akıl yürütme|7907|4667|
|Görünür çıktı|2852|2951|
|Toplam çıktı|10759|7618|
|Maliyet USD|0.126708|0.094964|

Dört satırın yerel çözümlemesi geçti; geometrik doğruluk garantisi değildir. Modelin tarifi elle değiştirilmedi. Çizim/STEP ve tekrar çağrı yapılmadı. Merkezden kesit kaçık üçüncü deliği göstermeyecek; kullanıcının tercih ettiği kapsam budur. Tek örnek karşılaştırması, farkın tamamının prompttan kaynaklandığını kanıtlamaz. Ham özel akıl yürütme yayımlanmadı.
