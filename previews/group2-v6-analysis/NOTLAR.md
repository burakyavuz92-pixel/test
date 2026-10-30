# Koşullu gövde akışı v6 denemesi

Kullanıcının isteğiyle tek target ve pas-geç semantiği eklendi. Aynı taslak2guncel-notesiz.jpg ve taslak2guncel.xlsx yazılıma verildi. Görüntü hash'i önceki notsuz sürümle aynı. Tek API çağrısı, high, 20.000 completion üst sınırı. Çizim veya STEP üretilmedi. Ham model tarifi JSON içeriğiyle eşleşiyor; plan elle değiştirilmedi.

## Yeni sözleşme

- hole/fillet/chamfer hedef gövdeyi target alanıyla alır; cut target ve tool alır. Bunlarda inputs/optionalInputs boş.
- when=false ise değiştiren işlem hedef gövdeyi aynen geçirir. Yerel çözümde op=passThrough, featureApplied=false kaydedilir. Olmayan delik çapı/konumu bu adımda hesaplanmaya zorlanmaz.
- Oluşturma işleminde false koşul şekil yokluğu anlamına gelir; değiştirende gövde var, özellik yok demektir.
- Ölçü/kesit hedefleri featureApplied bilgisiyle süzülür. Gövde zinciri sonraki hedefler için kullanılabilir.
- Birleştirme hâlâ birden çok girdiyi alabilir. Alternatif gövdeler bir hole.inputs listesine yazılamaz. Sürüm 5 tarifleri otomatik olarak yorumlanmaz.

26 yerel C# kontrolü geçti. Boş E'de target aktarımı, var E'de delik oluşumu, sonraki işlem zinciri, olmayan özelliğin ölçü/kesitten çıkarılması, karışık target+inputs ve döngüler test edildi. Bu kontroller native CAD üretimi anlamına gelmez.

## Gelen tarif

Sıra: outerCyl, innerCyl, cupCut(target outerCyl/tool innerCyl), innerFillet(target cupCut), outerFillet(target innerFillet), holeC(target outerFillet), holeD(target holeC), holeE(target holeD, E doluysa).

Önceki iki gövdeli holeC hatası yok. E boş olan 200 ve 92'de holeE pas-geç olarak çözülüyor, nihai gövde sonuç kimliği korunuyor. E ölçüsü/kesit hedefi çıkarılıyor. E dolu 212/381'de özellik uygulanmış. F=0 delik varlığını kaldırmıyor.

Konum ilişkileri: holeCy=B-G, holeDy=-G, holeEx=-F. Dolayısıyla 92 için üst=86,7/alt=-78,7; 381'de üçüncü delik merkezde. Dört satırın tarif çözümlemesi başarılı, durum recipe-analysis-only. İşlem akışındaki düzeltme çalışıyor.

## Kalan yorum farkları

Model R8'i iç büküm yarıçapı saymış; dış yarıçapı 8+3=11 türetmiş. Önceki tarif ve kullanıcıyla izlenen pleyt modeli dış R8/iç R5 idi. Model bunu R8_INTERPRETATION uyarısında açıkça varsayım olarak bildiriyor. Format denetimi bu yanlış/kararsız görsel eşlemeyi tek başına düzeltemez. Bu nedenle tarifi tüm geometrisiyle onaylanmış saymıyoruz.

G için hideIf=never dönmüş. Eski kırmızı nottaki yarım-mesafe gizleme tercihi notsuz girdiden bu kez çıkarılmamış. Görsel yerleşim test edilmedi. Ölçek/piksel uyarısı ve G-not-half uyarısı model yorumlarıdır; bunlar doğru Excel'in değiştirilmesini gerektiren kanıt değildir.

## Kullanım

15.798 input, 9.845 completion (4.691 reasoning dâhil), toplam 25.643 token. Sağlayıcı maliyeti 0,130046 USD. Cache okuma/yazma 0. API çağrısı 1, yeni çizim 0, plan müdahalesi 0. NativeExecutionImplemented=false devam ediyor.

Dosyalar recipe.json ham planı, *.resolved.json satır bazlı yerel çözümleri, checks.json çalışma ve sayaç özetlerini içerir. Kod değişiklikleri koşullu akış sözleşmesine ait; R8 veya B/G için özel doğru cevap eklenmedi.
