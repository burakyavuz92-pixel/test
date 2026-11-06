# @dis kesit gösterimi — Cıvata2.1

Mevcut genel @name promptu değiştirilmeden yeni JPEG/Excel ile 7 ürün çalıştırıldı.
Haiku 5.5 / high reasoning; iki API çağrısı. Model yanıtı elle değiştirilmedi.

## Gösterim sonucu

- 7 STEP + 7 JPEG üretildi; 7 ürünün tamamında dis ve montaj yüzey adları STEP'e yazıldı.
- dis silindirik A gövdesine bağlandı. Her paftada 1 işaretli kesit bölgesi,
  yüzeyin tam eksen boyu boyunca 2 ince çizgi ve 2 kesikli uç sınırı çizildi.
- Çizgiler pah/konik yüzeyin boyundan değil seçilmiş silindir yüzeyinin sınırlarından
  hesaplanır. Baş/son ayrımı, metin/standart/adım veya uygun çap hesabı yok.
- Bütün görünür ölçüler bağlandı; çözülemeyen ölçü/etiket yok.
- 4 yeni kesit testi ve mevcut 30 referans/yerleşim testi geçti.
- Pafta üretimi öncesi/sonrası 7 STEP SHA256 özeti aynı.
- 730001, gösterim kapalıyken ayrıca üretildi: izometrik occt-preview.png görüntüsü
  gösterim açık haliyle piksel düzeyinde aynı. preservation-check.json sonuçları içerir.
- Sadece boyuna (silindir eksenine paralel) kesit gösterimi desteklenir; enine/eğik
  kesitte yeni halka/elips gösterimi eklenmedi. Etiketsiz parça etkilenmez.

## Geometri inceleme notu

Bu yeni API çağrısında model 1 mm bilgisini COLLAR_FILLET=1 ile boyun-kafa birleşiminde
R1 olarak yorumladı; önceki çağrıdaki kafa ucunun 1 mm içeri çekilmesiyle aynı yorum
değildir. Konik geçişi de 2,5 mm tamamladı ve profilin geçiş sıralaması önceki
örnekten farklıdır. Görselde boyun yakınındaki geçiş ayrıca incelenmelidir.
Geçerli STEP ve çalışan gösterim, modelin bütün geometrik yorumlarının doğru olduğu
anlamına gelmez. Bu geometri elle düzeltilmedi; bu çalışma @dis çizim özelliğini
uygular ve sınar. Önceki ürünle birebir geometri eşitliği iddia edilmiyor.

## API kullanımı

| Çağrı | Input | Görünür output | Reasoning | USD |
|---|---:|---:|---:|---:|
| Geometri | 8.922 | 2.228 | 23.463 | 0,0137377 |
| Ölçü bağlama | 10.991 | 1.897 | 13.572 | 0,0088336 |
| Toplam | 19.913 | 4.125 | 37.035 | 0,0225713 |

Görünür output completion-reasoning farkıdır; ham reasoning yayımlanmadı.
Ek API çağrısı yok. Gösterim kapalı karşılaştırması API kullanmadı.

section-detail.png kesit yakın planı, preview.jpeg örnek paftadır.
STEP/JPEG dosyaları ana klasörde, teknik kayıtlar raporlar/ altında tutuldu.
