# Doğrusal ölçülerin sanal referansları

Distance/thickness için iki noktanın malzemeye temas etme zorunluluğu kaldırıldı.
Modelin koordinatları yüzeye taşınmıyor. Sonlu koordinat, birim yön, nominal uzaklık,
görsel ok yönü ve seçilen görünüşte izdüşüm kontrolleri korunuyor. Çap, radyus ve pah
geometrik destek kontrolleri değiştirilmedi. İkinci çağrı sözleşmesi de sanal noktalar,
merkezler ve eksenleri kabul edecek şekilde aynı kuralla uyumlu hale getirildi.

Önceki canlı çalışmada J'si bağlanmayan 8 ürün mevcut STEP ve model referanslarıyla
tekrar çizildi: 8/8 pafta, her birinde 7 görünür ölçü, çözülemeyen ölçü/etiket yok.
F=0 olduğu için F gizli; J artık yerinde. API çağrısı yok. STEP SHA256 değerleri
önceki çalışma ile aynı. Diğer 32 pafta bu çalışmada yeniden üretilmedi.
11 referans testi ve 16 yerleşim testi geçti.

R1,5 incelemesi: 11-30-260 STEP'inde açık uçtaki torus küçük yarıçapı 1,5 mm,
profil açısı 90 derece. Dış yarıçap 113,5; torus ana yarıçapı 112; açık düz alının
sınır yarıçapları 112 ve 110,5 mm. Arada 1,5 mm düz alın kalıyor, iç köşe keskin.
Model geometri kodu dış köşede çeyrek yay çizip iç çapa düz hatla dönmüş.
R1,5 geometrisi bu değişiklikte düzeltilmedi. İç ve dışı birleştiren tam yuvarlak
uç profili ayrı bir geometri yorumlama konusudur; bütün radyusları otomatik olarak
iki köşeye uygulayan bir kural eklenmedi.
