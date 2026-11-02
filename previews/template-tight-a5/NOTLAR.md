# Yazıya yakın çakışma kontrolü ve üst üste tolerans

Yeni API çağrısı yapılmadı. Önceki template-bound-a5 denemesindeki aynı kayıtlı tarif, aynı güncel Excel ve JPEG yeniden işlendi. Geometri değiştirilmedi; önceki I→L referans uyarlaması aynen kullanıldı.

Çakışma sınırı artık döndürülmüş metnin dış dikdörtgeni yerine görünen harflerin yaklaşık bir çıktı pikseli çevresini izler. Etiketler arasındaki önceki dört piksellik ek boşluk kaldırıldı. Yakın adaylar önce 4, 8, 12, 16 piksel adımlarla aranır. Geometriyle çakışma kontrolü de aynı dar metin maskesini kullanır. Bu, tüm ölçü çizgilerinin birbiriyle çakışmasını çözen bir algoritma değildir.

Asimetrik toleranslar nominal değerin yanında küçük puntoda üst/alt satır halinde, parantez içinde çizilir. Ana yazı 18, tolerans 12 referans punto/piksel biriminde hazırlanır ve pafta ölçeğinde rasterlenir. ± toleranslar ve diş çağrıları tek satır kalır. Yerleşimde metin genişliği de bu yeni yazımın gerçek raster genişliğinden alınır.

Altı JPEG/PDF üretildi; dört satırda 11, B=0 olan iki satırda 10 ölçü yerleştirildi. Çözülemeyen bağlantı kaydı yok. Dar kesitte J/E ölçüleri ve bazı çizgiler hâlâ yakındır; yerleşim tamamlanmış sayılmaz. Önceki geometri hataları bu çalışmanın kapsamı dışındadır.

Doğrulama: yeni dört metin/mask testi, dört mevcut ölçü testi, beş bağlama testi ve dokuz OCCT yürütücü testi geçti.
