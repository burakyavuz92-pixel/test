# Yeni 3deliklipleyt — baştan sona canlı çalışma

Yüklenen yeni ZIP girdisi değişmeden kullanıldı. Haiku 5.5 / high reasoning,
12 temsilci satır, iki canlı API çağrısı; 40 ürünün tamamı yerelde çalıştırıldı.
Otomatik ek çağrı yok. Model kodu/referansları elle değiştirilmedi. Süre 403,95 saniye
(yaklaşık 6 dakika 44 saniye); API süreleri 149,60 ve 83,75 saniye.

## Sonuç

- 40 STEP ve 40 ölçülendirilmiş JPEG üretildi.
- 40/40 STEP geçerlilik/tek katı/dışa-içe aktarım kontrolü geçti.
- 40/40 montaj yüzeyi etiketi ve bağımsız dış çap, derinlik, üç delik merkezi/çapı,
  montaj iç düzlemi ve alanı kontrolü geçti. Her profil ayrıntısının tam kanıtı değildir.
- 32 pafta tüm ölçülerle tamamlandı. 8 paftada J ölçüsü bağlanamadı.
- Toplam 304 ölçü yerleştirildi. F=0 olan 8 üründe F ölçüsü doğru şekilde gizli.
- OCR ile doğrulanamayan etiket: 0. 120 C/D/E çapının tamamı inclined-diameter.
- Ölçekler: 20 üründe 1:2, 9 üründe 1:2,5, 11 üründe 1:4.
  A=160 grubunda 1:2,5; A=227 grubunda 1:4 kullanıldı.
- Ana çıktı klasöründe STEP/JPEG dosyaları birlikte; diğer kayıtlar raporlar/ altında.
- Çalışmadan önce derleme ve 24 ilgili yerel ölçek/yerleşim testi geçti.

## J neden bağlanmadı?

İkinci çağrının ölçü fonksiyonu J için ilk noktayı [0,0,0] seçmiş.
F=0 olduğunda E deliği merkezdedir; bu nokta malzemede değil, deliğin boşluğunda
kalır. Diğer J noktası [ri,0,-J] gövde üzerindedir. OCCT ile ayrıca ölçülen ilk nokta
uzaklıkları E/2 ile aynı, ikinci nokta uzaklıkları sıfırdır; ayrıntı
j-reference-diagnosis.json içinde.

Etkilenen ürünler: 11-30-260, 11-30-299, 11-30-372, 11-30-381,
11-30-382, 11-30-81, 11-30-905, 11-30-912.

Bu geometri üretim hatası veya nominal J değeri hatası değildir; ikinci model
çağrısında yanlış referans noktası seçilmesidir. F=0 örnekleri seçilmiş tabloda
vardır. Yazılım noktayı reddetti ve paftada kontrol tablosuna aldı.
Koşu durumu sheets-produced-with-unresolved-measurements, çıkış kodu 2.
product-results.json içindeki completed dosyanın üretildiğini ifade eder; ölçülerin
eksiksizliği script-sheet-results.json ve run-report.json ile ayrıca değerlendirilir.

## Kullanıcının kabul ettiği kesit ayarı

32 satırın sıfır olmayan V kesit kaçıklığı pozitiftir: sağa (+X) kaydırır.
E deliği ise kaynak taslağa uygun olarak X=-F tarafında üretilmiştir. Bu sebeple bu
satırlarda kaçık kesit E deliği merkezinden geçmez. Kullanıcının talimatıyla
kaçıklık işareti değiştirilmedi. F=0 satırlarında merkez kesiti E'den geçer.
Bu durum J referans hatasından ayrıdır.

## Token kullanımı

| Çağrı | Input | Görünür output | Reasoning | USD |
|---|---:|---:|---:|---:|
| Geometri | 12.507 | 1.684 | 31.481 | 0,0178332 |
| Ölçü bağlama | 14.468 | 2.198 | 17.434 | 0,0112628 |
| Toplam | 26.975 | 3.882 | 48.915 | 0,0290960 |

Görünür output, completion token sayısından reasoning çıkarılarak hesaplandı.
Her çağrının completion tavanı reasoning dahil 65.536; zaman aşımı 600 saniye.
Tablo 42.917 → 12.912 UTF-8 bayta indi; bayt miktarı token değildir.
Sağlayıcının iç reasoning metni yayımlanmadı.

## Dosyalar

Ana dizinde tüm STEP/JPEG'ler; bu dizindeki step-jpeg.zip indirme paketidir.
Paketin içinde de tüm STEP/JPEG'ler aynı seviyede, diğer kayıtlar raporlar/ altındadır.
raporlar/input.zip özgün yükleme, overview.png dört örnek paftanın önizlemesidir.
Rapor, eksik J ölçülerini belirtir; bu dosyalar eksiksiz üretim onayı değildir.
