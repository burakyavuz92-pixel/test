# Güncel JPEG'deki [5] neden ölçülendirilmiyor?

Kaynak taslak7.1 JPEG; taslak7.2 denemesinde de aynı görüntü kullanıldı. Üretim kodu, kaynak görüntü, OCR önbelleği veya pafta değiştirilmedi. Yeni API çağrısı yok. Kırpımlar yalnız teşhis deneyidir.

## Kesin bulgu

Gerçek [5] konumunda mevcut OCR [9] döndürüyor. Bu konum yaklaşık x=3038, y=1174 piksel. Kayıtlı drawing/0 cleaned okumada [9] güven puanı 92,08; yerel psm7 kırpımında 87,38. Dolayısıyla etiket görüntüden kaybolmuş değil, rakam yanlış okunuyor.

Köşeli parantez ayrıştırıcısı [9]'u geçerli sabit ölçü adayı olarak kabul ediyor. Modelin aynı konumdaki etiketi 5 olduğu için metin eşleşmiyor. Başka bölgede, G'nin yerinde 180 derece döndürülmüş okumadan gelen [5] ise konum eşleşmesine uymuyor. Bu yüzden yanlış etiket bağlanmadan ölçü dışarıda bırakılıyor.

## Kontrollü kırpma denemeleri

| Görüntü | psm7 | psm11 |
|---|---|---|
| Çevre çizgileriyle birlikte 400×350 bağlam | [9] | [9] |
| Mevcut yerel kırpıma benzer 260×130 bölge | [9] | [9] |
| Yalnız metni içeren 100×90 sıkı kırpım | [5] | [5] |
| Aynı sıkı kırpıma 20 piksel beyaz kenar | [9] | [9] |
| Sıkı kırpımı 2 kat büyütme | [9] | [9] |

Sıkı kırpım psm6/7/8/11/13 seçeneklerinin hepsinde [5] okudu. Büyütülmüş kırpımda psm8/13 [5] döndürürken psm6/7/11 [9] döndürdü. Bu, daha büyük çözünürlüğün veya yalnız farklı psm seçmenin tek başına güvenilir çözüm olmadığını gösteriyor.

Mevcut yerel bölge üretimi harf/rakam bileşeninin çevresinde sabit ±130×±65 piksel kullanıyor. Adaylar çizgiler temizlenmiş görüntüden seçilse de yerel OCR'a verilen kırpım ham görüntüden alınıyor. Bu örnekte ölçü çizgisi ve ok parçaları da bölgeye giriyor. Bununla birlikte beyaz kenar deneyi de okumayı değiştirdiği için sorunu yalnız ölçü çizgisinin yakınlığına bağlamak doğru değil. Kesin bulgu, Tesseract'ın bu rakamda kırpma/kenar/ölçek bağlamına duyarlı 5–9 karışıklığı göstermesidir; iç tanıma mekanizması ayrıca kanıtlanmış değildir.

## Genel çözüm yönü

Gerçek parantezli metin sınırını ayırmak ve sınırlı kırpım/ölçek varyantlarından çıkan alternatifleri konumlarıyla birlikte korumak denenebilir. Tek bir yüksek güvenli okumayı kesin doğru saymamak gerekir. 9→5 gibi özel bir dönüşüm yazılmadı; yalnız model istediği için OCR metni değiştirilmedi. Teşhis koordinatları üretim koduna konmadı.
