# Sağ üst OCCT görünüşü — ilk bütünleşik kontrol paftası

[Pafta JPEG](11-30-212.jpeg) · [STEP](11-30-212.step)

Eski el çizimi izometrik motoru kaldırıldı. Ön görünüş/kesit Skia ile, sağ üst görünüş OCCT katı modeli ve yerel VTK CPU görüntülemesiyle oluşur. Örnekte sabitler ve kamera API planından, delikler Excel'den geldi; asistan sayısal geometri veya kamera girmedi. İkinci grubun A–H sözleşmesi programda açıkça desteklenen profildir, genel her-parça modelleme tamamlanmadı.

Kamera API'nin JPEG üst sağ referansından tahminidir; son yanıt confidence=low verdi. Bu nedenle pafta yalnızca açı kontrolü için üretildi; kamera kesin eşleşmiş/insan tarafından onaylanmış değildir. Bu durumda toplu üretim engellenir. Önizleme, parametreleri değiştirmeden tamamlanmış API yanıtını kaynak SHA256 bağıyla tekrar doğrulayan yerel komutla üretildi. Yeni API çağrısı yapılmadı. İzometrik kutuya sığdırılmıştır; teknik baskı ölçeği verilmez. Ana görünüşün ölçeği ayrıdır.

Müdahaleler: asistan yeni OCCT bağlantısını ve kamera şemasını kodladı; model tam paftadan açıyı belirsiz bulunca yazılıma otomatik referans kırpma ekledi. Kırpma bölgesi bu pafta profiline elle tanımlıdır. İki çalışma da düşük kamera güveni nedeniyle durdu. Sonra yalnızca kamera belirsizliğinin tek önizlemede uyarı olarak kalması sağlandı; geometrik belirsizliklerin engellenmesi korundu. Kaydedilmiş yanıtla ilk ürün üretildi. Bu, sınırsız otonom çizim veya genel kamera kalibrasyonu iddiası değildir.

27 C# kontrolü ve 6 OCCT geometri testi geçti. CPU llvmpipe doğrulandı. BRep, delik hacmi ve STEP dışa/içe aktarımı doğrulandı. Görsel ve kamera onayı bekleniyor.
