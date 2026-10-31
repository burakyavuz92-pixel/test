# A5 — geometriye bağlı ölçülendirme

Yeni API çağrısı yapılmadı. Kayıtlı Haiku no-colors tarifi değiştirilmeden kullanıldı. 3 JPEG ve PDF üretildi. Sabit taslak çerçeve ve anteti korunur; ürün kodu, ölçek ve A5 alanları yerelde yazılır.

## Yapılanlar

Çap ölçülerine lider ve ok; mesafelere ölçü/uzatma çizgileri; radyuslara mevcut katıdaki toroidal yüzlere bağlı liderler eklendi. Arial yazı kullanılır. Nominal ve toleranslar yerel kaynak hücreden gelir. Katının görsel büyüklüğünden tolerans veya değer tahmin edilmez. İlk ürün görsel incelendi. Ölçüler artık genel tabloda değil görünüşlerin üzerindedir.

İlk iki üründe 14'er ölçü; 11-24-372'de 13 ölçü yerleştirildi. Son üründe B=0 ölçüsü atlandı. Bu üç üründe çözülemeyen veya yazı çakışması yüzünden yerleştirilemeyen ölçü kalmadı. Her ürünün placement JSON'u yerleştirme/atlama nedenlerini kaydeder. Yazı kutuları birbirleriyle çakışırsa ilgili çizim geri alınır; isimsiz çizgiler bırakılmaz. Yazılar son katmanda tekrar basılarak çizgilerin metin üzerinden geçmesi önlenir. Bütün lider yollarının birbirleriyle kesişmesini eniyileyen tam bir yerleşim çözücüsü değildir.

## Geometri bağlantısının kapsamı

Etiket A/B/C veya belirli ürün kodları için sabit değer yazılmadı. Targets işlem ID'leriyle silindirik yapım öğelerine gidilir. Desteklenen bağlantılar: önden görülen silindir çapı; iki eksen merkezi arasındaki X/Y mesafe; tek eksenin dünya orijinine X/Y uzaklığı; Z eksenli silindirin gövdeyle kesişen eksenel boyu; aynı eksenli iç/dış silindir yüzleri arasındaki radyal et; tekil torus yüzüne bağlanabilen fillet radyusu. Tek hedefli X/Y ölçüde datum dünya orijinidir. Serbest role metninden keyfi teknik anlam çıkarılmaz.

Açı, keyfi profiller, çoklu/örtüşen torus yüzleri, desenlenmiş birden çok şekil veya farklı datum ilişkileri için bu çözücü genel çözüm değildir. Desteklenmeyen/çakışan ölçü varsa bağlantısı uydurulmaz; ayrı kontrol tablosu ve JSON raporunda tutulur. Bu, bütün parçalar için üretim seviyesinde otomatik ölçülendirme garantisi değildir. Geometrik eşitlik kontrolleri yalnız uygun çizim ankrajını seçmek içindir; eksiksiz parça doğrulama sistemi değildir.

## Korunan sınırlamalar

R2 ve gövde iç köşe geometrisi düzeltilmedi; R2 oku mevcut yanlış kök radyusuna bağlıdır. Kullanıcı geometriyi bu paftadan doğru kabul etmemeli. Kademeli kesit sınır çizgileri ve arka kenar görünürlüğünün mevcut sınırlamaları devam eder. Ölçü gizleme Excel düzeni henüz eklenmedi; daha önce yeşil olan ölçüler de bu denemede gösterilir. Sabit antet A5'te küçük yazılar içerir. Baskı %100/gerçek boyutla kontrol edilmeli.

4 yeni ölçü bağlantısı/başarısız yerleştirme testi geçti. Mevcut 9 native test de geçti. Üç yeni katı üretimi ve STEP yeniden okuma kontrolü başarılı. Bu kayıt onaylı üretim resmi değildir.
