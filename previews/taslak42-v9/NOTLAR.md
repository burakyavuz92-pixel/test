# Taslak4.2 — mevcut detaysız v9 testi

Yeni ZIP'teki taslak4.2.jpg ve taslak4.xlsx yazılıma verildi. Dosyalar, prompt ve sözleşme değiştirilmedi; parçaya özel ek bilgi yok. Claude Sonnet 5.5, high, tek çağrı. Yazılıma veya ham model JSON'una müdahale edilmedi. Otomatik ikinci çağrı yok.

## Kullanım

Input: 9825; reasoning: 9786; görünür completion: 3167; toplam completion: 12953. Maliyet 0,149180 USD; cache 0. Komut başlangıcından API yanıtının dosyaya kaydına yaklaşık 106 saniye; yalnız düşünme süresi değildir.

Taslak4.1: reasoning 8168 ve 0,123380 USD. Taslak4.2 yaklaşık %20,9 pahalı. Yeni JPEG'de R2 ve yeşil J+6 ölçüsü bulunuyor; bu nedenle denemeler aynı görsel girdinin tekrarı değildir. Tek çağrıyla maliyet değişiminin sebebi belirlenemez.

## Sonuç ve eksikler

- Üç geçerli tek katı, STEP yeniden okuma kontrolü ve üç JPEG inceleme önizlemesi üretildi. Detay görünüşü yok.
- Yeni J+6 bilgisi hubCollar dış çapına uygulanmış. R2, collarFillet işlemiyle uygulanmış ve siyah ölçüye bağlanmış.
- F yine dış çıkıntı: gövde tabanı z=0..3, hubFlange/add işlemi D çapıyla z=-F'den başlıyor. Ölçü rolü de protruding outer face. Bu, kullanıcının istediği içe boşaltma değildir. Yazılım bu veriyi elle düzeltmedi.
- Siyah C ölçüsü sourceColor=green dönmüş ve gizlenmiş. Yeşil 3/R8/R1,5 ise black dönerek tabloya basılmış. Renk yorumlama hatası API yanıtındadır.
- B=0 satırında ilgili şekillendirilmiş bölge merkezde kalır; üst/alt delikler ±C/2 olarak tarif edilmiş.
- Ölçü okları, delik eksenleri, taslak anteti ve sayfa yerleşimi önceki inceleme yürütücüsü sınırlarında. Bu JPEG'ler tamamlanmış üretim paftası değildir.

Bu denemeyi doğru/optimum sonuç olarak kabul etmiyoruz. R2 ve dış çap bilgisi uygulanmış olsa da F yönü ve renk sınıflandırması sorunları devam ediyor.

## 82 çizimlik sürüme dönüş

Kodların çalışmayı yayımlayan Git kaydı c261eb1 ile korunmuş olduğu doğrulandı. archive/legacy-v4 altında pleyt adaptörünün kopyası var; eski OCCT pleyt kodu experiments/occt altında. Güncel çalışmayı silmeden ayrı worktree/klasörde eski commit açılabilir. Aktif v9 uygulamasında tek tuşla motor değiştirme özelliği yok. Eski sürümün bağımlılıkları, font ve kaynak dosyalarıyla birlikte kurulması gerekir; bu çalışma sırasında eski sürüm yeniden çalıştırılmadı ve mevcut yazılım geri alınmadı.
