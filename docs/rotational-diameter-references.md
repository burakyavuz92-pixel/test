# Kavisli dönel yüzeyde çap referansı

Çap referansı silindir veya dairesel BRep kenarına ek olarak koni, küre, torus ve
dairesel/daha genel dönel yüzey üzerindeki tam bir çemberle desteklenebilir.
Yuvarlak bir kafanın en geniş kesitinde topolojik kenar bulunması zorunlu değildir.

Yazılım verilen merkez, eksen ve yarıçapı değiştirmez. Destek yüzeyinin dönme ekseni
ile eş eksenlilik kontrol edilir. Kurulan çemberin yüzeyle BRep ortak kısmının
uzunluğu tam çevresiyle karşılaştırılır: kısmi yay veya yanlış kesitteki çember
kabul edilmez. Düzlemsel yüzey içinde rastgele bir çember destek sayılmaz.
Mevcut nominal/yarıçap ve görünüş kontrolleri korunur; parça kimliğine özel kural yoktur.

İlgili testler: test_script_measurements.py (küre/torus kabulü, yarım yüzey,
yanlış kesit ve düzlem üzerinde uydurma çemberin reddi). Cıvata2'nin R5 dönel
kafasındaki L referansı aynı model yanıtıyla ayrıca pafta üretiminde doğrulandı.
