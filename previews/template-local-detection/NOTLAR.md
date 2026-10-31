# Taslak ölçü yerleşimi — yerel OCR önizlemesi

API çağrısı yapılmadı. Ürün CAD/JPEG'i yeniden çizilmedi; bu, kaynak taslak üzerindeki tespit işaretlemesidir. Kaynak taslak4.2.jpg; Excel olmadan okundu. Görünüş bölgeleri bu taslak yerleşimi için bir kez yazılımda tanımlandı: kesit, ana görünüş ve izometrik. Bunlar her keyfi taslaktan otomatik çıkarılmıyor.

Yerel araçlar: Tesseract 5 CLI, Pillow, NumPy ve OpenCV. Düz, dikey ve ±45 derece okumalar; uzun çizgileri ayıklama ve iki tek tırnak arasında karakter bulma yöntemleri birlikte denendi. Görüntüdeki renkler görünürlük kararı için kullanılmadı. Tek tırnak tespiti OCR'nin büyük paftada kaçırdığı B/C/G gibi harfleri bulmayı sağladı. İşlem ağ veya AI API'si gerektirmez.

## Sonuç

13 aday kutulandı. Harfli: B, C, G ana görünüşte; A, D, E, F, J kesitte. Ek bir J tespiti aslında J+6 alanındaki harftir; +6 henüz okunmadı. Etiketsiz sabit adaylar: R8, R1,5, R2 ve 33, hepsi kesitte. Konum, normalize kutu, okuma açısı, görünüş, OCR güveni ve yöntem JSON'da saklanır. Bunlar onaylanmış ölçü bağlantıları değildir.

## Eksikler

I ve sabit 3 mm bulunamadı. J+6 bileşiğinde +6 eksik; 33±0,5 bileşiğinde tolerans eksik. Sabit değerlerin eksik parçaları tahminle tamamlanmadı. Sabit ölçüler Excel'de bulunmadığı için atılmıyor, ancak bu aşamada bütün sabit ölçülerin kusursuz okunabildiği söylenemez. Tespiti eksik bir değeri üretimde yeniden yazmak tolerans kaybına yol açabilir; bu yüzden üretim yerleşimine bağlanmadı.

Bütün kayıtlar needs-review durumundadır. Mavi kutu harfli aday, kırmızı kutu sabit sayısal adaydır; önizlemedeki bu renkler kaynak ölçü rengi veya gizleme talimatı değildir. OCR güveni doğruluk garantisi değildir. Ok ucunun veya uzatma çizgisinin hangi geometrik öğeye bağlı olduğu henüz çözülmedi; yalnız yazı konumunu bulduk.

İlk ham OCR az sayıda doğru tespit ve yanlış aday verdi. Kırpma/rotasyon, çizgi ayıklama ve tırnak komşuluğu ile sonuç iyileşti; son önizleme görsel incelendi. Bu bir keşif prototipidir, otomatik ölçü yerleşiminin tamamlandığı anlamına gelmez. Eski yerleşim algoritması bu tespitlerle değiştirilmedi. Gizlenecek ölçüler için Excel düzenine dokunulmadı.

## Çalıştırma

Depo kökünde, Tesseract CLI kurulu ve Python bağımlılıkları mevcutken:

`python tools/inspect_template_dimensions.py samples/taslak43-upload/taslak4.2.jpg output/new-template-detection`

Sonraki çalışma: eksik tek karakter/bileşik ölçüleri güvenilir okumak, sonra ölçü çizgisi/ok yönünü çıkarıp bu konumları görünüşe göre yeniden yerleştirme kurallarına dönüştürmek. Sabit ölçüler de aynı yerleşim kaydında tutulmalı; henüz eksik okumayı üretime taşımamalıyız.
