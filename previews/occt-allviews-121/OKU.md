# 11-30-121 — OCCT tüm görünüşler denemesi

[Pafta JPEG](11-30-121.jpeg) · [STEP](11-30-121.step)

Girdi: taslak1.xlsx + ilk grubun R8 eklenmiş yüksek çözünürlüklü taslağı (highres-reference.jpg). İkinci grubun taslağı kullanılmadı. Hedef: Ø286±1, B=139,7±0,5, üst Ø21 ve alt Ø12,6 (+0,1|-0,0), parça numarası 11-30-121. Sabitler API'den 33,5 mm derinlik, 3 mm et, dış R8 olarak okundu.

Yeni API planı sütun ifadeleri, delik bağlantıları, kamera ve kesit/ölçü gösterim tarifini içerir. İlk model yanıtı çelişkili/geometrik onay soruları bıraktığı için reddedildi; ikinci yanıtta sorular kalmadı. Toplam 2 çağrı, bildirilen maliyet 0,061246 USD. Kamerayı/ölçüleri asistan elle girmedi. İlk yerel JSON veri ömrü hatası kodda düzeltildi; kaydedilen API planı yeniden çağrı yapmadan kullanıldı.

Üç görünüş aynı OCCT katısından üretilir. Ön görünüş HLR, gerçek düzlem kesiti OCCT kesişim/yarım katı HLR, izometrik VTK'dır. Oklar/yazılar/toleranslar yeni SVG katmanıdır; SkiaSharp kullanılmaz. Arial gerçek font dosyasından vektör glyph olarak çizilir. Ölçüler model değerleriyle karşılaştırıldı: 286, 139,7, 21 ve 12,6 mm. Düzlemsellik 0,5 kaynak resimden modele aktarılıp gösterildi.

1754×1240, kaynakla aynı 300 DPI. Fiziksel boyut yaklaşık 148,5×105 mm; ana ölçek 1:5, izometrik ölçeksiz. Kaynak antet/çerçeve korunmuştur. Görsel/üretim onayı verilmiş değildir. Kamera tahminidir; kaynakla birebir eşleştirme yapılmadı. Kademeli kesit bu yeni yolda desteklenmiyor. Font boyutu henüz taslaktan otomatik ölçülmüyor. Yeni geometri, görüntü ve genel ölçü yerleşimi kullanıcı kontrolü gerektirir.
