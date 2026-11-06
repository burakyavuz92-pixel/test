# Cıvata2 — canlı API ve yerel devam çalışması

7 ürün, 7 temsilci (tam tablo). Haiku 5.5 / high reasoning ile iki API çağrısı.
Modelin betikleri/referansları elle değiştirilmedi; çizgi kesişimi davranışı değiştirilmedi.

## Sonuç

- 7 STEP ve 7 JPEG üretildi; 7/7 geçerli tek katı ve STEP aktarım kontrolü geçti.
- 7/7 montaj yüzeyi etiketi kontrolü geçti. Etiket kafa altındaki z=-B düzleminde.
- Bağımsız nominal kontrol: toplam boy B+D, dış kafa çapı L, gövde çapı A,
  boyun çapı C, sabit 5 mm boyun, uç pahı ve montaj düzlemi/alanı 7/7 doğru.
- Her paftada 6 ölçü yerleştirildi; toplam 42 ölçü. Geometrik olarak çözülemeyen
  ölçü yok; L etiketi OCR ile doğrulanamadığından kafa çapı ölçüsü 7 paftada da gizli.
- C'nin önünde kullanıcı Ø vermediğinden düz sayı; L'nin Ø işareti model girdisinde
  mevcut fakat OCR kapısından geçemediği için anotasyonu çizilmedi.
- A_METIN metinleri nominal çapın yerine yazdırıldı; geometri nominal A ile yapıldı.
  Thread standardı yorumlanmadı, helisel diş üretilmedi, kullanıcı metni düzeltilmedi.
- Ölçek: 730001/730003/730006/730017 için 2:1;
  730013/730014/730016 için 2,5:1. MALZEME: 8.8 antetten korundu.

## İlk durma ve genel yazılım düzeltmesi

İkinci model yanıtı AXIS_DIR=[0.0,0.0,1.0] sabitini üretti. Önceki sözleşme ve
kontrollü yürütücü modül seviyesinde yalnız tek sayılı sabitleri kabul ettiği için
ölçü kodu yüklenemedi; ilk çalışma measurement-execution aşamasında durdu.
Bu bir şekil üretme hatası veya API reddi değildi.

Yürütücüye sonlu sayılardan oluşan literal liste/tuple vektör ve matris desteği
eklendi. Sayısal olmayan, çalıştırılabilir veya aşırı iç içe sabitler reddedilir;
import/IO kuralları korunur. Sözleşmeler aynı kapsamla uyumlu hale getirildi.
12 yürütücü testi geçti. Orijinal istekler geometry-prompt.txt/measurements-prompt.txt;
yeni sözleşmeler *-updated-contract.txt içindedir.

Aynı iki model yanıtı replay ile API olmadan tekrar çalıştırıldı; geometri, montaj,
ölçü fonksiyonu ve pafta aşamaları tamamlandı. İlk çalışma 164,06 saniye, tekrar
202,87 saniye; toplam çalışma süresi yaklaşık 6 dakika 7 saniye (inceleme/düzeltme
süresi hariç). Ek API çağrısı yok. initial-run-report.json ilk durmayı,
run-report.json API'siz son tekrarın durumunu gösterir. Toplam API kullanımı aşağıdadır.

## L OCR teşhisi

L konumunda 315 derece tarama (L] (~69,46 güven), 300 derece tarama {L} (~54,83 güven)
olarak okumuş. Başka yönde [7] okuması da var. Köşeli parantez içinde güvenilir L
olmadığı için modelin occ-L işareti doğrulanamadı. Ayrıntı ocr-L-observations.json.
L referansı model yanıtında mevcut; nominal çap geometriden de doğrulandı.
OCR ölçüyü yetkilendirmediği için çizilmedi. Etiket elle bağlanmadı ve bu çalışmada
OCR kuralları gevşetilmedi. Kullanıcı [ L ] biçiminde aralık/boyut iyileştirmesini
ayrı bir girdi denemesinde değerlendirebilir; bunun başarı garantisi yoktur.

Son durum sheets-produced-with-unconfirmed-labels, çıkış kodu 2. product-results
completed dosyanın üretildiğini ifade eder; bütün etiketlerin doğrulandığı anlamına
gelmez. Bu çıktılar eksiksiz ölçülendirme onayı değildir.

## Kullanım

| Çağrı | Input | Görünür output | Reasoning | USD |
|---|---:|---:|---:|---:|
| Geometri | 8.896 | 2.302 | 15.364 | 0,0097226 |
| Ölçü bağlama | 10.791 | 2.192 | 12.750 | 0,0085501 |
| Toplam | 19.687 | 4.494 | 28.114 | 0,0182727 |

Completion sınırı çağrı başına reasoning dahil 65.536. Görünür output, completion
sayısından reasoning çıkarılarak hesaplandı. Sağlayıcının iç reasoning metni
paylaşılmadı. Tekrar koşusunun API maliyeti sıfır.

## Geometri yorumunun sınırı

Ölçüsü verilmeyen geçiş açısını model 10 derece, kafa dış uç köşesi yuvarlatmasını
2 mm tamamlamış. Nominal kontroller bu ayrıntıların tasarım niyetine tam uygunluğunu
kanıtlamaz. Bu değerler kullanıcı ölçüsü olarak sunulmuyor.

Ana klasörde 7 STEP ve 7 JPEG birlikte, kayıtlar raporlar/ altında. step-jpeg.zip
aynı düzenle indirme paketidir. overview.png dört örnek paftayı gösterir.
